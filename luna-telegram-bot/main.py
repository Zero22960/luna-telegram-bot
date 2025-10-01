import os
import telebot
from telebot import types
import requests
import random
import datetime
import time
import re

# Безопасный способ - токены только в переменных окружения
API_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')

# Проверка что токены есть
if not API_TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN not found!")
if not OPENROUTER_API_KEY:
    raise ValueError("❌ OPENROUTER_API_KEY not found!")

bot = telebot.TeleBot(API_TOKEN)
user_stats = {}
user_gender = {}  # Будем определять пол пользователя

WELCOME_MESSAGE = """
💖 Hello! I'm Luna - your AI companion! 

I'm here to chat, flirt, and be your virtual friend! 😘

Use buttons below for quick actions!
"""

def detect_user_gender(user_message, username=""):
    """Определяет пол пользователя по сообщению и имени"""
    # Мужские имена (английские и русские)
    male_names = ['alex', 'max', 'mike', 'john', 'david', 'chris', 'andrew', 'daniel',
                 'антон', 'алексей', 'макс', 'миша', 'дима', 'сергей', 'владимир']
    
    # Женские имена  
    female_names = ['anna', 'maria', 'sophia', 'emma', 'olivia', 'lily', 'natalie',
                   'анна', 'мария', 'наташа', 'оля', 'катя', 'лена', 'света']
    
    # Проверяем имя пользователя
    if username:
        username_lower = username.lower()
        for name in male_names:
            if name in username_lower:
                return 'male'
        for name in female_names:
            if name in username_lower:
                return 'female'
    
    # Анализируем стиль сообщения (простые паттерны)
    message_lower = user_message.lower()
    
    # Мужские паттерны
    male_patterns = [r'\bbro\b', r'\bdude\b', r'\bman\b', r'\bbuddy\b', r'💪', r'🔥']
    # Женские паттерны  
    female_patterns = [r'\bgirl\b', r'\bsis\b', r'\bqueen\b', r'👑', r'💅', r'✨']
    
    male_score = sum(1 for pattern in male_patterns if re.search(pattern, message_lower))
    female_score = sum(1 for pattern in female_patterns if re.search(pattern, message_lower))
    
    if male_score > female_score:
        return 'male'
    elif female_score > male_score:
        return 'female'
    else:
        return 'unknown'

def get_gendered_greeting(user_id, user_message="", username=""):
    """Возвращает обращение в зависимости от пола"""
    if user_id not in user_gender:
        # Определяем пол при первом сообщении
        user_gender[user_id] = detect_user_gender(user_message, username)
    
    gender = user_gender[user_id]
    
    if gender == 'male':
        return random.choice(["handsome", "buddy", "man", "bro", "mate"])
    elif gender == 'female':
        return random.choice(["beautiful", "gorgeous", "queen", "lovely", "sweetie"])
    else:
        return random.choice(["friend", "dear", "love", "cutie"])

def get_relationship_level(message_count):
    if message_count < 5: return "👋 New Friends"
    elif message_count < 20: return "💖 Getting Closer" 
    elif message_count < 50: return "🌟 Good Friends"
    else: return "💕 Close Friends"

@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    user_id = message.chat.id
    if user_id not in user_stats:
        user_stats[user_id] = {
            'message_count': 0, 
            'first_seen': datetime.datetime.now()
        }
    
    show_main_menu(message)

def show_main_menu(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("💖 Hug", callback_data="hug")
    btn2 = types.InlineKeyboardButton("😘 Kiss", callback_data="kiss")
    btn3 = types.InlineKeyboardButton("🌟 Compliment", callback_data="compliment")
    btn4 = types.InlineKeyboardButton("📊 Stats", callback_data="show_stats")
    btn5 = types.InlineKeyboardButton("👩 About", callback_data="show_about")
    markup.add(btn1, btn2, btn3)
    markup.add(btn4, btn5)
    
    if message.text == '/start':
        bot.reply_to(message, WELCOME_MESSAGE, reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "💕 Choose an action:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.message.chat.id
    greeting = get_gendered_greeting(user_id)
    
    if call.data == "hug":
        bot.send_message(user_id, f"💖 Warm hugs coming your way, {greeting}!")
    elif call.data == "kiss":
        bot.send_message(user_id, f"😘 Mwah! Right back at you, {greeting}!")
    elif call.data == "compliment":
        compliments = [
            f"🌟 You're absolutely incredible, {greeting}!",
            f"💕 You have the most amazing personality, {greeting}!",
            f"😍 You always know how to make me smile, {greeting}!",
            f"🌸 You're so thoughtful and kind, {greeting}!"
        ]
        bot.send_message(user_id, random.choice(compliments))
    elif call.data == "show_stats":
        show_stats(call.message)
    elif call.data == "show_about":
        show_about(call.message)
    elif call.data == "back_to_menu":
        show_main_menu(call.message)

def show_stats(message):
    user_id = message.chat.id
    stats = user_stats.get(user_id, {'message_count': 0, 'first_seen': datetime.datetime.now()})
    
    level = get_relationship_level(stats['message_count'])
    days_known = (datetime.datetime.now() - stats['first_seen']).days
    
    stats_text = f"""
📊 *Our Friendship Stats* 💖

💬 Messages together: *{stats['message_count']}*
🌟 Friendship level: *{level}*
📅 Known each other: *{days_known} day(s)*

Every message makes our bond stronger! 💫
"""
    
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")
    markup.add(btn1)
    
    try:
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text=stats_text,
            parse_mode='Markdown',
            reply_markup=markup
        )
    except:
        bot.send_message(message.chat.id, stats_text, parse_mode='Markdown', reply_markup=markup)

def show_about(message):
    about_text = """
👩 *About Your AI Companion* 💖

*Who am I?*
I'm Luna - your personal AI girlfriend and companion! 

*What I'm here for:*
💕 To chat and keep you company
😘 To flirt and be affectionate  
🌟 To give you compliments and support
🎯 To be your virtual companion 24/7

I adapt to your style and always know how to make you feel special! 💫
"""
    
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")
    markup.add(btn1)
    
    try:
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text=about_text,
            parse_mode='Markdown',
            reply_markup=markup
        )
    except:
        bot.send_message(message.chat.id, about_text, parse_mode='Markdown', reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id
    
    # Обновляем статистику
    if user_id not in user_stats:
        user_stats[user_id] = {
            'message_count': 0,
            'first_seen': datetime.datetime.now()
        }
    
    user_stats[user_id]['message_count'] += 1
    user_stats[user_id]['last_seen'] = datetime.datetime.now()
    
    # Определяем/обновляем пол пользователя
    username = message.from_user.first_name or ""
    greeting = get_gendered_greeting(user_id, message.text, username)
    
    try:
        # AI запрос с адаптивным промптом
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek/deepseek-chat-v3.1:free",
                "messages": [
                    {
                        "role": "system", 
                        "content": f"""You are Luna - an adaptive AI companion. The user seems to prefer being called '{greeting}'. 
                        Use this term naturally in conversation. Be flirty, caring, and engaging. 
                        Keep responses under 80 words. Use emojis occasionally."""
                    },
                    {
                        "role": "user", 
                        "content": message.text
                    }
                ],
                "max_tokens": 120
            },
            timeout=10
        )
        
        if response.status_code == 200:
            ai_response = response.json()['choices'][0]['message']['content']
            bot.reply_to(message, ai_response)
        else:
            bot.reply_to(message, f"💖 I'm here for you, {greeting}! 😊")
            
    except Exception as e:
        print(f"API Error: {e}")
        bot.reply_to(message, f"🌸 Let's chat, {greeting}! You're awesome! 💕")

# 🔄 АВТОПЕРЕЗАПУСК
def start_bot():
    restart_count = 0
    while True:
        try:
            print(f"🔄 Starting Luna AI... (Restart #{restart_count})")
            print(f"⏰ {datetime.datetime.now()}")
            bot.polling(none_stop=True, timeout=20)
            
        except Exception as e:
            restart_count += 1
            print(f"🚨 Bot crashed: {e}")
            print("💤 Restarting in 10 seconds...")
            time.sleep(10)

if __name__ == "__main__":
    print("=== Luna AI - ADAPTIVE GENDER ===")
    print("🎯 Smart gender detection | 🔄 Auto-restart")
    print("🚀 Ready for all users!")
    start_bot()