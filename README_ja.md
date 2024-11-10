# Tsuraika

[简体中文](https://github.com/cocoteirina/tsuraika/blob/main/docs/README.md) | [English](https://github.com/cocoteirina/tsuraika/blob/main/docs/README_en.md) | [日本語](https://github.com/cocoteirina/tsuraika/blob/main/docs/README_ja.md)

[![Python バージョン](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/downloads/) [![PyPI](https://img.shields.io/pypi/v/tsuraika)](https://pypi.org/project/tsuraika/) [![ライセンス](https://img.shields.io/github/license/cocoteirina/tsuraika)](https://github.com/cocoteirina/tsuraika/blob/main/LICENSE)

Tsuraika はシンプルでありながら強力なリバースプロキシツールで、内部サービスを安全に公衆網に公開することができます。Python で実装され、サーバー・クライアントモードをサポートし、開発テスト、イントラネットペネトレーションなどのシーンに適しています。

## 特徴

- 🚀 使いやすいコマンドラインインターフェース
- 🔒 サーバー・クライアントモードをサポート
- 🔄 自動再接続機能
- 📊 詳細なログ記録
- 🛡 安定した接続管理
- ⚡ 効率的なデータ転送
- 📡 TCP ポート転送
- 🌐 HTTP/HTTPS プロトコルプロキシ
- 🏷 カスタムドメインサポート
- 🔒 SSL/TLS 暗号化サポート
- 🖥 クロスプラットフォームサポート

## インストール

### PyPI からインストール（推奨）

```bash
pip install tsuraika
```

### ソースコードからインストール

```bash
git clone https://github.com/cocoteirina/tsuraika.git
cd tsuraika
pip install.
```

## 簡単な使い方

### サーバー起動

```bash
# 基本的なサーバー（ポート 7000）
tsuraika server -p 7000

# SSL 有効なサーバー
tsuraika server -p 7000 --ssl-cert cert.pem --ssl-key key.pem
```

### クライアント起動

#### TCP ポート転送
```bash
# ローカルの 8080 ポートをリモートの 80 ポートに転送
tsuraika client \
    --local-addr localhost \
    --local-port 8080 \
    --remote-addr example.com \
    --remote-port 80 \
    --server-port 7000
```

#### カスタムドメインを使用した HTTP プロキシ

```bash
# カスタムドメインでローカルの Web サービスを公開
tsuraika client \
    --local-addr localhost \
    --local-port 8080 \
    --remote-addr example.com \
    --custom-domain myapp.example.com \
    --protocol http \
    --server-port 7000
```

## コマンドライン引数

### サーバーオプション

```bash
tsuraika server [options]
```

| オプション | 説明 | デフォルト値 |
|--------|-------------|---------|
| `--port`, `-p` | サーバーの制御ポート | 7000 |
| `--ssl-cert` | SSL 証明書ファイル | なし |
| `--ssl-key` | SSL 秘密鍵ファイル | なし |

### クライアントオプション

```bash
tsuraika client [options]
```

| オプション | 説明 | 必須か否か |
|--------|-------------|----------|
| `--local-addr`, `-l` | ローカルサービスのアドレス | はい |
| `--local-port`, `-p` | ローカルサービスのポート | はい |
| `--remote-addr`, `-r` | リモートサーバーのアドレス | はい |
| `--remote-port`, `-P` | リモートで公開するポート | いいえ* |
| `--custom-domain`, `-d` | HTTP/HTTPS プロキシのカスタムドメイン | いいえ* |
| `--protocol` | プロトコル種類（tcp/http/https） | いいえ（デフォルト: tcp） |
| `--server-port`, `-s` | サーバーの制御ポート | いいえ（デフォルト: 7000） |

*HTTP/HTTPS プロトコルの場合は、`remote-port`または`custom-domain`のいずれかを指定する必要があります。

## 利用シーン

1. **開発テスト**
   - 迅速にローカル開発環境をテスターに公開。
   - 開発成果をクライアントに簡単に示す。

2. **イントラネットペネトレーション**
   - 安全にイントラネットサービスを公衆網に公開。
   - リモートからイントラネットリソースにアクセス。

3. **一時的なサービス共有**
   - ローカルで実行中のウェブサイトやサービスを共有。
   - 共同開発やデバッグ。

## 利用例

### ローカル開発サーバー

ローカル開発サーバーを公衆網に公開：

```bash
# サーバー
tsuraika server -p 7000

# クライアント
tsuraika client \
    --local-addr localhost \
    --local-port 3000 \
    --remote-addr your-server.com \
    --remote-port 8080 \
    --protocol http
```

### HTTPS セキュアサービス

カスタムドメインを持つ HTTPS プロキシを設定：

```bash
# サーバー（SSL 証明書を設定）
tsuraika server \
    -p 7000 \
    --ssl-cert /path/to/cert.pem \
    --ssl-key /path/to/key.pem

# クライアント
tsuraika client \
    --local-addr localhost \
    --local-port 8080 \
    --remote-addr your-server.com \
    --custom-domain secure.example.com \
    --protocol https
```

### データベースポート転送

ローカルデータベースポートを安全に転送：

```bash
tsuraika client \
    --local-addr localhost \
    --local-port 5432 \
    --remote-addr your-server.com \
    --remote-port 54320
```

## よくある質問

1. **接続に失敗した場合は？**
   - サーバーが正常に動作しているか確認。
   - ファイアウォールの設定を確認。
   - ポートが占有されていないか確認。

2. **プロトコルはどう選ぶ？**
   - TCP：一般的なポート転送に適しています。
   - HTTP：Web サービスに適し、ドメインをサポート。
   - HTTPS：SSL 証明書が必要で、暗号化保護を提供。

3. **自動再接続機能**
   - 切断後自動的に再接続を試み。
   - 指数バックオフ戦略を採用。
   - 最大 5 回まで再試行。

## 開発計画

- [x] TLS 暗号化サポート追加
- [ ] 設定ファイルサポート実装
- [ ] Web 管理インターフェース追加
- [ ] 多重化サポート
- [ ] トラフィック統計機能追加

## 更新履歴

### v0.1.3 (2024-11-10)
- HTTP / HTTPS サポート
- カスタムドメインサポート追加

### v0.1.2 (2024-11-09)
- エントリー関数のインポート問題を修正。

### v0.1.1 (2024-11-09)
- argparse を typer に置き換え。

### v0.1.0 (2024-11-09)
- 初期バージョンリリース
- 基本的なリバースプロキシ機能実装
- コマンドラインインターフェース追加
- サーバー・クライアントモードサポート

---
❤️によって作成された [CocoTeirina](https://github.com/CocoTeirina)