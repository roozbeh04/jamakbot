import telebot
import requests
from config import BOT_TOKEN, WC_URL, WC_KEY, WC_SECRET, SUPPORT_USERNAME, NEWSLETTER_EMAIL, SITE_URL, INSTAGRAM_URL
from config import *
from telebot import types

bot = telebot.TeleBot(BOT_TOKEN)

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🛍️ دسته‌بندی محصولات")
    markup.row("📩 عضویت در خبرنامه", "🆘 پشتیبانی")
    markup.row("🌐 آدرس سایت و اینستاگرام")
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "به ژامک‌شاپ خوش آمدید ✨\nلطفاً یک گزینه را انتخاب کنید:", reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.text == "🛍️ دسته‌بندی محصولات")
def show_categories(message):
    response = requests.get(f"{WC_URL}/products/categories", auth=(WC_KEY, WC_SECRET))
    if response.status_code == 200:
        categories = response.json()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for cat in categories:
            if cat["count"] > 0:
                markup.row(cat["name"])
        markup.row("🔙 بازگشت به منو")
        bot.send_message(message.chat.id, "لطفاً یک دسته‌بندی را انتخاب کنید:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "خطا در دریافت دسته‌بندی‌ها ❌")

@bot.message_handler(func=lambda message: message.text == "🔙 بازگشت به منو")
def back_to_main(message):
    bot.send_message(message.chat.id, "بازگشت به منوی اصلی 🔙", reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.text == "📩 عضویت در خبرنامه")
def newsletter(message):
    msg = bot.send_message(message.chat.id, "لطفاً شماره تماس خود را وارد کنید (مثال: 09121234567):")
    bot.register_next_step_handler(msg, save_newsletter)

def save_newsletter(message):
    phone = message.text.strip()
    with open("newsletter.txt", "a", encoding="utf-8") as f:
        f.write(phone + "\n")
    bot.send_message(message.chat.id, "✅ شماره شما با موفقیت در خبرنامه ثبت شد.")

@bot.message_handler(func=lambda message: message.text == "🆘 پشتیبانی")
def support(message):
    bot.send_message(message.chat.id, f"برای پشتیبانی به آیدی زیر پیام دهید:\n@{SUPPORT_USERNAME}")

@bot.message_handler(func=lambda message: message.text == "🌐 آدرس سایت و اینستاگرام")
def show_links(message):
    bot.send_message(message.chat.id, f"🌐 آدرس سایت و اینستاگرام ژامک‌شاپ:\n\nسایت: {SITE_URL}\nاینستاگرام: {INSTAGRAM_URL}")

@bot.message_handler(func=lambda message: True)
def show_products(message):
    response = requests.get(f"{WC_URL}/products/categories", auth=(WC_KEY, WC_SECRET))
    categories = response.json()
    selected_category = next((cat for cat in categories if cat["name"] == message.text), None)
    if selected_category:
        cat_id = selected_category["id"]
        response = requests.get(f"{WC_URL}/products?category={cat_id}&per_page=100", auth=(WC_KEY, WC_SECRET))
        if response.status_code == 200:
            products = response.json()
            for p in products:
                if p["stock_status"] == "instock" and p["images"]:
                    caption = f"*{p['name']}*\nقیمت: {p['price']} تومان\nبرای سفارش، پیام دهید."
                    bot.send_photo(message.chat.id, photo=p["images"][0]["src"], caption=caption, parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, "محصولی یافت نشد ❌")

bot.infinity_polling()
