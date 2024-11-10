# frp/cli.py

import typer
import logging
from typing import Optional
from .core import FRPServer, FRPClient, ProxyConfig

app = typer.Typer()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@app.command()
def server(
    port: int = typer.Option(7000, "--port", "-p", help="Server control port"),
    ssl_cert: Optional[str] = typer.Option(None, "--ssl-cert", help="SSL certificate file for HTTPS"),
    ssl_key: Optional[str] = typer.Option(None, "--ssl-key", help="SSL key file for HTTPS")
):
    """
    Start FRP server on specified port
    """
    try:
        server = FRPServer(port, ssl_cert, ssl_key)
        server.start()
    except KeyboardInterrupt:
        logging.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        raise typer.Exit(code=1)

@app.command()
def client(
    local_addr: str = typer.Option(..., "--local-addr", "-l", help="Local address to forward to"),
    local_port: int = typer.Option(..., "--local-port", "-p", help="Local port to forward to"),
    remote_addr: str = typer.Option(..., "--remote-addr", "-r", help="Remote server address"),
    remote_port: Optional[int] = typer.Option(None, "--remote-port", "-P", help="Remote port to expose"),
    custom_domain: Optional[str] = typer.Option(None, "--custom-domain", "-d", help="Custom domain for HTTP/HTTPS proxy"),
    protocol: str = typer.Option("tcp", "--protocol", help="Protocol: tcp, http, or https"),
    server_port: int = typer.Option(7000, "--server-port", "-s", help="Server control port")
):
    """
    Start FRP client and establish connection to server
    """
    try:
        if protocol in ("http", "https") and not (remote_port or custom_domain):
            raise typer.BadParameter("Either remote-port or custom-domain must be specified for HTTP/HTTPS proxy")
            
        config = ProxyConfig(
            local_addr=local_addr,
            local_port=local_port,
            remote_addr=remote_addr,
            remote_port=remote_port,
            custom_domain=custom_domain,
            protocol=protocol
        )
        
        client = FRPClient(remote_addr, server_port)
        client.start(config)
    except KeyboardInterrupt:
        logging.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()