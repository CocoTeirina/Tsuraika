import logging
from enum import Enum
from dataclasses import dataclass

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("tsuraika")


class MessageType(Enum):
    INITIAL_REQUEST = "initial_request"
    INITIAL_RESPONSE = "initial_response"
    DATA = "data"


@dataclass
class ClientConfig:
    server_addr: str
    server_port: int
    local_addr: str
    local_port: int
    proxy_name: str
    remote_port: int


def validate_message(message: dict) -> bool:
    """Validate message format"""
    try:
        if not isinstance(message, dict):
            return False

        type_key = b"type" if isinstance(next(iter(message.keys())), bytes) else "type"
        data_key = b"data" if isinstance(next(iter(message.keys())), bytes) else "data"

        if type_key not in message or data_key not in message:
            return False

        if not isinstance(message[data_key], dict):
            return False

        msg_type = message[type_key]
        if isinstance(msg_type, bytes):
            msg_type = msg_type.decode("utf-8")

        data = message[data_key]

        if msg_type == MessageType.INITIAL_REQUEST.value:
            required_fields = (
                {b"proxy_type", b"remote_port", b"proxy_name"}
                if isinstance(next(iter(data.keys())), bytes)
                else {"proxy_type", "remote_port", "proxy_name"}
            )
            return all(field in data for field in required_fields)

        elif msg_type == MessageType.INITIAL_RESPONSE.value:
            required_fields = (
                {b"proxy_name", b"remote_port"}
                if isinstance(next(iter(data.keys())), bytes)
                else {"proxy_name", "remote_port"}
            )
            return all(field in data for field in required_fields)

        elif msg_type == MessageType.DATA.value:
            required_fields = (
                {b"proxy_name", b"data"}
                if isinstance(next(iter(data.keys())), bytes)
                else {"proxy_name", "data"}
            )
            return all(field in data for field in required_fields)

        return False
    except Exception as e:
        logger.error(f"Validation error: {e}")
        return False
