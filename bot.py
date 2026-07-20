import os
import logging
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

def main():
    try:
        tg_bot = TelegramBot(token=TELEGRAM_TOKEN)
        logger.info(f"🚀 Starting to fetch from {len(channels)} channels...")

        for channel in channels:
            try:
                updates = tg_bot.get_updates(chat_id=channel, limit=1)
                if not updates:
                    logger.info(f"📭 {channel}: No new messages.")
                    continue

                last_message = None
                for update in updates:
                    if update.channel_post:
                        last_message = update.channel_post
                        break
                    if update.message:
                        last_message = update.message
                        break

                if not last_message:
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
    main()
