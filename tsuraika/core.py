# frp/core.py

import socket
import threading
import json
import time
from dataclasses import dataclass
from typing import Dict, Optional
import logging
import sys

@dataclass
class ProxyConfig:
    local_addr: str
    local_port: int
    remote_addr: str
    remote_port: int

class FRPServer:
    def __init__(self, bind_port: int):
        self.bind_port = bind_port
        self.proxy_mappings: Dict[int, ProxyConfig] = {}
        self.control_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.control_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.running = True
        self.proxy_listeners: Dict[int, socket.socket] = {}

    def start(self):
        try:
            self.control_sock.bind(('0.0.0.0', self.bind_port))
            self.control_sock.listen(5)
            logging.info(f"FRP Server started on port {self.bind_port}")
            logging.info(f"Waiting for client connections...")

            while self.running:
                try:
                    client_sock, addr = self.control_sock.accept()
                    logging.info(f"New control connection from {addr}")
                    threading.Thread(target=self.handle_client_control, args=(client_sock, addr)).start()
                except Exception as e:
                    logging.error(f"Error accepting client connection: {e}")
                    time.sleep(1)
        except Exception as e:
            logging.error(f"Server startup error: {e}")
            sys.exit(1)
        finally:
            self.cleanup()

    def cleanup(self):
        logging.info("Server shutting down...")
        self.running = False
        for port, sock in self.proxy_listeners.items():
            try:
                sock.close()
                logging.info(f"Closed proxy listener on port {port}")
            except:
                pass
        if hasattr(self, 'control_sock'):
            self.control_sock.close()

    def start_proxy_listener(self, config: ProxyConfig):
        try:
            proxy_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            proxy_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            proxy_sock.bind(('0.0.0.0', config.remote_port))
            proxy_sock.listen(5)
            
            self.proxy_listeners[config.remote_port] = proxy_sock
            logging.info(f"Started proxy listener on port {config.remote_port}")
            
            while self.running and config.remote_port in self.proxy_mappings:
                try:
                    client_sock, addr = proxy_sock.accept()
                    logging.info(f"New proxy connection from {addr} on port {config.remote_port}")
                    threading.Thread(
                        target=self.handle_proxy_connection,
                        args=(client_sock, config)
                    ).start()
                except socket.error:
                    if not self.running or config.remote_port not in self.proxy_mappings:
                        break
                    logging.error(f"Error accepting proxy connection on port {config.remote_port}")
                    time.sleep(1)
                
        except Exception as e:
            logging.error(f"Error starting proxy listener on port {config.remote_port}: {e}")
        finally:
            if config.remote_port in self.proxy_listeners:
                self.proxy_listeners[config.remote_port].close()
                del self.proxy_listeners[config.remote_port]

    def handle_proxy_connection(self, client_sock: socket.socket, config: ProxyConfig):
        target_sock = None
        try:
            target_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target_sock.connect((config.local_addr, config.local_port))
            
            forward_thread = threading.Thread(
                target=self.forward_data,
                args=(client_sock, target_sock, "client -> target")
            )
            backward_thread = threading.Thread(
                target=self.forward_data,
                args=(target_sock, client_sock, "target -> client")
            )
            
            forward_thread.start()
            backward_thread.start()
            
            forward_thread.join()
            backward_thread.join()
            
        except Exception as e:
            logging.error(f"Proxy connection error: {e}")
        finally:
            if target_sock:
                target_sock.close()
            if not client_sock._closed:
                client_sock.close()

    def forward_data(self, source: socket.socket, destination: socket.socket, direction: str):
        try:
            while True:
                data = source.recv(4096)
                if not data:
                    break
                destination.send(data)
        except Exception as e:
            logging.debug(f"Data forwarding error ({direction}): {e}")
        finally:
            source.close()
            destination.close()

    def handle_client_control(self, client_sock: socket.socket, addr):
        config = None
        try:
            client_sock.settimeout(30)
            
            data = client_sock.recv(1024).decode()
            if not data:
                logging.warning(f"Empty configuration received from {addr}")
                return
                
            config = ProxyConfig(**json.loads(data))
            
            if config.remote_port in self.proxy_mappings:
                logging.warning(f"Port {config.remote_port} is already in use")
                client_sock.send("port_in_use".encode())
                return
            
            self.proxy_mappings[config.remote_port] = config
            client_sock.send("success".encode())
            
            proxy_thread = threading.Thread(
                target=self.start_proxy_listener,
                args=(config,)
            )
            proxy_thread.daemon = True
            proxy_thread.start()
            
            logging.info(f"New proxy mapping: {config.remote_port} -> {config.local_addr}:{config.local_port}")
            
            while self.running:
                try:
                    if not client_sock.recv(1024):
                        break
                    client_sock.send(b'pong')
                except socket.timeout:
                    logging.warning(f"Control connection timeout from {addr}")
                    break
                except Exception as e:
                    logging.error(f"Control connection error: {e}")
                    break
                    
        except json.JSONDecodeError:
            logging.error(f"Invalid configuration format from {addr}")
        except Exception as e:
            logging.error(f"Control connection error: {e}")
        finally:
            client_sock.close()
            if config and config.remote_port in self.proxy_mappings:
                del self.proxy_mappings[config.remote_port]
                logging.info(f"Removed proxy mapping for port {config.remote_port}")

class FRPClient:
    def __init__(self, server_addr: str, server_port: int):
        self.server_addr = server_addr
        self.server_port = server_port
        self.running = True
        self.retry_count = 0
        self.max_retries = 5
        self.retry_delay = 5

    def connect(self) -> Optional[socket.socket]:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        try:
            logging.info(f"Connecting to FRP server at {self.server_addr}:{self.server_port}...")
            sock.connect((self.server_addr, self.server_port))
            self.retry_count = 0
            self.retry_delay = 5
            return sock
        except ConnectionRefusedError:
            logging.error(f"Connection refused - Please check if the server is running at {self.server_addr}:{self.server_port}")
        except socket.timeout:
            logging.error("Connection timeout - Server is not responding")
        except socket.gaierror:
            logging.error(f"Invalid server address: {self.server_addr}")
        except Exception as e:
            logging.error(f"Connection error: {e}")
        
        sock.close()
        return None

    def start(self, config: ProxyConfig):
        while self.running and self.retry_count < self.max_retries:
            try:
                self.control_sock = self.connect()
                if not self.control_sock:
                    raise ConnectionError("Failed to establish connection")

                config_data = json.dumps({
                    "local_addr": config.local_addr,
                    "local_port": config.local_port,
                    "remote_addr": config.remote_addr,
                    "remote_port": config.remote_port
                })
                self.control_sock.send(config_data.encode())
                
                response = self.control_sock.recv(1024).decode()
                if response == "port_in_use":
                    logging.error(f"Remote port {config.remote_port} is already in use")
                    break
                elif response != "success":
                    logging.error(f"Unexpected server response: {response}")
                    break

                logging.info(f"Successfully connected to FRP server")
                logging.info(f"Forwarding {config.remote_addr}:{config.remote_port} -> {config.local_addr}:{config.local_port}")
                
                while self.running:
                    self.control_sock.send(b'ping')
                    response = self.control_sock.recv(1024)
                    if not response:
                        raise ConnectionError("Server disconnected")
                    time.sleep(30)

            except (ConnectionError, socket.error) as e:
                self.retry_count += 1
                if self.retry_count < self.max_retries:
                    logging.error(f"Connection lost: {e}")
                    logging.info(f"Retrying in {self.retry_delay} seconds... (Attempt {self.retry_count}/{self.max_retries})")
                    time.sleep(self.retry_delay)
                    self.retry_delay = min(self.retry_delay * 2, 60)
                else:
                    logging.error("Max retry attempts reached. Exiting...")
                    break
            except KeyboardInterrupt:
                logging.info("Received keyboard interrupt, shutting down...")
                break
            except Exception as e:
                logging.error(f"Unexpected error: {e}")
                break
            finally:
                if hasattr(self, 'control_sock'):
                    self.control_sock.close()