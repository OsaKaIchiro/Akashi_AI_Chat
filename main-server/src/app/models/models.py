from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Time, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text
from app.db import Base
from sqlalchemy import Index

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    discord_user_id = Column(String(20), unique=True, nullable=False)
    discord_username = Column(String(100), nullable=False)
    dm_channel_id = Column(String(20), nullable=True)
    basic_info = Column(JSON, nullable=True)
    is_active = Column(Boolean, server_default=text('true'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    notification_enabled = Column(Boolean, server_default=text('true'), nullable=False)
    notification_time = Column(Time, nullable=True)
    timezone = Column(String(50), server_default=text("'Asia/Tokyo'"), nullable=False)


# 実装前にサービス層で使用するモデルを定義
class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    remind_at = Column(DateTime(timezone=True), nullable=False)
    is_completed = Column(Boolean, server_default=text('false'), nullable=False)
    is_notified = Column(Boolean, server_default=text('false'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index('idx_reminders_remind_at', 'remind_at'),
        Index('idx_reminders_user_id', 'user_id'),
    )

class MessageLog(Base):
    __tablename__ = "message_logs"

    id = Column(Integer, primary_key=True)
    message_id = Column(String(20), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    processed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index('idx_message_logs_user_id', 'user_id'),
    )

class CafeteriaMenu(Base):
    __tablename__ = "cafeteria_menus"

    id = Column(Integer, primary_key=True)
    date = Column(DateTime(timezone=True), nullable=False)
    data = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index('idx_cafeteria_menus_date', 'date'),
    )

class DormitoryCafeteriaMenu(Base):
    __tablename__ = "dormitory_cafeteria_menus"

    id = Column(Integer, primary_key=True)
    date = Column(DateTime(timezone=True), nullable=False)
    part = Column(String(20), nullable=False)
    data = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index('idx_dormitory_cafeteria_menus_date', 'date'),
    )


class ConversationLog(Base):
    __tablename__ = "conversation_logs"

    id = Column(Integer, primary_key=True)
    message_id = Column(String(20), unique=True, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index('idx_conversation_logs_user_id_created_at', 'user_id', 'created_at'),
    )