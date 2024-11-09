# Tsuraika

Tsuraika 是一个简单但功能强大的反向代理工具，可以帮助你将内部服务安全地暴露到公网。基于 Python 实现，支持服务器-客户端模式运行，适用于开发测试、内网穿透等场景。

## 特性

- 🚀 简单易用的命令行界面
- 🔒 支持服务器-客户端模式
- 🔄 自动重连机制
- 📊 详细的日志记录
- 🛡 稳定的连接管理
- ⚡ 高效的数据转发

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
tsuraika server --port 7000
```

### 启动客户端

```bash
tsuraika client \
    --local-addr localhost \
    --local-port 8080 \
    --remote-addr example.com \
    --remote-port 80 \
    --server-port 7000
```

## 命令行参数

### 服务器模式

```
tsuraika server [OPTIONS]

Options:
  -p, --port INTEGER  服务器控制端口 [default: 7000]
  --help             显示帮助信息
```

### 客户端模式

```
tsuraika client [OPTIONS]

Options:
  -l, --local-addr TEXT   本地服务地址 [required]
  -p, --local-port INTEGER  本地服务端口 [required]
  -r, --remote-addr TEXT    远程服务器地址 [required]
  -P, --remote-port INTEGER 远程暴露端口 [required]
  -s, --server-port INTEGER 服务器控制端口 [default: 7000]
  --help                   显示帮助信息
```

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

## 项目结构

```
tsuraika/
├── tsuraika/
│   ├── __init__.py
│   ├── core.py        # 核心功能实现
│   └── cli.py         # 命令行接口
├── setup.py
├── README.md
└── requirements.txt
```

## 技术细节

- 使用 Python 异步 Socket 编程
- 采用线程池管理连接
- 实现指数退避重连策略
- 支持优雅关闭和资源清理

## 常见问题

### 1. 连接被重置

可能的原因：
- 防火墙限制
- 网络不稳定
- 服务器负载过高

解决方案：
- 检查防火墙设置
- 确保网络连接稳定
- 适当增加重试次数和间隔

### 2. 端口已被占用

解决方案：
- 使用 `netstat` 检查端口占用情况
- 选择其他可用端口
- 关闭占用端口的程序

## 开发计划

- [ ] 添加 TLS 加密支持
- [ ] 实现配置文件支持
- [ ] 添加 Web 管理界面
- [ ] 支持多路复用
- [ ] 添加流量统计功能

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 更新日志

### v0.1.0 (2024-03-09)
- 初始版本发布
- 实现基本的反向代理功能
- 添加命令行界面
- 支持服务器-客户端模式