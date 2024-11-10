# frp/core.py

import socket
import threading
import json
import time
from dataclasses import dataclass
from typing import Dict, Optional, Union
import logging
import sys
import ssl
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import http.client

@dataclass
class ProxyConfig:
    local_addr: str
    local_port: int
    remote_addr: str
    remote_port: Optional[int] = None
    custom_domain: Optional[str] = None
    protocol: str = "tcp"  # "tcp", "http", or "https"

class HTTPProxyHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, proxy_config: ProxyConfig, **kwargs):
        self.proxy_config = proxy_config
        super().__init__(*args, **kwargs)
        
    def do_METHOD(self):
        try:
            # Create connection to local service
            if self.proxy_config.protocol == "https":
                conn = http.client.HTTPSConnection(
                    self.proxy_config.local_addr,
                    self.proxy_config.local_port
                )
            else:
                conn = http.client.HTTPConnection(
                    self.proxy_config.local_addr,
                    self.proxy_config.local_port
                )

            # Read request body if present
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else None

            # Forward the request
            conn.request(
                method=self.command,
                url=self.path,
                body=body,
                headers=dict(self.headers)
            )

            # Get response from local service
            response = conn.getresponse()
            
            # Send response back to client
            self.send_response(response.status)
            for header, value in response.getheaders():
                if header.lower() not in ('server', 'date', 'transfer-encoding'):
                    self.send_header(header, value)
            self.end_headers()
            
            # Forward response body
            self.wfile.write(response.read())
            
        except Exception as e:
            logging.error(f"Proxy error: {e}")
            self.send_error(502, f"Proxy Error: {str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()

    def do_GET(self): self.do_METHOD()
    def do_POST(self): self.do_METHOD()
    def do_PUT(self): self.do_METHOD()
    def do_DELETE(self): self.do_METHOD()
    def do_HEAD(self): self.do_METHOD()
    def do_OPTIONS(self): self.do_METHOD()
    def do_PATCH(self): self.do_METHOD()

class FRPServer:
    def __init__(self, bind_port: int, ssl_cert: Optional[str] = None, ssl_key: Optional[str] = None):
        self.bind_port = bind_port
        self.ssl_cert = ssl_cert
        self.ssl_key = ssl_key
        self.proxy_mappings: Dict[Union[int, str], ProxyConfig] = {}
        self.control_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.control_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.running = True
        self.proxy_listeners: Dict[Union[int, str], Union[socket.socket, HTTPServer]] = {}
        self.domain_to_config: Dict[str, ProxyConfig] = {}

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
        for key, listener in self.proxy_listeners.items():
            try:
                if isinstance(listener, HTTPServer):
                    listener.shutdown()
                listener.close()
                logging.info(f"Closed proxy listener for {key}")
            except:
                pass
        if hasattr(self, 'control_sock'):
            self.control_sock.close()

    def start_tcp_proxy(self, config: ProxyConfig):
        try:
            proxy_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            proxy_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            proxy_sock.bind(('0.0.0.0', config.remote_port))
            proxy_sock.listen(5)
            
            self.proxy_listeners[config.remote_port] = proxy_sock
            logging.info(f"Started TCP proxy listener on port {config.remote_port}")
            
            while self.running and config.remote_port in self.proxy_mappings:
                try:
                    client_sock, addr = proxy_sock.accept()
                    logging.info(f"New TCP proxy connection from {addr} on port {config.remote_port}")
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
            logging.error(f"Error starting TCP proxy listener on port {config.remote_port}: {e}")
        finally:
            if config.remote_port in self.proxy_listeners:
                self.proxy_listeners[config.remote_port].close()
                del self.proxy_listeners[config.remote_port]

    def start_http_proxy(self, config: ProxyConfig):
        try:
            handler = type(
                'CustomHTTPProxyHandler',
                (HTTPProxyHandler,),
                {'proxy_config': config}
            )
            
            server = HTTPServer(('0.0.0.0', config.remote_port or 80), handler)
            
            if config.protocol == "https" and self.ssl_cert and self.ssl_key:
                server.socket = ssl.wrap_socket(
                    server.socket,
                    certfile=self.ssl_cert,
                    keyfile=self.ssl_key,
                    server_side=True
                )
            
            if config.custom_domain:
                self.domain_to_config[config.custom_domain] = config
                logging.info(f"Registered domain {config.custom_domain} -> {config.local_addr}:{config.local_port}")
            
            self.proxy_listeners[config.remote_port or config.custom_domain] = server
            server.serve_forever()
            
        except Exception as e:
            logging.error(f"Error starting HTTP proxy: {e}")

    def start_proxy_listener(self, config: ProxyConfig):
        if config.protocol in ("http", "https"):
            self.start_http_proxy(config)
        else:
            self.start_tcp_proxy(config)

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
            
            # 检查端口或域名是否已被使用
            if (config.remote_port and config.remote_port in self.proxy_mappings) or \
               (config.custom_domain and config.custom_domain in self.domain_to_config):
                logging.warning(f"Port or domain already in use")
                client_sock.send("port_or_domain_in_use".encode())
                return
            
            key = config.remote_port or config.custom_domain
            self.proxy_mappings[key] = config
            client_sock.send("success".encode())
            
            proxy_thread = threading.Thread(
                target=self.start_proxy_listener,
                args=(config,)
            )
            proxy_thread.daemon = True
            proxy_thread.start()
            
            protocol_info = f"{config.protocol}://" if config.protocol in ("http", "https") else ""
            logging.info(f"New proxy mapping: {protocol_info}{config.custom_domain or config.remote_port} -> {config.local_addr}:{config.local_port}")
            
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
            if config:
                key = config.remote_port or config.custom_domain
                if key in self.proxy_mappings:
                    del self.proxy_mappings[key]
                if config.custom_domain in self.domain_to_config:
                    del self.domain_to_config[config.custom_domain]
                logging.info(f"Removed proxy mapping for {key}")

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
                    "remote_port": config.remote_port,
                    "custom_domain": config.custom_domain,
                    "protocol": config.protocol
                })
                self.control_sock.send(config_data.encode())
                
                response = self.control_sock.recv(1024).decode()
                if response == "port_or_domain_in_use":
                    logging.error(f"Remote port or domain is already in use")
                    break
                elif response != "success":
                    logging.error(f"Unexpected server response: {response}")
                    break

                logging.info(f"Successfully connected to FRP server")
                protocol_info = f"{config.protocol}://" if config.protocol in ("http", "https") else ""
                logging.info(f"Forwarding {protocol_info}{config.custom_domain or f'{config.remote_addr}:{config.remote_port}'} -> {config.local_addr}:{config.local_port}")
                
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
            except Exception as e:
                logging.error(f"Unexpected error: {e}")
                break
            finally:
                if hasattr(self, 'control_sock'):
                    self.control_sock.close()
