import telegram
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
import pytesseract
from PIL import Image
import io
import os

# --- আপনার টেলিগ্রাম বট টোকেন এখানে দিন ---
BOT_TOKEN = "7907973008:AAHl22xnla_tk7zG8J1nW1Hqap5DMiVcQog"  # <<<<<<<<<<<<<<<<<<<<< এখানে আপনার বট টোকেন লিখুন

# --- Tesseract OCR এর পাথ (path) ---
# Seenode.com এ Tesseract ইনস্টল করা নাও থাকতে পারে।
# সেক্ষেত্রে, এটি কাজ নাও করতে পারে অথবা Seenode এর সাপোর্টের সাথে কথা বলতে হতে পারে।
# যদি আপনার কম্পিউটারে Tesseract ইনস্টল করা থাকে এবং আপনি লোকালি টেস্ট করতে চান,
# তাহলে tesseract.exe ফাইলের পাথ এখানে দিতে হবে।
# উদাহরণস্বরূপ উইন্ডোজের জন্য: pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# লিনাক্সে সাধারণত ইনস্টল করলে এটি পাথে যুক্ত হয়ে যায়।

def start(update, context):
    """বট শুরু করার কমান্ড হ্যান্ডলার"""
    update.message.reply_text(
        "আসসালামু আলাইকুম! আমাকে একটি ছবি পাঠান, আমি চেষ্টা করবো ছবিতে থাকা লেখা বের করে দিতে।"
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

        # সবচেয়ে ভালো কোয়ালিটির ছবিটি নেওয়া হচ্ছে
        photo_file_id = message.photo[-1].file_id
        photo_file = context.bot.get_file(photo_file_id)

        # ছবিটি বাইট হিসেবে ডাউনলোড করা হচ্ছে
        image_bytes = photo_file.download_as_bytearray()
        image_stream = io.BytesIO(image_bytes)
        img = Image.open(image_stream)

        # ছবি থেকে লেখা বের করা (OCR)
        # এখানে lang='ben+eng' মানে বাংলা এবং ইংরেজি উভয় ভাষার লেখা শনাক্ত করার চেষ্টা করা হবে
        # আপনি চাইলে শুধু 'ben' (বাংলা) অথবা 'eng' (ইংরেজি) ব্যবহার করতে পারেন।
        # Tesseract OCR এ বাংলা ভাষার জন্য trained data ইনস্টল করা থাকতে হবে।
        try:
            text = pytesseract.image_to_string(img, lang='ben+eng')
        except pytesseract.TesseractNotFoundError:
            error_message = (
                "সার্ভারে Tesseract OCR ইনস্টল করা নেই অথবা সঠিকভাবে কনফিগার করা হয়নি। "
                "Seenode.com এ Tesseract সাপোর্ট না থাকলে এই বট কাজ করবে না।"
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
    if BOT_TOKEN == "YOUR_BOT_TOKEN":
        print("ত্রুটি: অনুগ্রহ করে main.py ফাইলের মধ্যে আপনার টেলিগ্রাম বট টোকেন সেট করুন।")
        return

    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # কমান্ড হ্যান্ডলার
    dp.add_handler(CommandHandler("start", start))

    # ছবি হ্যান্ডলার
    dp.add_handler(MessageHandler(Filters.photo, image_handler))

    # অজানা মেসেজের জন্য (শুধু ছবি গ্রহণ করবে)
    dp.add_handler(MessageHandler(Filters.text & (~Filters.command), lambda u,c: u.message.reply_text("আমি শুধু ছবি প্রসেস করতে পারি। অনুগ্রহ করে একটি ছবি পাঠান।")))

    print("বট চালু হয়েছে...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()