from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class Attachment(BaseModel):
    url: str
    filename: str

class Message(BaseModel):
    discord_user_id: str
    discord_username: str
    guild_id: Optional[str] = None
    channel_id: str
    message_id: str
    content: str
    timestamp: datetime
    attachments: Optional[list[Attachment]] = None


class TimerTick(BaseModel):
    previous_tick: datetime
    current_tick: datetime