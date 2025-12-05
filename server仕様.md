# サーバ仕様

## 技術選定

### 言語・フレームワーク

| コンポーネント | 技術 | 理由 |
|--------------|------|------|
| Discord受信サーバ | **Python + FastAPI** | 言語統一、discord.py使用可 |
| 中央サーバ | **Python + FastAPI** | シンプルなAPI構築、型ヒント対応 |
| DB | **PostgreSQL** | 信頼性、JSONサポート、無料 |
| 定期タイマー | **cron (コンテナ内)** | シンプル、追加サービス不要 |

---

## インフラ構成

### 概要図

```
┌─────────────────────────────────────────────────────────────┐
│                     Docker Network                          │
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   discord    │    │    main      │    │   postgres   │  │
│  │   receiver   │───▶│   server     │───▶│     db       │  │
│  │  (FastAPI)   │    │  (FastAPI)   │    │              │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                             ▲                               │
│                             │                               │
│                      ┌──────────────┐                       │
│                      │    cron      │                       │
│                      │   (timer)    │                       │
│                      └──────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

### コンテナ構成

| サービス名 | イメージ | ポート | 役割 |
|-----------|---------|--------|------|
| discord-receiver | python:3.12-slim | 3000 (内部) | Discord Webhook受信 → 中央サーバへ転送 |
| main-server | python:3.12-slim | 8000 (内部) | メイン処理、Discord送信、DB操作 |
| postgres | postgres:16-alpine | 5432 (内部) | データベース |
| cron | alpine + curl | - | 定期的にmain-serverへPOST |

---

### docker-compose.yml

```yaml
version: '3.8'

services:

  # Discord受信サーバ
  discord-receiver:
    build: ./discord-receiver
    container_name: discord-receiver
    restart: unless-stopped
    environment:
      - MAIN_SERVER_URL=http://main-server:8000
      - DISCORD_BOT_TOKEN=${DISCORD_BOT_TOKEN}
    depends_on:
      - main-server
    networks:
      - app-network

  # 中央サーバ
  main-server:
    build: ./main-server
    container_name: main-server
    restart: unless-stopped
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/botdb
      - DISCORD_BOT_TOKEN=${DISCORD_BOT_TOKEN}
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - app-network

  # PostgreSQL
  postgres:
    image: postgres:16-alpine
    container_name: postgres
    restart: unless-stopped
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=botdb
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d botdb"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - app-network

  # 定期タイマー
  cron:
    build: ./cron
    container_name: cron
    restart: unless-stopped
    environment:
      - MAIN_SERVER_URL=http://main-server:8000
    depends_on:
      - main-server
    networks:
      - app-network

networks:
  app-network:
    driver: bridge

volumes:
  postgres_data:
```

---

### ディレクトリ構成

```
project/
├── docker-compose.yml
├── .env                      # 環境変数（DISCORD_BOT_TOKEN等）
├── init.sql                  # DB初期化SQL
│
├── discord-receiver/         # Discord受信サーバ
│   ├── Dockerfile
│   ├── requirements.txt
│   └── src/
│       └── main.py
│
├── main-server/              # 中央サーバ
│   ├── Dockerfile
│   ├── requirements.txt
│   └── src/
│       ├── main.py
│       ├── api/
│       ├── services/
│       └── models/
│
└── cron/                     # 定期タイマー
    ├── Dockerfile
    └── crontab
```

---

### 各Dockerfile（簡易版）

**discord-receiver/Dockerfile**:
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "3000"]
```

**main-server/Dockerfile**:
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**cron/Dockerfile**:
```dockerfile
FROM alpine:latest
RUN apk add --no-cache curl tzdata
ENV TZ=Asia/Tokyo
COPY crontab /etc/crontabs/root
CMD ["crond", "-f"]
```

**cron/crontab**:
```
# 毎時0分にタイマーAPIを呼び出す
0 * * * * curl -X POST -H "Content-Type: application/json" -d '{"previous_tick":"'$(date -u -d '1 hour ago' +\%Y-\%m-\%dT\%H:\%M:\%S.000Z)'","current_tick":"'$(date -u +\%Y-\%m-\%dT\%H:\%M:\%S.000Z)'"}' http://main-server:8000/api/v1/timer/tick
```

---

### 共通 requirements.txt

**discord-receiver/requirements.txt**:
```
fastapi==0.104.1
uvicorn==0.24.0
httpx==0.25.2
discord.py==2.3.2
```

**main-server/requirements.txt**:
```
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
discord.py==2.3.2
pydantic==2.5.2
```

---

### 環境変数 (.env)

```env
# Discord
DISCORD_BOT_TOKEN=your_bot_token_here

# PostgreSQL（本番では変更必須）
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=botdb
```

---

### 起動コマンド

```bash
# 初回起動
docker-compose up -d --build

# ログ確認
docker-compose logs -f

# 停止
docker-compose down

# DBデータも含めて完全削除
docker-compose down -v
```

---

## discord受信サーバ
### 概要
・discordをwebhookで監視し、得られたメッセージを中央サーバに送る

### 詳細

## 中央サーバ
### 概要
・ユーザーメッセージを受け取り、内部で返答を作成して、discordSDKで送信する。
・定期タイマーをpostリクエストで受けとって、該当者に返答を作成して、discordSDKで送信する。

### API仕様

※ 内部通信専用のため、認証ヘッダーは不要（ファイアウォール/ネットワークレベルでアクセス制限を行う）

---

#### 1. ユーザーメッセージ受信 API

**エンドポイント**: `POST /api/v1/messages`

**概要**: Discord受信サーバから転送されたユーザーメッセージを受け取り、処理して返答を生成・送信する。

**リクエストヘッダー**:
| ヘッダー名 | 必須 | 説明 |
|-----------|------|------|
| Content-Type | ○ | `application/json` |

**リクエストボディ**:
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
      "url": "https://cdn.discordapp.com/attachments/...",
      "filename": "image.png"
    }
  ]
}
```

| フィールド | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| discord_user_id | string | ○ | DiscordユーザーID（スノーフレーク） |
| discord_username | string | ○ | Discordユーザー名 |
| guild_id | string / null | ○ | サーバーID（DMの場合は`null`） |
| channel_id | string | ○ | チャンネルID（※DMでも存在する。DMチャンネルのID） |
| message_id | string | ○ | メッセージID（重複排除用） |
| content | string | ○ | メッセージ本文 |
| timestamp | string (ISO 8601) | ○ | メッセージ送信時刻 |
| attachments | array | △ | 添付ファイル（URLとファイル名のみ。省略可） |
| attachments[].url | string | ○ | 添付ファイルのURL |
| attachments[].filename | string | ○ | ファイル名 |

**レスポンス**:

受付成功時（200 OK）:
```json
{
  "status": "ok"
}
```

エラー時（4xx / 5xx）:
```json
{
  "status": "error",
  "message": "エラー内容の説明"
}
```

| HTTPステータス | 説明 |
|---------------|------|
| 200 | 受付成功 |
| 400 | リクエスト形式が不正 |
| 500 | サーバ内部エラー |

---

#### 2. 定期タイマー API

**エンドポイント**: `POST /api/v1/timer/tick`

**概要**: 外部タイマー（cron等）から定期的に呼び出される。中央サーバは経過時間を元に、DBを参照して該当ユーザーへ通知を送信する。

**リクエストヘッダー**:
| ヘッダー名 | 必須 | 説明 |
|-----------|------|------|
| Content-Type | ○ | `application/json` |

**リクエストボディ**:
```json
{
  "previous_tick": "2025-12-03T08:00:00.000Z",
  "current_tick": "2025-12-03T09:00:00.000Z"
}
```

| フィールド | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| previous_tick | string (ISO 8601) | ○ | 前回のタイマー発火時刻 |
| current_tick | string (ISO 8601) | ○ | 今回のタイマー発火時刻 |

**レスポンス**:

受付成功時（200 OK）:
```json
{
  "status": "ok"
}
```

エラー時（4xx / 5xx）:
```json
{
  "status": "error",
  "message": "エラー内容の説明"
}
```

| HTTPステータス | 説明 |
|---------------|------|
| 200 | 受付成功 |
| 400 | リクエスト形式が不正 |
| 500 | サーバ内部エラー |

**備考**: 対象ユーザーのフィルタリング（誰に通知を送るか）は、中央サーバ内でDBを参照して決定する。

## DB
### 概要
postgreSQLを使い、ユーザごとの情報を管理する。

### テーブル設計

---

#### 1. users（ユーザーテーブル）

ユーザーの基本情報を管理する。

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|-----|------|-----------|------|
| id | SERIAL | NO | - | 内部ID（主キー） |
| discord_user_id | VARCHAR(20) | NO | - | DiscordユーザーID（ユニーク） |
| discord_username | VARCHAR(100) | NO | - | Discordユーザー名 |
| dm_channel_id | VARCHAR(20) | YES | NULL | DMチャンネルID（DM送信用） |
| is_active | BOOLEAN | NO | true | 有効/無効フラグ |
| created_at | TIMESTAMP | NO | CURRENT_TIMESTAMP | 登録日時 |
| updated_at | TIMESTAMP | NO | CURRENT_TIMESTAMP | 更新日時 |

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    discord_user_id VARCHAR(20) NOT NULL UNIQUE,
    discord_username VARCHAR(100) NOT NULL,
    dm_channel_id VARCHAR(20),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

---

#### 2. user_settings（ユーザー設定テーブル）

ユーザーごとの設定（通知時間帯など）を管理する。

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|-----|------|-----------|------|
| id | SERIAL | NO | - | 主キー |
| user_id | INTEGER | NO | - | 外部キー（users.id） |
| notification_enabled | BOOLEAN | NO | true | 通知を受け取るか |
| notification_time | TIME | YES | NULL | 通知希望時刻（例: 09:00） |
| timezone | VARCHAR(50) | NO | 'Asia/Tokyo' | タイムゾーン |

```sql
CREATE TABLE user_settings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    notification_enabled BOOLEAN NOT NULL DEFAULT true,
    notification_time TIME,
    timezone VARCHAR(50) NOT NULL DEFAULT 'Asia/Tokyo',
    UNIQUE(user_id)
);
```

---

#### 3. reminders（リマインダーテーブル）

ユーザーが登録したリマインダー/タスクを管理する。

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|-----|------|-----------|------|
| id | SERIAL | NO | - | 主キー |
| user_id | INTEGER | NO | - | 外部キー（users.id） |
| content | TEXT | NO | - | リマインダー内容 |
| remind_at | TIMESTAMP | NO | - | 通知予定日時 |
| is_completed | BOOLEAN | NO | false | 完了フラグ |
| is_notified | BOOLEAN | NO | false | 通知済みフラグ |
| created_at | TIMESTAMP | NO | CURRENT_TIMESTAMP | 作成日時 |

```sql
CREATE TABLE reminders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    remind_at TIMESTAMP NOT NULL,
    is_completed BOOLEAN NOT NULL DEFAULT false,
    is_notified BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_reminders_remind_at ON reminders(remind_at);
CREATE INDEX idx_reminders_user_id ON reminders(user_id);
```

---

#### 4. message_logs（メッセージログテーブル）

処理済みメッセージを記録し、重複処理を防止する。

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|-----|------|-----------|------|
| id | SERIAL | NO | - | 主キー |
| message_id | VARCHAR(20) | NO | - | DiscordメッセージID（ユニーク） |
| user_id | INTEGER | NO | - | 外部キー（users.id） |
| content | TEXT | NO | - | メッセージ内容 |
| processed_at | TIMESTAMP | NO | CURRENT_TIMESTAMP | 処理日時 |

```sql
CREATE TABLE message_logs (
    id SERIAL PRIMARY KEY,
    message_id VARCHAR(20) NOT NULL UNIQUE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    processed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_message_logs_user_id ON message_logs(user_id);
```

---

### ER図（簡易）

```
users
  │
  ├──< user_settings (1:1)
  │
  ├──< reminders (1:N)
  │
  └──< message_logs (1:N)
```

---

### 想定クエリ例

**タイマーAPIで通知対象ユーザーを取得**:
```sql
SELECT u.discord_user_id, u.dm_channel_id, r.id, r.content
FROM users u
JOIN reminders r ON u.id = r.user_id
JOIN user_settings s ON u.id = s.user_id
WHERE u.is_active = true
  AND s.notification_enabled = true
  AND r.is_completed = false
  AND r.is_notified = false
  AND r.remind_at BETWEEN :previous_tick AND :current_tick;
```

**重複メッセージチェック**:
```sql
SELECT EXISTS(SELECT 1 FROM message_logs WHERE message_id = :message_id);
```