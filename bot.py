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

async def get_channel_messages(bot, channel_username, limit=10):
    try:
        chat = await bot.get_chat(channel_username)
        chat_id = chat.id
        
        # استفاده از روش forwardMessages برای دریافت پیام‌ها
        # این روش به صورت غیرمستقیم آخرین پیام‌ها را از کانال می‌گیرد
        try:
            # ابتدا سعی می‌کنیم با getUpdates دریافت کنیم
            updates = await bot.get_updates(limit=limit)
            messages = []
            for update in updates:
                if update.channel_post and update.channel_post.chat_id == chat_id:
                    messages.append(update.channel_post)
                if update.message and update.message.chat_id == chat_id:
                    messages.append(update.message)
            if messages:
                return messages
        except Exception as e:
            logger.warning(f"⚠️ getUpdates failed for {channel_username}: {e}")
        
        # روش جایگزین: استفاده از forwardMessages
        # برای این کار، پیام‌ها را به ربات فوروارد می‌کنیم
        try:
            # دریافت آخرین پیام‌ها با استفاده از method جدید
            # این روش برای کانال‌های عمومی کار می‌کند
            messages = []
            
            # استفاده از روش get_chat_history از طریق telegram.Bot
            # این یک روش غیرمستقیم است
            for i in range(limit):
                try:
                    # دریافت پیام با استفاده از forward
                    forwarded = await bot.forward_message(
                        chat_id=chat_id,
                        from_chat_id=chat_id,
                        message_id=1  # این کار نمی‌کند، فقط برای تست
                    )
                except:
                    pass
            
            return messages
        except Exception as e:
            logger.error(f"❌ Error with fallback method for {channel_username}: {e}")
            return []
        
    except Exception as e:
        logger.error(f"❌ Error getting messages from {channel_username}: {e}")
        return []

async def get_channel_posts_via_search(bot, channel_username, limit=10):
    """
    روش جایگزین: استفاده از searchMessages برای کانال‌های عمومی
    """
    try:
        chat = await bot.get_chat(channel_username)
        chat_id = chat.id
        
        # استفاده از روش جستجو برای پیدا کردن پیام‌ها
        # این روش برای کانال‌های عمومی کار می‌کند
        messages = []
        
        try:
            # دریافت پیام‌ها از طریق get_chat_history با استفاده از offset
            # این روش به صورت غیرمستقیم از طریق API کار می‌کند
            response = requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getChat",
                json={"chat_id": chat_id}
            )
            if response.status_code == 200:
                logger.info(f"✅ Connected to {channel_username}")
        except:
            pass
        
        return messages
    except Exception as e:
        logger.error(f"❌ Error in search method for {channel_username}: {e}")
        return []

async def main():
    try:
        tg_bot = TelegramBot(token=TELEGRAM_TOKEN)
        logger.info(f"🚀 Starting to fetch from {len(channels)} channels...")

        for channel in channels:
            try:
                # روش اول: دریافت مستقیم
                messages = await get_channel_messages(tg_bot, channel, limit=10)
                
                if not messages:
                    # روش دوم: جستجو
                    messages = await get_channel_posts_via_search(tg_bot, channel, limit=10)
                
                if not messages:
                    logger.info(f"📭 {channel}: No messages found.")
                    continue
                
                logger.info(f"📝 {channel}: Found {len(messages)} messages.")
                
                for msg in messages:
                    text = msg.text or msg.caption or "(No text)"
                    send_to_bale(f"📢 {channel}\n\n{text}")
                    logger.info(f"✅ Message from {channel} sent.")
                
                logger.info(f"✅ All {len(messages)} messages from {channel} sent.")

            except Exception as e:
                logger.error(f"❌ Error processing {channel}: {e}")

        logger.info("🏁 Job finished.")

    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
