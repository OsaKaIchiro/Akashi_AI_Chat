from sqlalchemy.orm import Session
from app.models.models import User, Reminder, UserSettings
from datetime import datetime
from typing import List, Tuple


def get_reminders_to_notify(
    db: Session,
    previous_tick: datetime,
    current_tick: datetime
) -> List[Tuple[User, Reminder]]:
    """
    通知対象のリマインダーを取得
    
    仕様のクエリ例:
    SELECT u.discord_user_id, u.dm_channel_id, r.id, r.content
    FROM users u
    JOIN reminders r ON u.id = r.user_id
    JOIN user_settings s ON u.id = s.user_id
    WHERE u.is_active = true
      AND s.notification_enabled = true
      AND r.is_completed = false
      AND r.is_notified = false
      AND r.remind_at BETWEEN :previous_tick AND :current_tick;
    
    Args:
        db: DBセッション
        previous_tick: 前回のタイマー発火時刻
        current_tick: 今回のタイマー発火時刻
    
    Returns:
        (User, Reminder) のタプルのリスト
    """
    results = (
        db.query(User, Reminder)
        .join(Reminder, User.id == Reminder.user_id)
        .join(UserSettings, User.id == UserSettings.user_id)
        .filter(
            User.is_active == True,
            UserSettings.notification_enabled == True,
            Reminder.is_completed == False,
            Reminder.is_notified == False,
            Reminder.remind_at >= previous_tick,
            Reminder.remind_at < current_tick
        )
        .all()
    )
    
    return results


def mark_reminder_as_notified(db: Session, reminder_id: int) -> None:
    """
    リマインダーを通知済みとしてマーク
    
    Args:
        db: DBセッション
        reminder_id: リマインダーID
    """
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if reminder:
        reminder.is_notified = True
        db.commit()
