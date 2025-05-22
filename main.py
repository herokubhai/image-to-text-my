import telegram
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
import pytesseract
from PIL import Image
import io
import os # <--- os মডিউল ইম্পোর্ট করা হয়েছে

# --- এনভায়রনমেন্ট ভেরিয়েবল থেকে টেলিগ্রাম বট টোকেন নিন ---
BOT_TOKEN = os.environ.get("BOT_TOKEN") # <--- পরিবর্তন: এনভায়রনমেন্ট ভেরিয়েবল থেকে টোকেন লোড হবে

# Tesseract OCR এর পাথ ডকারে সাধারণত প্রয়োজন হয় না, কারণ এটি PATH এ যুক্ত থাকে
# pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract' # <--- ডকারে এটি সাধারণত লাগে না

def start(update, context):
    """বট শুরু করার কমান্ড হ্যান্ডলার"""
    update.message.reply_text(
        "আসসালামু আলাইকুম! আমাকে একটি ছবি পাঠান, আমি চেষ্টা করবো ছবিতে থাকা লেখা বের করে দিতে। (ডকার ভার্সন)"
    )

def image_handler(update, context):
    """ছবি থেকে লেখা বের করার ফাংশন"""
    message = update.message
    chat_id = message.chat_id

    if not message.photo:
        context.bot.send_message(chat_id=chat_id, text="অনুগ্রহ করে একটি ছবি পাঠান।")
        return

    try:
        context.bot.send_message(chat_id=chat_id, text="ছবি প্রসেস করা হচ্ছে, অনুগ্রহ করে অপেক্ষা করুন...")

        photo_file_id = message.photo[-1].file_id
        photo_file = context.bot.get_file(photo_file_id)

        image_bytes = photo_file.download_as_bytearray()
        image_stream = io.BytesIO(image_bytes)
        img = Image.open(image_stream)

        try:
            # lang='ben+eng' মানে বাংলা এবং ইংরেজি উভয় ভাষার লেখা শনাক্ত করার চেষ্টা করা হবে
            text = pytesseract.image_to_string(img, lang='ben+eng')
        except pytesseract.TesseractNotFoundError:
            # এই সমস্যাটি হওয়ার কথা নয় যদি Dockerfile সঠিকভাবে Tesseract ইনস্টল করে
            error_message = (
                "ত্রুটি: ডকার ইমেজে Tesseract OCR সঠিকভাবে ইনস্টল বা কনফিগার করা হয়নি। "
                "অনুগ্রহ করে Dockerfile এবং ডেপ্লয়মেন্ট লগ চেক করুন।"
            )
            print(error_message)
            context.bot.send_message(chat_id=chat_id, text=error_message)
            return
        except Exception as ocr_error:
            print(f"OCR Error: {ocr_error}")
            context.bot.send_message(chat_id=chat_id, text=f"ছবি থেকে লেখা বের করতে সমস্যা হয়েছে: {ocr_error}")
            return

        if text.strip():
            context.bot.send_message(chat_id=chat_id, text="শনাক্ত করা লেখা:\n\n" + text)
        else:
            context.bot.send_message(chat_id=chat_id, text="দুঃখিত, ছবিতে কোনো লেখা খুঁজে পাওয়া যায়নি।")

    except telegram.error.BadRequest as e:
        print(f"Telegram API Error: {e}")
        context.bot.send_message(chat_id=chat_id, text=f"একটি সমস্যা হয়েছে: {e}. অনুগ্রহ করে ছোট সাইজের ছবি দিন।")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        context.bot.send_message(chat_id=chat_id, text="একটি অপ্রত্যাশিত সমস্যা হয়েছে। অনুগ্রহ করে আবার চেষ্টা করুন।")

def main():
    """বট চালু করার প্রধান ফাংশন"""
    if not BOT_TOKEN:
        print("ত্রুটি: BOT_TOKEN এনভায়রনমেন্ট ভেরিয়েবল সেট করা হয়নি। অনুগ্রহ করে এটি সেট করুন।")
        return

    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.photo, image_handler))
    dp.add_handler(MessageHandler(Filters.text & (~Filters.command), lambda u,c: u.message.reply_text("আমি শুধু ছবি প্রসেস করতে পারি। অনুগ্রহ করে একটি ছবি পাঠান।")))

    print("বট চালু হয়েছে (ডকার ভার্সন)...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()