import os
import logging
import asyncio
import requests
from telegram import Bot as TelegramBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
BALE_TOKEN = os.getenv("BALE_TOKEN")
CHANNELS_LIST = os.getenv("CHANNELS_LIST")
BALE_CHAT_ID = os.getenv("BALE_CHAT_ID")

if not all([TELEGRAM_TOKEN, BALE_TOKEN, CHANNELS_LIST, BALE_CHAT_ID]):
    logger.error("❌ One or more environment variables are missing.")
    exit(1)

channels = [ch.strip() for ch in CHANNELS_LIST.split(",") if ch.strip()]
logger.info(f"📋 Channel list: {channels}")

def send_to_bale(text):
    url = f"https://safir.bale.ai/v3/bot{BALE_TOKEN}/sendMessage"
    payload = {
        "chat_id": BALE_CHAT_ID,
        "text": text
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            logger.info("✅ Message sent to Bale successfully.")
            return True
        else:
            logger.error(f"❌ Failed to send to Bale: {response.text}")
            return False
    except Exception as e:
        logger.error(f"❌ Connection error to Bale: {e}")
        return False

async def get_channel_messages(bot, channel_username):
    try:
        # Get chat entity first
        chat = await bot.get_chat(channel_username)
        
        # Get updates from this chat
        updates = await bot.get_updates(limit=5)
        
        # Filter updates for this channel
        for update in updates:
            if update.channel_post and update.channel_post.chat_id == chat.id:
                return update.channel_post
            if update.message and update.message.chat_id == chat.id:
                return update.message
        return None
    except Exception as e:
        logger.error(f"❌ Error getting messages from {channel_username}: {e}")
        return None

async def main():
    try:
        tg_bot = TelegramBot(token=TELEGRAM_TOKEN)
        logger.info(f"🚀 Starting to fetch from {len(channels)} channels...")

        for channel in channels:
            try:
                last_message = await get_channel_messages(tg_bot, channel)
                if not last_message:
                    logger.info(f"📭 {channel}: No new messages.")
                    continue

                text = last_message.text or last_message.caption or "(No text)"
                send_to_bale(f"📢 {channel}\n\n{text}")
                logger.info(f"✅ Message from {channel} sent.")

            except Exception as e:
                logger.error(f"❌ Error processing {channel}: {e}")

        logger.info("🏁 Job finished.")

    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
