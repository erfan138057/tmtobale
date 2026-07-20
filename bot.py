import os
import logging
from telegram import Bot as TelegramBot
from bale import Bot as BaleBot

# تنظیم لاگ برای مشاهده خطاها و اطلاعات
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# دریافت اطلاعات از Secrets گیت‌هاب
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
BALE_TOKEN = os.getenv("BALE_TOKEN")
CHANNELS_LIST = os.getenv("CHANNELS_LIST")  # لیست کانال‌ها به صورت @channel1,@channel2,...
BALE_CHAT_ID = os.getenv("BALE_CHAT_ID")

# بررسی اینکه همه اطلاعات وارد شده باشند
if not all([TELEGRAM_TOKEN, BALE_TOKEN, CHANNELS_LIST, BALE_CHAT_ID]):
    logger.error("❌ یکی از متغیرهای محیطی (Secrets) مقداردهی نشده است.")
    exit(1)

# تبدیل لیست کانال‌ها از رشته به آرایه
channels = [ch.strip() for ch in CHANNELS_LIST.split(",") if ch.strip()]
logger.info(f"📋 لیست کانال‌ها: {channels}")

def main():
    try:
        # اتصال به ربات تلگرام
        tg_bot = TelegramBot(token=TELEGRAM_TOKEN)
        # اتصال به ربات بله
        bale_bot = BaleBot(token=BALE_TOKEN)

        logger.info("🚀 شروع دریافت پیام‌ها از کانال‌های تلگرام...")

        for channel in channels:
            try:
                # دریافت آخرین پیام از کانال
                updates = tg_bot.get_updates(chat_id=channel, limit=1)

                if not updates:
                    logger.info(f"📭 کانال {channel}: پیام جدیدی وجود ندارد.")
                    continue

                # پیدا کردن آخرین پیام (متن یا کپشن)
                last_message = None
                for update in updates:
                    if update.channel_post:
                        last_message = update.channel_post
                        break
                    if update.message:
                        last_message = update.message
                        break

                if not last_message:
                    logger.info(f"📭 کانال {channel}: پیامی یافت نشد.")
                    continue

                # گرفتن متن یا کپشن پیام
                text = last_message.text or last_message.caption or "(پیام بدون متن)"

                # ارسال به بله
                bale_bot.send_message(
                    chat_id=BALE_CHAT_ID,
                    text=f"📢 {channel}\n\n{text}"
                )
                logger.info(f"✅ پیام از {channel} به بله ارسال شد.")

            except Exception as e:
                logger.error(f"❌ خطا در پردازش کانال {channel}: {e}")
                continue

        logger.info("🏁 پایان اجرای ربات.")

    except Exception as e:
        logger.error(f"❌ خطای کلی در اجرای ربات: {e}")
        raise

if __name__ == "__main__":
    main()
