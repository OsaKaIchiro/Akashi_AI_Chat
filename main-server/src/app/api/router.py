from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import app.api.schema as schema
from app.db import get_db
from app.services import user_service, message_service, timer_service

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.post("/api/v1/messages")
def receive_message(message: schema.Message, db: Session = Depends(get_db)):
    """
    ユーザーメッセージ受信API
    
    処理フロー:
    1. 重複チェック（message_idで確認）
    2. ユーザー作成または取得
    3. メッセージログ保存
    4. 返答生成・送信（TODO: Discord送信処理）
    """
    try:
        # 1. 重複チェック
        if message_service.is_message_processed(db, message.message_id):
            # 冪等性を保つため、重複時も200を返す
            return {"status": "ok"}
        
        # 2. ユーザー作成または取得
        user = user_service.get_or_create_user(
            db=db,
            discord_user_id=message.discord_user_id,
            discord_username=message.discord_username,
            dm_channel_id=message.channel_id if message.guild_id is None else None
        )
        
        # 3. メッセージログ保存
        message_service.save_message_log(
            db=db,
            message_id=message.message_id,
            user_id=user.id,
            content=message.content
        )
        
        # 4. TODO: 返答生成・Discord送信処理
        # discord_service.send_message(channel_id, response_content)
        
        return {"status": "ok"}
    
    except Exception as e:
        # DB接続エラーなどの予期しないエラー
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/api/v1/timer/tick")
def timer_tick(timer: schema.TimerTick, db: Session = Depends(get_db)):
    """
    定期タイマーAPI
    
    処理フロー:
    1. 通知対象のリマインダーを取得（previous_tick ~ current_tick の範囲）
    2. 各リマインダーに対して通知送信
    3. 通知済みフラグを更新
    """
    try:
        # 1. 通知対象のリマインダーを取得
        reminders_to_notify = timer_service.get_reminders_to_notify(
            db=db,
            previous_tick=timer.previous_tick,
            current_tick=timer.current_tick
        )
        
        # 2. 各リマインダーに対して通知送信
        for user, reminder in reminders_to_notify:
            # TODO: Discord送信処理
            # discord_service.send_reminder(user.dm_channel_id, reminder.content)
            
            # 3. 通知済みフラグを更新
            timer_service.mark_reminder_as_notified(db=db, reminder_id=reminder.id)
        
        return {"status": "ok"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
