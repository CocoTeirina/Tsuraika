## Tsuraika

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/downloads/) [![License](https://img.shields.io/github/license/cocoteirina/tsuraika)](https://github.com/cocoteirina/tsuraika/blob/main/LICENSE)

Tsuraika 是一个简单但功能强大的反向代理工具，可以帮助你将内部服务安全地暴露到公网。基于 Python 实现，支持服务器-客户端模式运行，适用于开发测试、内网穿透等场景。

### 特性 / Features

- 🚀 简单易用的命令行界面
- 🔒 支持服务器-客户端模式
- 🔄 自动重连机制
- 📊 详细的日志记录
- 🛡 稳定的连接管理
- ⚡ 高效的数据转发
- 📡 TCP 端口转发
- 🌐 HTTP/HTTPS 协议代理
- 🏷 自定义域名支持
- 🔒 SSL/TLS 加密支持
- 🖥 跨平台支持

### 安装 / Installation

#### 从 PyPI 安装 / Install from PyPI

```bash
$ pip install tsuraika
```

或者, 如果你想用 pipx:

```bash
$ pipx install tsuraika
```

#### 从源码安装 / Build from source

前提条件

- [Poetry](https://python-poetry.org/)
- [Git](https://git-scm.org/)

拉取源代码

```bash
$ git clone https://github.com/CocoTeirina/Tsuraika.git
$ cd Tsuraika
```

安装依赖项

```bash
$ poetry install
```

### 快速开始 / Quick Start

启动服务端

```bash
$ poetry run tsuraika server -p 7000 -d
```

启动客户端

```bash
$ poetry run tsuraika client -c /path/to/config.json -d
```

### 命令行参数 / CLI Arguments

#### 服务端选项

```bash
$ poetry run tsuraika server [options]
```

| 选项            | 说明                      | 默认值 |
| --------------- | ------------------------- | ------ |
| `--port`, `-p`  | 服务端端口                | `7000` |
| `--debug`, `-d` | 调试模式 (详细控制台输出) | 禁用   |

#### 客户端选项

```bash
$ poetry run tsuraika client [options]
```

| 选项                   | 说明                        | 默认值      |
| ---------------------- | --------------------------- | ----------- |
| `--config`, `-c`       | 配置文件路径                | 空          |
| `--server`, `-s`       | 服务端地址                  | `127.0.0.1` |
| `--server-port`, `-sp` | 服务端端口                  | `7000`      |
| `--local`, `-l`        | 本地服务地址                | `127.0.0.1` |
| `--local-port`, `-lp`  | 本地服务端口                | `8080`      |
| `--remote-port`, `-rp` | 服务端暴露端口 (`0 = 随机`) | `0`         |
| `--name`, `-n`         | 客户端名称                  | 空          |
| `--debug`, `-d`        | 调试模式 (详细控制台输出)   | 禁用        |

### 更新日志 / Update Logs

#### v1.0.0 (2024-11-23)

- 之前的版本存在可能导致 Tsuraika 无法使用的错误, 采用 MsgPack 重构了 Tsuraika

<hr />

Made with ♥ by [CocoTeirina](https://github.com/CocoTeirina)
