import telebot
import requests
import os
from flask import Flask
import threading

BOT_TOKEN = os.getenv('BOT_TOKEN')
HF_TOKEN = os.getenv('HF_TOKEN')

MODEL = "microsoft/Phi-3-mini-4k-instruct"
API_URL = f"https://api-inference.huggingface.co/models/{MODEL}"

bot = telebot.TeleBot(BOT_TOKEN)

# ✅ Flask для "heartbeat" (чтобы Render не убивал бота)
app = Flask(__name__)

@app.route('/')
def health():
    return "Bot is running!", 200

@app.route('/health')
def health_check():
    return "OK", 200

# Запускаем Flask в фоне
def run_flask():
    app.run(host='0.0.0.0', port=10000)

# Запускаем Flask в отдельном потоке
threading.Thread(target=run_flask, daemon=True).start()

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "🤖 Бот работает!")

@bot.message_handler(func=lambda m: True)
def handle(m):
    bot.reply_to(m, f"Получил: {m.text}")

print("🚀 Бот запущен!")
bot.infinity_polling()
