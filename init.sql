-- users（ユーザーテーブル）
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    discord_user_id VARCHAR(20) NOT NULL UNIQUE,
    discord_username VARCHAR(100) NOT NULL,
    dm_channel_id VARCHAR(20),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- user_settings（ユーザー設定テーブル）
CREATE TABLE user_settings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    notification_enabled BOOLEAN NOT NULL DEFAULT true,
    notification_time TIME,
    timezone VARCHAR(50) NOT NULL DEFAULT 'Asia/Tokyo',
    UNIQUE(user_id)
);

-- reminders（リマインダーテーブル）
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

-- message_logs（メッセージログテーブル）
CREATE TABLE message_logs (
    id SERIAL PRIMARY KEY,
    message_id VARCHAR(20) NOT NULL UNIQUE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    processed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_message_logs_user_id ON message_logs(user_id);
