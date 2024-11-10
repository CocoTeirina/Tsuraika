# Tsuraika

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/downloads/) [![PyPI](https://img.shields.io/pypi/v/tsuraika)](https://pypi.org/project/tsuraika/) [![License](https://img.shields.io/github/license/cocoteirina/tsuraika)](https://github.com/cocoteirina/tsuraika/blob/main/LICENSE)

Tsuraika 是一个简单但功能强大的反向代理工具，可以帮助你将内部服务安全地暴露到公网。基于 Python 实现，支持服务器-客户端模式运行，适用于开发测试、内网穿透等场景。

## 特性

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


## 安装

### 从 PyPI 安装（推荐）

```bash
pip install tsuraika
```

### 从源码安装

```bash
git clone https://github.com/cocoteirina/tsuraika.git
cd tsuraika
pip install .
```

## 快速开始

### 启动服务器

```bash
# 基础服务端（端口 7000）
tsuraika server -p 7000

# 启用 SSL 的服务端
tsuraika server -p 7000 --ssl-cert cert.pem --ssl-key key.pem
```

### 启动客户端


#### TCP 端口转发
```bash
# 将本地 8080 端口转发到远程 80 端口
tsuraika client \
    --local-addr localhost \
    --local-port 8080 \
    --remote-addr example.com \
    --remote-port 80 \
    --server-port 7000
```

#### 使用自定义域名的 HTTP 代理

```bash
# 使用自定义域名暴露本地 Web 服务
tsuraika client \
    --local-addr localhost \
    --local-port 8080 \
    --remote-addr example.com \
    --custom-domain myapp.example.com \
    --protocol http \
    --server-port 7000
```

## 命令行参数

### 服务端选项

```bash
tsuraika server [options]
```

| 选项 | 说明 | 默认值 |
|--------|-------------|---------|
| `--port`, `-p` | 服务端控制端口 | 7000 |
| `--ssl-cert` | SSL 证书文件 | 无 |
| `--ssl-key` | SSL 密钥文件 | 无 |

### 客户端选项

```bash
tsuraika client [options]
```

| 选项 | 说明 | 是否必需 |
|--------|-------------|----------|
| `--local-addr`, `-l` | 本地服务地址 | 是 |
| `--local-port`, `-p` | 本地服务端口 | 是 |
| `--remote-addr`, `-r` | 远程服务器地址 | 是 |
| `--remote-port`, `-P` | 远程暴露端口 | 否* |
| `--custom-domain`, `-d` | HTTP/HTTPS 代理的自定义域名 | 否* |
| `--protocol` | 协议类型 (tcp/http/https) | 否 (默认: tcp) |
| `--server-port`, `-s` | 服务端控制端口 | 否 (默认: 7000) |

\* HTTP/HTTPS 协议必须指定 `remote-port` 或 `custom-domain` 其中之一

## 使用场景

1. **开发测试**
   - 快速将本地开发环境暴露给测试人员
   - 方便地展示开发成果给客户

2. **内网穿透**
   - 安全地将内网服务暴露到公网
   - 远程访问内网资源

3. **临时服务共享**
   - 分享本地运行的网站或服务
   - 协作开发和调试

## 使用示例

### 本地开发服务器

将本地开发服务器暴露到公网：

```bash
# 服务端
tsuraika server -p 7000

# 客户端
tsuraika client \
    --local-addr localhost \
    --local-port 3000 \
    --remote-addr your-server.com \
    --remote-port 8080 \
    --protocol http
```

### HTTPS 安全服务

设置带有自定义域名的 HTTPS 代理：

```bash
# 服务端（配置 SSL 证书）
tsuraika server \
    -p 7000 \
    --ssl-cert /path/to/cert.pem \
    --ssl-key /path/to/key.pem

# 客户端
tsuraika client \
    --local-addr localhost \
    --local-port 8080 \
    --remote-addr your-server.com \
    --custom-domain secure.example.com \
    --protocol https
```

### 数据库端口转发

安全地转发本地数据库端口：

```bash
frp client \
    --local-addr localhost \
    --local-port 5432 \
    --remote-addr your-server.com \
    --remote-port 54320
```

## 常见问题

1. **连接失败怎么办？**
   - 检查服务端是否正常运行
   - 确认防火墙设置
   - 验证端口是否被占用

2. **如何选择协议？**
   - TCP：适用于一般的端口转发
   - HTTP：适用于 Web 服务，支持域名
   - HTTPS：需要 SSL 证书，提供加密保护

3. **自动重连机制**
   - 断线后自动重试
   - 采用指数退避策略
   - 最多重试 5 次

## 开发计划

- [x] 添加 TLS 加密支持
- [ ] 实现配置文件支持
- [ ] 添加 Web 管理界面
- [ ] 支持多路复用
- [ ] 添加流量统计功能

## 更新日志

### v0.1.3 (2024-11-10)
- HTTP / HTTPS 支持
- 添加自定义域名支持

### v0.1.2 (2024-11-09)
- 修复了入口函数的导入问题

### v0.1.1 (2024-11-09)
- 改用 typer 替代 argparse

### v0.1.0 (2024-11-09)
- 初始版本发布
- 实现基本的反向代理功能
- 添加命令行界面
- 支持服务器-客户端模式

---
Made with ❤️ by [CocoTeirina](https://github.com/CocoTeirina)