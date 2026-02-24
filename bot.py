import telebot
import requests
import os

BOT_TOKEN = os.getenv('BOT_TOKEN')  # Токен бота
HF_TOKEN = os.getenv('HF_TOKEN')    # Токен HF

# Модель
MODEL = "microsoft/Phi-3-mini-4k-instruct"
API_URL = f"https://api-inference.huggingface.co/models/{MODEL}"

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "🤖 Привет! Я AI-бот на Hugging Face. Спроси что угодно!")

@bot.message_handler(func=lambda m: True)
def handle(m):
    wait = bot.reply_to(m, "⏳ Думаю...")
    
    try:
        headers = {
            "Authorization": f"Bearer {HF_TOKEN}",
            "Content-Type": "application/json"
        }
        data = {
            "inputs": m.text,
            "parameters": {
                "max_new_tokens": 200,
                "return_full_text": False
            }
        }
        
        resp = requests.post(API_URL, headers=headers, json=data, timeout=40)
        
        if resp.status_code == 503:
            bot.edit_message_text("⏳ Модель загружается... Подожди 30 сек и попробуй снова.", m.chat.id, wait.message_id)
            return
        elif resp.status_code == 401:
            bot.edit_message_text("❌ Неверный токен HF. Проверь настройки.", m.chat.id, wait.message_id)
            return
        elif resp.status_code != 200:
            bot.edit_message_text(f"❌ Ошибка {resp.status_code}: {resp.text[:100]}", m.chat.id, wait.message_id)
            return
        
        result = resp.json()
        if isinstance(result, list) and len(result) > 0:
            text = result[0].get('generated_text', '')
        elif isinstance(result, dict):
            text = result.get('generated_text', str(result))
        else:
            text = str(result)
        
        bot.edit_message_text(text.strip(), m.chat.id, wait.message_id)
        
    except Exception as e:
        bot.edit_message_text(f"💥 {type(e).__name__}", m.chat.id, wait.message_id)

print("🚀 Бот на Hugging Face Spaces запущен!")
bot.infinity_polling()
