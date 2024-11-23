import sys
import logging
import asyncio
from typing import Optional

import typer
from rich import print
from rich.console import Console
from importlib.metadata import version

from .common import logger, ClientConfig
from .server import ProxyServer
from .client import ProxyClient, load_config

app = typer.Typer(
    name="Tsuraika",
    help="The Next Generation of Fast Reverse Proxy",
    add_completion=False,
)
console = Console()


def version_callback(value: bool):
    if value:
        try:
            current_version = version("tsuraika")
            print(
                f"[bold green]Tsuraika[/bold green] version [bold]{current_version}[/bold]"
            )
        except Exception:
            print("[bold green]Tsuraika[/bold green] version [bold]unknown[/bold]")
        raise typer.Exit()


@app.callback()
def common(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version information",
        callback=version_callback,
        is_eager=True,
    ),
):
    """Tsuraika - Simple and efficient reverse proxy tool"""
    pass


@app.command()
def server(
    port: int = typer.Option(7000, "--port", "-p", help="Server port (default: 7000)"),
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug logging"),
):
    """Start the server"""
    if debug:
        logger.setLevel(logging.DEBUG)

    try:
        with console.status("[bold green]Starting server..."):
            server_instance = ProxyServer(port)
            console.print(f"[green]Server started on port {port}[/green]")

        asyncio.run(server_instance.start())
    except KeyboardInterrupt:
        console.print("\n[yellow]Server stopped[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@app.command()
def client(
    config: Optional[str] = typer.Option(
        None, "--config", "-c", help="Path to client configuration file (optional)"
    ),
    server_addr: str = typer.Option(
        "127.0.0.1", "--server", "-s", help="Server address"
    ),
    server_port: int = typer.Option(7000, "--server-port", "-sp", help="Server port"),
    local_addr: str = typer.Option(
        "127.0.0.1", "--local", "-l", help="Local service address"
    ),
    local_port: int = typer.Option(
        8080, "--local-port", "-lp", help="Local service port"
    ),
    remote_port: int = typer.Option(
        0, "--remote-port", "-rp", help="Remote service port (0 = random)"
    ),
    proxy_name: str = typer.Option(None, "--name", "-n", help="Proxy name"),
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug logging"),
):
    """Start the client"""
    if debug:
        logger.setLevel(logging.DEBUG)

    try:
        with console.status("[bold green]Starting client..."):
            if config:
                try:
                    client_config = load_config(config)
                except FileNotFoundError:
                    console.print(
                        f"[red]Error: Configuration file not found {config}[/red]"
                    )
                    sys.exit(1)
            else:
                if not proxy_name:
                    proxy_name = f"proxy_{local_port}"
                client_config = ClientConfig(
                    server_addr=server_addr,
                    server_port=server_port,
                    local_addr=local_addr,
                    local_port=local_port,
                    proxy_name=proxy_name,
                    remote_port=remote_port,
                )

            client_instance = ProxyClient(client_config)
            console.print("[green]Client started[/green]")
            console.print(
                f"[blue]Proxy configuration:[/blue]\n"
                f"  Local service: {client_config.local_addr}:{client_config.local_port}\n"
                f"  Server: {client_config.server_addr}:{client_config.server_port}\n"
                f"  Proxy name: {client_config.proxy_name}"
            )

        asyncio.run(client_instance.start())
    except KeyboardInterrupt:
        console.print("\n[yellow]Client stopped[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


def main():
    app()


if __name__ == "__main__":
    main()
