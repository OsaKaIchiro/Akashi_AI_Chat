from sqlalchemy.orm import Session
from app.models.models import MessageLog
from datetime import datetime
from typing import Optional


def is_message_processed(db: Session, message_id: str) -> bool:
    """
    メッセージが既に処理されているかチェック
    
    Args:
        db: DBセッション
        message_id: DiscordメッセージID
    
    Returns:
        処理済みならTrue、未処理ならFalse
    """
    exists = db.query(MessageLog).filter(MessageLog.message_id == message_id).first()
    return exists is not None


def save_message_log(
    db: Session,
    message_id: str,
    user_id: int,
    content: str
) -> MessageLog:
    """
    メッセージログを保存
    
    Args:
        db: DBセッション
        message_id: DiscordメッセージID
        user_id: ユーザーID（users.id）
        content: メッセージ内容
    
    Returns:
        MessageLogオブジェクト
    """
    message_log = MessageLog(
        message_id=message_id,
        user_id=user_id,
        content=content
    )
    db.add(message_log)
    db.commit()
    db.refresh(message_log)
    
    return message_log


def get_message_log(db: Session, message_id: str) -> Optional[MessageLog]:
    """
    メッセージログを取得
    
    Args:
        db: DBセッション
        message_id: DiscordメッセージID
    
    Returns:
        MessageLogオブジェクト（存在しない場合はNone）
    """
    return db.query(MessageLog).filter(MessageLog.message_id == message_id).first()
