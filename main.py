import telebot
import requests
from config import *
from telebot import types

bot = telebot.TeleBot(BOT_TOKEN)

# ------------------ دسته‌بندی‌ها ------------------
def get_categories():
    url = f"{WC_URL}/products/categories"
    response = requests.get(url, auth=(WC_KEY, WC_SECRET))
    return response.json()

# ------------------ محصولات موجود ------------------
def get_products_by_category(cat_id):
    url = f"{WC_URL}/products?category={cat_id}&stock_status=instock"
    response = requests.get(url, auth=(WC_KEY, WC_SECRET))
    return response.json()

# ------------------ استارت ------------------
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('🛍 دسته‌بندی محصولات')
    markup.row('📝 عضویت در خبرنامه', '📞 پشتیبانی')
    bot.send_message(message.chat.id, """به ژامک‌شاپ خوش آمدید ✨لطفاً یک گزینه را انتخاب کنید:""" , reply_markup=markup)

# ------------------ هندل پیام ------------------
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    if message.text == '🛍 دسته‌بندی محصولات':
        categories = get_categories()
        markup = types.InlineKeyboardMarkup()
        for cat in categories:
            if cat['count'] > 0:
                markup.add(types.InlineKeyboardButton(cat['name'], callback_data=f"cat_{cat['id']}"))
        bot.send_message(message.chat.id, "لطفاً یک دسته را انتخاب کنید:", reply_markup=markup)
    elif message.text == '📝 عضویت در خبرنامه':
        msg = bot.send_message(message.chat.id, "لطفاً شماره تماس خود را ارسال کنید (مثال: 09123456789):")
        bot.register_next_step_handler(msg, save_number)
    elif message.text == '📞 پشتیبانی':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("واتساپ", url=WHATSAPP_LINK))
        markup.add(types.InlineKeyboardButton("تلگرام", url=SUPPORT_TELEGRAM))
        bot.send_message(message.chat.id, "برای پشتیبانی روی یکی از گزینه‌ها کلیک کنید:", reply_markup=markup)

# ------------------ ذخیره شماره ------------------
def save_number(message):
    with open("newsletter.txt", "a") as f:
        f.write(f"{message.chat.id}: {message.text}
")
    bot.send_message(message.chat.id, "شماره شما ذخیره شد. از عضویت در خبرنامه سپاسگزاریم!")

# ------------------ کال‌بک دسته‌بندی ------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("cat_"))
def send_products(call):
    cat_id = call.data.split("_")[1]
    products = get_products_by_category(cat_id)
    if not products:
        bot.send_message(call.message.chat.id, "محصولی در این دسته موجود نیست.")
        return
    for p in products:
        name = p['name']
        price = p['price']
        image = p['images'][0]['src'] if p['images'] else ''
        caption = f"*{name}*
قیمت: {price} تومان
برای سفارش، پیام دهید."
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("سفارش", url=f"https://t.me/{SUPPORT_TELEGRAM_USERNAME}"))
        bot.send_photo(call.message.chat.id, image, caption=caption, parse_mode="Markdown", reply_markup=markup)

bot.infinity_polling()
