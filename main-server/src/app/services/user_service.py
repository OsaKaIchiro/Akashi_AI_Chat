from sqlalchemy.orm import Session
from app.models.models import User
from typing import Optional


def get_or_create_user(
    db: Session,
    discord_user_id: str,
    discord_username: str,
    dm_channel_id: Optional[str] = None
) -> User:
    """
    ユーザーを取得、存在しなければ作成する
    
    Args:
        db: DBセッション
        discord_user_id: DiscordユーザーID
        discord_username: Discordユーザー名
        dm_channel_id: DMチャンネルID（任意）
    
    Returns:
        Userオブジェクト
    """
    # 既存ユーザーを検索
    user = db.query(User).filter(User.discord_user_id == discord_user_id).first()
    
    if user:
        # 既存ユーザーが見つかった場合、username や dm_channel_id を更新
        user.discord_username = discord_username
        if dm_channel_id:
            user.dm_channel_id = dm_channel_id
        db.commit()
        db.refresh(user)
    else:
        # 新規ユーザーを作成
        user = User(
            discord_user_id=discord_user_id,
            discord_username=discord_username,
            dm_channel_id=dm_channel_id
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return user


def get_user_by_discord_id(db: Session, discord_user_id: str) -> Optional[User]:
    """
    Discord IDでユーザーを取得
    
    Args:
        db: DBセッション
        discord_user_id: DiscordユーザーID
    
    Returns:
        Userオブジェクト（存在しない場合はNone）
    """
    return db.query(User).filter(User.discord_user_id == discord_user_id).first()
