import os
import logging
from datetime import datetime, timezone
import discord
from discord.ext import commands
import httpx
import asyncio

# 







logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 環境変数
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
MAIN_SERVER_URL = os.getenv("MAIN_SERVER_URL", "http://main-server:8000")

if not DISCORD_BOT_TOKEN:
    raise ValueError("DISCORD_BOT_TOKEN環境変数が設定されていません")

# Discord Bot設定
intents = discord.Intents.default()
intents.message_content = True  # メッセージ内容を取得するために必要
intents.guilds = True
intents.dm_messages = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    """Bot起動時のイベント"""
    logger.info(f"Discord Bot起動完了: {bot.user.name} (ID: {bot.user.id})")
    logger.info(f"メインサーバーURL: {MAIN_SERVER_URL}")


@bot.event
async def on_message(message: discord.Message):
    """メッセージ受信時のイベント"""
    # Bot自身のメッセージは無視
    if message.author.bot:
        return

    # コマンドの処理を先に実行
    await bot.process_commands(message)

    try:
        # メッセージデータを構築
        message_data = {
            "discord_user_id": str(message.author.id),
            "discord_username": message.author.name,
            "guild_id": str(message.guild.id) if message.guild else None,
            "channel_id": str(message.channel.id),
            "message_id": str(message.id),
            "content": message.content,
            "timestamp": message.created_at.isoformat(),
            "attachments": [
                {
                    "url": attachment.url,
                    "filename": attachment.filename
                }
                for attachment in message.attachments
            ] if message.attachments else []
        }

        logger.info(
            f"メッセージ受信: user={message.author.name}, "
            f"guild={message.guild.name if message.guild else 'DM'}, "
            f"content={message.content[:50]}..."
        )

        # 中央サーバー　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　へ転送
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{MAIN_SERVER_URL}/api/v1/messages",
                json=message_data
            )
            response.raise_for_status()
            
            logger.info(
                f"メインサーバーへ転送成功: message_id={message.id}, "
                f"status={response.status_code}"
            )

    except httpx.HTTPError as e:
        logger.error(f"メインサーバーへの転送失敗: {e}")
    except Exception as e:
        logger.error(f"メッセージ処理中にエラー発生: {e}", exc_info=True)


@bot.event
async def on_error(event: str, *args, **kwargs):
    """エラーハンドリング"""
    logger.error(f"Discord Botでエラー発生: event={event}", exc_info=True)


async def main():
    """メイン処理"""
    try:
        logger.info("Discord Bot起動中...")
        await bot.start(DISCORD_BOT_TOKEN)
    except KeyboardInterrupt:
        logger.info("KeyboardInterruptを検知。シャットダウン中...")
        await bot.close()
    except Exception as e:
        logger.error(f"予期しないエラー: {e}", exc_info=True)
        await bot.close()


if __name__ == "__main__":
    asyncio.run(main())
