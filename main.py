import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
import smtplib
from email.mime.text import MIMEText
from config import TELEGRAM_TOKEN, WC_API_URL, WC_CONSUMER_KEY, WC_CONSUMER_SECRET, EMAIL_ADDRESS, EMAIL_PASSWORD, SUPPORT_USERNAME

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🛍️ مشاهده محصولات", callback_data="products")],
        [InlineKeyboardButton("📩 عضویت در خبرنامه", callback_data="subscribe")],
        [InlineKeyboardButton("🆘 پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")]
    ]
    await update.message.reply_text("به ژامک‌بات خوش آمدید! یکی از گزینه‌ها را انتخاب کنید:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "products":
        await send_products(query, context)
    elif query.data == "subscribe":
        await query.edit_message_text("لطفاً ایمیل خود را ارسال کنید تا در خبرنامه عضو شوید.")
        context.user_data["subscribe_mode"] = True

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("subscribe_mode"):
        email = update.message.text
        context.user_data["subscribe_mode"] = False
        await update.message.reply_text(f"ایمیل شما ({email}) در خبرنامه ثبت شد. ✅")
        # ایمیل به مدیر سایت
        send_email("عضویت در خبرنامه", f"ایمیل جدید: {email}")
    else:
        await update.message.reply_text("برای شروع /start را بزنید.")

async def send_products(query, context):
    response = requests.get(WC_API_URL, auth=(WC_CONSUMER_KEY, WC_CONSUMER_SECRET))
    products = response.json()

    for product in products[:5]:
        name = product['name']
        price = product['price']
        image = product['images'][0]['src'] if product['images'] else ""
        caption = f"*{name}*"
قیمت: {price} تومان
برای سفارش، پیام دهید."
        await context.bot.send_photo(chat_id=query.message.chat.id, photo=image, caption=caption, parse_mode="Markdown")

def send_email(subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_ADDRESS

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_query))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
