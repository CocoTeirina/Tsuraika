# Tsuraika

[简体中文](https://github.com/cocoteirina/tsuraika/blob/main/docs/README.md) | [English](https://github.com/cocoteirina/tsuraika/blob/main/docs/README_en.md) | [日本語](https://github.com/cocoteirina/tsuraika/blob/main/docs/README_ja.md)

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/downloads/) [![PyPI](https://img.shields.io/pypi/v/tsuraika)](https://pypi.org/project/tsuraika/) [![License](https://img.shields.io/github/license/cocoteirina/tsuraika)](https://github.com/cocoteirina/tsuraika/blob/main/LICENSE)

Tsuraika is a simple yet powerful reverse proxy tool that helps you securely expose internal services to the public network. It is implemented in Python and supports the server-client mode, suitable for development testing, intranet penetration, and other scenarios.

## Features

- 🚀 Easy-to-use command-line interface
- 🔒 Supports server-client mode
- 🔄 Automatic reconnection mechanism
- 📊 Detailed log records
- 🛡 Stable connection management
- ⚡ Efficient data forwarding
- 📡 TCP port forwarding
- 🌐 HTTP/HTTPS protocol proxy
- 🏷 Custom domain support
- 🔒 SSL/TLS encryption support
- 🖥 Cross-platform support

## Installation

### Install from PyPI (Recommended)

```bash
pip install tsuraika
```

### Install from Source Code

```bash
git clone https://github.com/cocoteirina/tsuraika.git
cd tsuraika
pip install.
```

## Quick Start

### Start the Server

```bash
# Basic server (port 7000)
tsuraika server -p 7000

# Server with SSL enabled
tsuraika server -p 7000 --ssl-cert cert.pem --ssl-key key.pem
```

### Start the Client

#### TCP Port Forwarding

```bash
# Forward local port 8080 to remote port 80
tsuraika client \
    --local-addr localhost \
    --local-port 8080 \
    --remote-addr example.com \
    --remote-port 80 \
    --server-port 7000
```

#### HTTP Proxy with Custom Domain

```bash
# Expose local web service with custom domain
tsuraika client \
    --local-addr localhost \
    --local-port 8080 \
    --remote-addr example.com \
    --custom-domain myapp.example.com \
    --protocol http \
    --server-port 7000
```

## Command Line Arguments

### Server Options

```bash
tsuraika server [options]
```

| Option | Description | Default Value |
|--------|-------------|---------|
| `--port`, `-p` | Server control port | 7000 |
| `--ssl-cert` | SSL certificate file | None |
| `--ssl-key` | SSL key file | None |

### Client Options

```bash
tsuraika client [options]
```

| Option | Description | Required |
|--------|-------------|----------|
| `--local-addr`, `-l` | Local service address | Yes |
| `--local-port`, `-p` | Local service port | Yes |
| `--remote-addr`, `-r` | Remote server address | Yes |
| `--remote-port`, `-P` | Remote exposed port | No* |
| `--custom-domain`, `-d` | Custom domain for HTTP/HTTPS proxy | No* |
| `--protocol` | Protocol type (tcp/http/https) | No (Default: tcp) |
| `--server-port`, `-s` | Server control port | No (Default: 7000) |

*For HTTP/HTTPS protocol, either `remote-port` or `custom-domain` must be specified.

## Use Cases

1. **Development Testing**
   - Quickly expose the local development environment to testers.
   - Easily demonstrate development results to clients.

2. **Intranet Penetration**
   - Securely expose intranet services to the public network.
   - Remotely access intranet resources.

3. **Temporary Service Sharing**
   - Share a locally running website or service.
   - Collaborative development and debugging.

## Examples of Use

### Local Development Server

Expose the local development server to the public network:

```bash
# Server
tsuraika server -p 7000

# Client
tsuraika client \
    --local-addr localhost \
    --local-port 3000 \
    --remote-addr your-server.com \
    --remote-port 8080 \
    --protocol http
```

### HTTPS Secure Service

Set up an HTTPS proxy with a custom domain:

```bash
# Server (configure SSL certificate)
tsuraika server \
    -p 7000 \
    --ssl-cert /path/to/cert.pem \
    --ssl-key /path/to/key.pem

# Client
tsuraika client \
    --local-addr localhost \
    --local-port 8080 \
    --remote-addr your-server.com \
    --custom-domain secure.example.com \
    --protocol https
```

### Database Port Forwarding

Securely forward the local database port:

```bash
tsuraika client \
    --local-addr localhost \
    --local-port 5432 \
    --remote-addr your-server.com \
    --remote-port 54320
```

## Frequently Asked Questions

1. **What if the connection fails?**
   - Check if the server is running normally.
   - Confirm the firewall settings.
   - Verify if the port is occupied.

2. **How to choose a protocol?**
   - TCP: Suitable for general port forwarding.
   - HTTP: Suitable for web services and supports domains.
   - HTTPS: Requires an SSL certificate and provides encryption protection.

3. **Automatic Reconnection Mechanism**
   - Automatically retry after disconnection.
   - Uses an exponential backoff strategy.
   - Retries up to 5 times.

## Development Plan

- [x] Add TLS encryption support.
- [ ] Implement configuration file support.
- [ ] Add a web management interface.
- [ ] Support multiplexing.
- [ ] Add traffic statistics function.

## Changelog

### v0.1.3 (2024-11-10)
- HTTP / HTTPS support added.
- Custom domain support added.

### v0.1.2 (2024-11-09)
- Fixed the import issue of the entry function.

### v0.1.1 (2024-11-09)
- Replaced argparse with typer.

### v0.1.0 (2024-11-09)
- Initial version released.
- Basic reverse proxy function implemented.
- Command-line interface added.
- Server-client mode supported.

---
Made with ❤️ by [CocoTeirina](https://github.com/CocoTeirina) 