import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters
import requests
from config import WC_API_URL, CONSUMER_KEY, CONSUMER_SECRET, BOT_TOKEN, SUPPORT_LINK, ADMIN_EMAIL

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

user_subscribers = set()

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "به ژامک‌بات خوش آمدید 🌸\n"
        "لطفاً یکی از گزینه‌ها را انتخاب کنید:",
        reply_markup=main_menu()
    )

def main_menu():
    keyboard = [
        [KeyboardButton("🛍 دسته‌بندی محصولات")],
        [KeyboardButton("📝 ثبت سفارش")],
        [KeyboardButton("📩 عضویت در خبرنامه")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    if text == "🛍 دسته‌بندی محصولات":
        send_categories(update, context)
    elif text == "📩 عضویت در خبرنامه":
        user_id = update.message.chat_id
        user_subscribers.add(user_id)
        update.message.reply_text("✅ شما با موفقیت در خبرنامه عضو شدید.")
    elif text == "📝 ثبت سفارش":
        update.message.reply_text("لطفاً سفارش خود را به صورت دقیق وارد کنید تا بررسی شود:")
        return
    else:
        if update.message:
            message = f"سفارش جدید از کاربر @{update.message.from_user.username}:
{text}"
            context.bot.send_message(chat_id=ADMIN_EMAIL, text=message)
            update.message.reply_text("✅ سفارش شما با موفقیت ثبت شد. به‌زودی با شما تماس خواهیم گرفت.")

def send_categories(update: Update, context: CallbackContext):
    response = requests.get(f"{WC_API_URL}/products/categories", auth=(CONSUMER_KEY, CONSUMER_SECRET))
    categories = response.json()
    keyboard = []
    for cat in categories:
        if cat['count'] > 0:
            keyboard.append([InlineKeyboardButton(cat['name'], callback_data=f"cat_{cat['id']}")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("دسته‌بندی‌ها:", reply_markup=reply_markup)

def category_selected(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    cat_id = query.data.split("_")[1]
    response = requests.get(f"{WC_API_URL}/products", params={
        "category": cat_id,
        "stock_status": "instock",
        "per_page": 10
    }, auth=(CONSUMER_KEY, CONSUMER_SECRET))
    products = response.json()

    if not products:
        query.edit_message_text("متاسفانه محصولی در این دسته موجود نیست ❌")
        return

    for product in products:
        name = product['name']
        price = product['price']
        image_url = product['images'][0]['src'] if product['images'] else None

        caption = f"*{name}*\nقیمت: {price} تومان\nبرای سفارش، پیام دهید."
        keyboard = [[InlineKeyboardButton("📞 پشتیبانی", url=SUPPORT_LINK)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        context.bot.send_photo(chat_id=query.message.chat.id, photo=image_url, caption=caption, parse_mode='Markdown', reply_markup=reply_markup)

def main():
    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(category_selected, pattern=r"^cat_"))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
