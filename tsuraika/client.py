import asyncio
import msgpack
import json
import os
from .common import ClientConfig, MessageType, validate_message, logger


class ProxyClient:
    def __init__(self, config: ClientConfig):
        self.config = config
        self.local_connections = {}
        self.server_writer = None

    def decode_if_bytes(self, value):
        if isinstance(value, bytes):
            return value.decode("utf-8")
        return value

    def get_message_field(self, message: dict, field: str):
        return message.get(field.encode()) or message.get(field)

    def get_data_field(self, data: dict, field: str):
        return data.get(field.encode()) or data.get(field)

    async def forward_local_to_server(
        self, reader: asyncio.StreamReader, connection_id: str
    ):
        try:
            while True:
                data = await reader.read(8192)
                if not data:
                    break

                if self.server_writer:
                    message = {
                        "type": MessageType.DATA.value,
                        "data": {
                            "proxy_name": self.config.proxy_name,
                            "data": data,
                            "connection_id": connection_id,
                        },
                    }
                    logger.debug(f"Forwarding local data to server: {message}")
                    packed_data = msgpack.packb(message)
                    self.server_writer.write(packed_data)
                    await self.server_writer.drain()

        except Exception as e:
            logger.error(f"Error forwarding local data to server: {e}")
        finally:
            if connection_id in self.local_connections:
                reader, writer = self.local_connections[connection_id]
                writer.close()
                await writer.wait_closed()
                del self.local_connections[connection_id]

    async def create_local_connection(
        self, connection_id: str
    ) -> tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        try:
            reader, writer = await asyncio.open_connection(
                self.config.local_addr, self.config.local_port
            )
            self.local_connections[connection_id] = (reader, writer)
            logger.info(
                f"Created new local connection {connection_id} to {self.config.local_addr}:{self.config.local_port}"
            )

            asyncio.create_task(self.forward_local_to_server(reader, connection_id))

            return reader, writer
        except Exception as e:
            logger.error(f"Failed to create local connection: {e}")
            raise

    async def handle_server_data(self, reader: asyncio.StreamReader):
        try:
            while True:
                packed_data = await reader.read(8192)
                if not packed_data:
                    break

                try:
                    message = msgpack.unpackb(packed_data)
                    logger.debug(f"Received message from server: {message}")

                    if not validate_message(message):
                        logger.error("Invalid message format received from server")
                        continue

                    msg_type = self.decode_if_bytes(
                        self.get_message_field(message, "type")
                    )
                    data = self.get_message_field(message, "data")

                    if msg_type == MessageType.INITIAL_RESPONSE.value:
                        remote_port = self.get_data_field(data, "remote_port")
                        proxy_name = self.decode_if_bytes(
                            self.get_data_field(data, "proxy_name")
                        )
                        logger.info(
                            f"Proxy established on remote port: {remote_port} for {proxy_name}"
                        )

                    elif msg_type == MessageType.DATA.value:
                        proxy_name = self.decode_if_bytes(
                            self.get_data_field(data, "proxy_name")
                        )
                        if proxy_name == self.config.proxy_name:
                            binary_data = self.get_data_field(data, "data")
                            connection_id = self.decode_if_bytes(
                                self.get_data_field(data, "connection_id")
                            )

                            if connection_id not in self.local_connections:
                                _, writer = await self.create_local_connection(
                                    connection_id
                                )
                            else:
                                _, writer = self.local_connections[connection_id]

                            writer.write(binary_data)
                            await writer.drain()
                            logger.debug(
                                f"Forwarded data to local service for connection {connection_id}"
                            )

                except msgpack.UnpackException as e:
                    logger.error(f"Failed to unpack message: {e}")
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    logger.exception(e)

        except Exception as e:
            logger.error(f"Server connection error: {e}")
            logger.exception(e)
        finally:
            for connection_id, (_, writer) in self.local_connections.items():
                writer.close()
                await writer.wait_closed()
            self.local_connections.clear()

    async def start(self):
        try:
            reader, writer = await asyncio.open_connection(
                self.config.server_addr, self.config.server_port
            )
            self.server_writer = writer
            logger.info(
                f"Connected to server at {self.config.server_addr}:{self.config.server_port}"
            )

            initial_request = {
                "type": MessageType.INITIAL_REQUEST.value,
                "data": {
                    "proxy_type": "tcp",
                    "remote_port": self.config.remote_port,
                    "proxy_name": self.config.proxy_name,
                },
            }

            writer.write(msgpack.packb(initial_request))
            await writer.drain()

            await self.handle_server_data(reader)

        except Exception as e:
            logger.error(f"Failed to connect to server: {e}")
            logger.exception(e)
        finally:
            for connection_id, (_, writer) in self.local_connections.items():
                writer.close()
                await writer.wait_closed()
            self.local_connections.clear()

            if self.server_writer:
                self.server_writer.close()
                await self.server_writer.wait_closed()


def load_config(config_path: str) -> ClientConfig:
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r") as f:
        config_data = json.load(f)

    return ClientConfig(
        server_addr=config_data.get("server_addr", "127.0.0.1"),
        server_port=config_data.get("server_port", 7000),
        local_addr=config_data.get("local_addr", "127.0.0.1"),
        local_port=config_data.get("local_port", 80),
        proxy_name=config_data.get("proxy_name", "test_proxy"),
        remote_port=config_data.get("remote_port", 8080),
    )
