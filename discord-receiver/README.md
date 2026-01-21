# Discord Receiver

Discord Botとして動作し、メッセージを受信してメインサーバーに転送するコンポーネントです。

## 概要

- **役割**: Discordからのメッセージを受信し、メインサーバーの `/api/v1/messages` エンドポイントに転送
- **使用技術**: Python 3.12, discord.py, httpx
- **実行環境**: Dockerコンテナ

## 機能

1. **Discord Bot起動**: Discord APIに接続してメッセージイベントをリッスン
2. **メッセージ受信**: ユーザーからのメッセージ（サーバー/DM両方）を受信
3. **データ変換**: メッセージをJSON形式に変換
4. **転送**: HTTPリクエストでメインサーバーに送信

## 環境変数

| 変数名 | 必須 | デフォルト | 説明 |
|-------|------|-----------|------|
| DISCORD_BOT_TOKEN | ○ | - | Discord Bot トークン |
| MAIN_SERVER_URL | △ | http://main-server:8000 | メインサーバーのURL |

## セットアップ

### 1. Discord Bot作成

1. [Discord Developer Portal](https://discord.com/developers/applications)にアクセス
2. 「New Application」でアプリケーションを作成
3. 「Bot」タブで「Add Bot」をクリック
4. トークンをコピーして `.env` ファイルに設定

### 2. Bot権限設定

以下の権限が必要です：
- **Privileged Gateway Intents**:
  - `MESSAGE CONTENT INTENT` (メッセージ内容を読むため)
- **Bot Permissions**:
  - `Read Messages/View Channels`
  - `Send Messages`
  - `Read Message History`

### 3. Botを招待

OAuth2 URL Generatorで以下を選択：
- **SCOPES**: `bot`
- **BOT PERMISSIONS**: 上記の権限を選択
- 生成されたURLでサーバーに招待

## 転送データ形式

メインサーバーへのPOSTリクエスト形式：

```json
{
  "discord_user_id": "123456789012345678",
  "discord_username": "example_user",
  "guild_id": "987654321098765432",
  "channel_id": "111222333444555666",
  "message_id": "999888777666555444",
  "content": "ユーザーのメッセージ本文",
  "timestamp": "2025-12-03T10:30:00.000Z",
  "attachments": [
    {
      "url": "https://cdn.discordapp.com/...",
      "filename": "image.png"
    }
  ]
}
```

## ログ

- **INFO**: Bot起動、メッセージ受信、転送成功
- **ERROR**: 転送失敗、Discord API エラー

ログ確認：
```bash
docker-compose logs -f discord-receiver
```

## トラブルシューティング

### Bot が起動しない

- `DISCORD_BOT_TOKEN` が正しく設定されているか確認
- `.env` ファイルが正しい場所にあるか確認
- Docker コンテナのログを確認

### メッセージが受信できない

- Bot がサーバーに招待されているか確認
- `MESSAGE CONTENT INTENT` が有効になっているか確認
- Bot にチャンネル閲覧権限があるか確認

### メインサーバーへの転送が失敗する

- `MAIN_SERVER_URL` が正しいか確認
- main-server コンテナが起動しているか確認
- ネットワーク設定を確認（`docker-compose.yml` の `app-network`）
