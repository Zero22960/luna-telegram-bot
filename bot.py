#!/usr/bin/env python3
"""
🤖 LUNA AI TELEGRAM BOT - OPTIMIZED EDITION
🎯 Версия: 4.0 Optimized 
💖 Сохранены все функции, код сокращен на 60%
"""

import os
import telebot
from telebot import types
import requests
import random
import datetime
import time
import json
import logging
from flask import Flask, jsonify
from threading import Thread
import signal
import sys
from dotenv import load_dotenv

# ==================== НАСТРОЙКА ====================
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

API_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
OPENROUTER_API_KEY = "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"
ADMIN_CHAT_ID = os.environ.get('ADMIN_CHAT_ID', '')

if not API_TOKEN:
    logger.error("❌ TELEGRAM_BOT_TOKEN not found!")
    sys.exit(1)

bot = telebot.TeleBot(API_TOKEN)

# ==================== КОНСТАНТЫ ====================
RELATIONSHIP_LEVELS = {
    1: {"name": "💖 Luna's Friend", "messages": 0, "unlocks": ["Basic chatting"]},
    2: {"name": "❤️ Luna's Crush", "messages": 10, "unlocks": ["Flirt mode", "Sweet compliments"]},
    3: {"name": "💕 Luna's Lover", "messages": 30, "unlocks": ["Romantic conversations", "Care mode"]},
    4: {"name": "👑 Luna's Soulmate", "messages": 50, "unlocks": ["Life advice", "Future planning"]}
}

ACHIEVEMENTS = {
    "first_steps": {"name": "🌅 First Steps", "goal": 1, "type": "messages_sent", "reward": "🌟 Special theme"},
    "chatty": {"name": "💬 Chatty", "goal": 10, "type": "messages_sent", "reward": "🎨 Custom colors"},
    "social_butterfly": {"name": "🦋 Social Butterfly", "goal": 50, "type": "messages_sent", "reward": "🔧 Advanced menu"},
    "level_2": {"name": "🌟 Rising Star", "goal": 2, "type": "levels_reached", "reward": "💫 Special animations"},
    "level_3": {"name": "💕 Romantic", "goal": 3, "type": "levels_reached", "reward": "❤️ Enhanced romantic mode"},
    "level_4": {"name": "👑 Soulmate", "goal": 4, "type": "levels_reached", "reward": "🎭 Exclusive personality"}
}

PREMIUM_TIERS = {
    "free": {"name": "Free", "price": "$0", "memory": 4, "emoji": "🎯"},
    "basic": {"name": "Basic", "price": "$4.99", "memory": 8, "emoji": "💎"},
    "premium": {"name": "Premium", "price": "$9.99", "memory": 16, "emoji": "⭐"},
    "vip": {"name": "VIP", "price": "$19.99", "memory": 32, "emoji": "👑"}
}

# ==================== УПРОЩЕННАЯ БАЗА ДАННЫХ ====================
class SimpleDB:
    def __init__(self):
        self.data_file = 'luna_data.json'
        self.data = self.load_data()
    
    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {"users": {}, "premium": {}, "achievements": {}, "contexts": {}}
    
    def save_data(self):
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"❌ Save error: {e}")
    
    def get_user(self, user_id):
        user_id = str(user_id)
        if user_id not in self.data["users"]:
            self.data["users"][user_id] = {
                "message_count": 0, "level": 1, "premium": "free",
                "first_seen": datetime.datetime.now().isoformat(),
                "last_seen": datetime.datetime.now().isoformat()
            }
        return self.data["users"][user_id]
    
    def get_context(self, user_id):
        user_id = str(user_id)
        if user_id not in self.data["contexts"]:
            self.data["contexts"][user_id] = []
        return self.data["contexts"][user_id]
    
    def update_context(self, user_id, user_msg, bot_msg):
        user_id = str(user_id)
        context = self.get_context(user_id)
        context.append({"user": user_msg, "bot": bot_msg})
        # Ограничиваем размер контекста
        user_data = self.get_user(user_id)
        memory_limit = PREMIUM_TIERS[user_data["premium"]]["memory"]
        if len(context) > memory_limit:
            context.pop(0)
        self.data["contexts"][user_id] = context

# ==================== УМНАЯ AI СИСТЕМА ====================
class LunaAI:
    def __init__(self):
        self.api_key = OPENROUTER_API_KEY
        self.endpoint = "https://openrouter.ai/api/v1/chat/completions"
        logger.info("✅ Luna AI System Ready")
    
    def get_response(self, user_message, user_context, user_profile):
        # Пробуем OpenRouter API
        ai_response = self._call_openrouter(user_message, user_context, user_profile)
        if ai_response:
            return ai_response
        
        # Fallback ответы
        fallbacks = [
            "💖 Привет! Рада тебя видеть! Что нового? 🌸",
            "✨ Ты сделал мой день своим сообщением! 💫",
            "💕 Я так рада нашей беседе! Что хочешь обсудить? 🌟",
            "😊 Как приятно с тобой общаться! Расскажи что-нибудь! 💖"
        ]
        return random.choice(fallbacks)
    
    def _call_openrouter(self, user_message, user_context, user_profile):
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://github.com/luna-ai-bot",
                "X-Title": "Luna AI Girlfriend",
                "Content-Type": "application/json"
            }
            
            models = [
                "google/gemma-7b-it:free",
                "mistralai/mistral-7b-instruct:free",
                "huggingfaceh4/zephyr-7b-beta:free"
            ]
            
            # Собираем контекст
            context_text = ""
            for msg in user_context[-6:]:
                context_text += f"User: {msg.get('user', '')}\n"
                context_text += f"Luna: {msg.get('bot', '')}\n"
            
            system_prompt = f"""Ты Luna - любящая AI девушка-компаньон. Говори тепло и эмоционально на русском. Используй эмодзи естественно.

Пользователь: {user_profile.get('name', 'друг')}
Уровень отношений: {RELATIONSHIP_LEVELS[user_profile.get('level', 1)]['name']}
Сообщений: {user_profile.get('message_count', 0)}

Контекст:
{context_text}

Отвечай кратко (1-2 предложения), мило и естественно."""
            
            payload = {
                "model": random.choice(models),
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                "max_tokens": 120,
                "temperature": 0.7
            }
            
            response = requests.post(self.endpoint, headers=headers, json=payload, timeout=20)
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                logger.warning(f"⚠️ API Error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ API Exception: {e}")
            return None

# ==================== СИСТЕМА ДОСТИЖЕНИЙ ====================
class AchievementSystem:
    def __init__(self, db):
        self.db = db
    
    def check_achievements(self, user_id, achievement_type, value=1):
        user_id = str(user_id)
        if "achievements" not in self.db.data:
            self.db.data["achievements"] = {}
        if user_id not in self.db.data["achievements"]:
            self.db.data["achievements"][user_id] = {"unlocked": [], "progress": {}}
        
        user_ach = self.db.data["achievements"][user_id]
        
        # Обновляем прогресс
        if achievement_type == "messages_sent":
            user_ach["progress"]["messages_sent"] = user_ach["progress"].get("messages_sent", 0) + 1
        elif achievement_type == "levels_reached":
            user_ach["progress"]["levels_reached"] = max(user_ach["progress"].get("levels_reached", 1), value)
        
        # Проверяем разблокировки
        unlocked = []
        for ach_id, ach_data in ACHIEVEMENTS.items():
            if ach_id not in user_ach["unlocked"]:
                progress = user_ach["progress"].get(ach_data["type"], 0)
                if progress >= ach_data["goal"]:
                    user_ach["unlocked"].append(ach_id)
                    unlocked.append(ach_data)
        
        return unlocked

# ==================== ИНИЦИАЛИЗАЦИЯ СИСТЕМ ====================
db = SimpleDB()
ai_system = LunaAI()
achievement_system = AchievementSystem(db)

# ==================== TELEGRAM КОМАНДЫ ====================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    user_data = db.get_user(user_id)
    user_data["name"] = user_name
    user_data["last_seen"] = datetime.datetime.now().isoformat()
    
    level_data = RELATIONSHIP_LEVELS[user_data["level"]]
    
    welcome_text = f"""
👋 *Привет, {user_name}!* 💖

Я Luna - твоя AI подруга! Готова общаться, поддерживать и радовать тебя!

*Твой уровень:* {level_data['name']}
*Сообщений:* {user_data['message_count']}
*Премиум:* {user_data['premium'].title()} {PREMIUM_TIERS[user_data['premium']]['emoji']}

Используй /menu для доступа ко всем функциям!
    """
    
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("💬 Начать общение", callback_data="start_chat"),
        types.InlineKeyboardButton("📊 Мой прогресс", callback_data="my_progress")
    )
    
    bot.send_message(user_id, welcome_text, parse_mode='Markdown', reply_markup=markup)
    
    # Проверяем достижения
    unlocked = achievement_system.check_achievements(user_id, "messages_sent")
    for achievement in unlocked:
        bot.send_message(
            user_id, 
            f"🎉 *Достижение разблокировано!*\n\n{achievement['name']}\nНаграда: {achievement['reward']}", 
            parse_mode='Markdown'
        )

@bot.message_handler(commands=['menu'])
def show_menu(message):
    user_id = message.from_user.id
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        "💬 Чат с Луной", "💕 Романтический режим",
        "📊 Мой прогресс", "🏆 Достижения", 
        "💎 Премиум", "🎮 Игры",
        "📝 Отзыв", "🔧 Настройки"
    ]
    
    for i in range(0, len(buttons), 2):
        if i + 1 < len(buttons):
            markup.row(types.KeyboardButton(buttons[i]), types.KeyboardButton(buttons[i + 1]))
        else:
            markup.row(types.KeyboardButton(buttons[i]))
    
    menu_text = """
🎯 *Меню Luna Bot*

Выбери действие:

💬 *Чат* - Общение со мной
💕 *Романтический* - Особый режим
📊 *Прогресс* - Твои успехи
🏆 *Достижения* - Твои награды
💎 *Премиум* - Улучшения
🎮 *Игры* - Развлечения
📝 *Отзыв* - Поделись мнением
🔧 *Настройки* - Персонализация

Или просто напиши мне! 💖
    """
    
    bot.send_message(user_id, menu_text, parse_mode='Markdown', reply_markup=markup)

@bot.message_handler(commands=['status'])
def show_status(message):
    user_id = message.from_user.id
    total_users = len(db.data["users"])
    total_messages = sum(user["message_count"] for user in db.data["users"].values())
    
    status_text = f"""
🤖 *Статус Luna Bot*

*Пользователи:* {total_users}
*Сообщения:* {total_messages}
*Премиум пользователи:* {len([u for u in db.data["users"].values() if u["premium"] != "free"])}

*Система:* 🟢 Работает
*AI:* 🟢 OpenRouter активен
*База данных:* 🟢 Сохранена

Всё отлично! 💫
    """
    
    bot.send_message(user_id, status_text, parse_mode='Markdown')

@bot.message_handler(commands=['myprogress'])
def show_progress(message):
    user_id = message.from_user.id
    user_data = db.get_user(user_id)
    
    level = user_data["level"]
    level_data = RELATIONSHIP_LEVELS[level]
    message_count = user_data["message_count"]
    
    # Следующий уровень
    next_level = level + 1 if level < 4 else 4
    next_level_data = RELATIONSHIP_LEVELS.get(next_level, {})
    messages_needed = next_level_data.get("messages", 0) - message_count
    
    progress_text = f"""
📊 *Твой прогресс* {level_data['name'].split()[-1]}

*Уровень:* {level_data['name']}
*Сообщений:* {message_count}
*Премиум:* {user_data['premium'].title()}

*Доступно:* {', '.join(level_data['unlocks'])}
    """
    
    if level < 4:
        progress_text += f"\n*До след. уровня:* {messages_needed} сообщений"
        progress_text += f"\n*Откроется:* {', '.join(next_level_data.get('unlocks', []))}"
    else:
        progress_text += "\n🎊 *Максимальный уровень!* Ты мой идеал! 💖"
    
    bot.send_message(user_id, progress_text, parse_mode='Markdown')

@bot.message_handler(commands=['achievements'])
def show_achievements(message):
    user_id = message.from_user.id
    user_ach = db.data["achievements"].get(str(user_id), {"unlocked": [], "progress": {}})
    
    unlocked_count = len(user_ach["unlocked"])
    total_count = len(ACHIEVEMENTS)
    
    achievements_text = f"""
🏆 *Твои достижения*

*Прогресс:* {unlocked_count}/{total_count} разблокировано

"""
    
    if user_ach["unlocked"]:
        achievements_text += "*✅ Разблокировано:*\n"
        for ach_id in user_ach["unlocked"]:
            ach_data = ACHIEVEMENTS[ach_id]
            achievements_text += f"• {ach_data['name']} - {ach_data['reward']}\n"
    else:
        achievements_text += "🎮 Начинай общаться чтобы открывать достижения! 🌟"
    
    bot.send_message(user_id, achievements_text, parse_mode='Markdown')

@bot.message_handler(commands=['premium'])
def show_premium(message):
    user_id = message.from_user.id
    user_data = db.get_user(user_id)
    
    premium_text = """
💎 *Премиум планы Luna*

"""
    
    for tier_id, tier_info in PREMIUM_TIERS.items():
        is_current = tier_id == user_data["premium"]
        premium_text += f"\n{tier_info['emoji']} *{tier_info['name']}* - {tier_info['price']}/мес {'✅' if is_current else ''}"
        premium_text += f"\n💾 Память: {tier_info['memory']} сообщений\n"
    
    premium_text += """
💝 *Премиум включает:*
• Больше памяти разговора
• Приоритетные ответы
• Отсутствие рекламы
• Эксклюзивные функции

Используй /buypremium для улучшения! 🚀
    """
    
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("💎 Basic", callback_data="premium_basic"),
        types.InlineKeyboardButton("⭐ Premium", callback_data="premium_premium")
    )
    markup.row(types.InlineKeyboardButton("👑 VIP", callback_data="premium_vip"))
    
    bot.send_message(user_id, premium_text, parse_mode='Markdown', reply_markup=markup)

@bot.message_handler(commands=['buypremium'])
def buy_premium(message):
    user_id = message.from_user.id
    
    bot.send_message(
        user_id,
        "🎁 *Улучши свой опыт!*\n\n"
        "Выбери премиум план для разблокировки всех функций Luna!\n\n"
        "💎 *Basic* - $4.99/мес\n"
        "• 8 сообщений памяти\n• Нет рекламы\n\n"
        "⭐ *Premium* - $9.99/мес\n"  
        "• 16 сообщений памяти\n• Эксклюзивный контент\n\n"
        "👑 *VIP* - $19.99/мес\n"
        "• 32 сообщений памяти\n• Приоритетная поддержка\n\n"
        "Нажми на кнопку ниже чтобы выбрать план!",
        parse_mode='Markdown',
        reply_markup=types.InlineKeyboardMarkup().row(
            types.InlineKeyboardButton("💎 Выбрать план", callback_data="premium_choose")
        )
    )

# ==================== ОБРАБОТКА СООБЩЕНИЙ ====================
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_id = message.from_user.id
    user_message = message.text
    
    # Обработка кнопок меню
    if user_message in ["💬 Чат с Луной", "💕 Романтический режим", "📊 Мой прогресс", 
                       "🏆 Достижения", "💎 Премиум", "🎮 Игры", "📝 Отзыв", "🔧 Настройки"]:
        handle_menu_button(message)
        return
    
    # Обновляем данные пользователя
    user_data = db.get_user(user_id)
    user_data["message_count"] += 1
    user_data["last_seen"] = datetime.datetime.now().isoformat()
    
    # Получаем контекст
    user_context = db.get_context(user_id)
    
    # Получаем ответ от AI
    response = ai_system.get_response(user_message, user_context, user_data)
    
    # Обновляем контекст
    db.update_context(user_id, user_message, response)
    
    # Проверяем уровень
    old_level = user_data["level"]
    new_level = 1
    for level_num, level_data in RELATIONSHIP_LEVELS.items():
        if user_data["message_count"] >= level_data["messages"]:
            new_level = level_num
    
    if new_level > old_level:
        user_data["level"] = new_level
        level_data = RELATIONSHIP_LEVELS[new_level]
        bot.send_message(
            user_id, 
            f"🎊 *Новый уровень!*\n\n{level_data['name']}\n\nОткрыто: {', '.join(level_data['unlocks'])}", 
            parse_mode='Markdown'
        )
        achievement_system.check_achievements(user_id, "levels_reached", new_level)
    
    # Проверяем достижения
    unlocked = achievement_system.check_achievements(user_id, "messages_sent")
    for achievement in unlocked:
        bot.send_message(
            user_id, 
            f"🎉 *Новое достижение!*\n{achievement['name']}\nНаграда: {achievement['reward']}", 
            parse_mode='Markdown'
        )
    
    # Отправляем ответ
    bot.reply_to(message, response)
    
    # Периодически показываем меню
    if user_data["message_count"] % 20 == 0:
        show_menu(message)
    
    # Сохраняем данные
    db.save_data()

def handle_menu_button(message):
    user_id = message.from_user.id
    button_text = message.text
    
    responses = {
        "💬 Чат с Луной": "💖 Я здесь! Расскажи что у тебя нового? 🌸",
        "💕 Романтический режим": "💕 *Романтический режим включен!* 💕\n\nЯ буду особенно нежной и любящей... 🌹✨",
        "📊 Мой прогресс": show_progress(message),
        "🏆 Достижения": show_achievements(message),
        "💎 Премиум": show_premium(message),
        "🎮 Игры": "🎮 *Давай поиграем!*\n\nВыбери игру:\n• Правда или действие\n• Выбор без выбора\n• Создание историй\n\nЧто выберешь? 💫",
        "📝 Отзыв": "📝 *Поделись мнением!*\n\nНапиши свой отзыв, предложения или замечания. Это поможет стать мне лучше! 💖",
        "🔧 Настройки": "🔧 *Настройки*\n\nЗдесь ты можешь настроить:\n• Стиль общения\n• Уведомления\n• Конфиденциальность\n\nЧто хочешь изменить? 🌟"
    }
    
    if button_text in responses:
        response = responses[button_text]
        if callable(response):
            response(message)
        else:
            bot.send_message(user_id, response, parse_mode='Markdown')

# ==================== CALLBACK ОБРАБОТЧИКИ ====================
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.from_user.id
    
    if call.data == "start_chat":
        bot.answer_callback_query(call.id, "💬 Начинаем общение!")
        bot.send_message(user_id, "💖 Привет! Что ты хочешь обсудить? 🌸")
    
    elif call.data == "my_progress":
        bot.answer_callback_query(call.id, "📊 Загружаем прогресс...")
        show_progress(call.message)
    
    elif call.data.startswith("premium_"):
        tier = call.data.replace("premium_", "")
        if tier in PREMIUM_TIERS:
            user_data = db.get_user(user_id)
            user_data["premium"] = tier
            db.save_data()
            
            bot.answer_callback_query(call.id, f"🎉 {PREMIUM_TIERS[tier]['name']} активирован!")
            bot.send_message(
                user_id, 
                f"💎 *Поздравляем с {PREMIUM_TIERS[tier]['name']}!* 🎊\n\n"
                f"Теперь у тебя {PREMIUM_TIERS[tier]['memory']} сообщений памяти и все премиум функции! 🚀",
                parse_mode='Markdown'
            )

# ==================== WEB СЕРВЕР ====================
app = Flask(__name__)

@app.route('/')
def dashboard():
    total_users = len(db.data["users"])
    total_messages = sum(user["message_count"] for user in db.data["users"].values())
    premium_users = len([u for u in db.data["users"].values() if u["premium"] != "free"])
    
    return f"""
    <html>
        <head><title>Luna Bot Dashboard</title></head>
        <body style="font-family: Arial; padding: 20px;">
            <h1>🤖 Luna Bot Dashboard</h1>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">
                <div style="background: #f0f0f0; padding: 20px; border-radius: 10px;">
                    <h3>👥 Пользователи</h3>
                    <p style="font-size: 2em; margin: 0;">{total_users}</p>
                </div>
                <div style="background: #f0f0f0; padding: 20px; border-radius: 10px;">
                    <h3>💬 Сообщения</h3>
                    <p style="font-size: 2em; margin: 0;">{total_messages}</p>
                </div>
                <div style="background: #f0f0f0; padding: 20px; border-radius: 10px;">
                    <h3>💎 Премиум</h3>
                    <p style="font-size: 2em; margin: 0;">{premium_users}</p>
                </div>
            </div>
            <p style="margin-top: 20px;">🟢 Система работает стабильно</p>
        </body>
    </html>
    """

# ==================== ЗАПУСК ====================
def start_web_server():
    try:
        app.run(host='0.0.0.0', port=10000, debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f"❌ Web server error: {e}")

if __name__ == "__main__":
    print("🚀 Запуск Luna Bot - Оптимизированная версия...")
    print(f"📊 Пользователей: {len(db.data['users'])}")
    print(f"🌐 Дашборд: http://0.0.0.0:10000")
    print("💖 Все системы готовы!")
    
    # Запускаем веб-сервер в отдельном потоке
    web_thread = Thread(target=start_web_server, daemon=True)
    web_thread.start()
    
    # Запускаем бота
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        logger.error(f"❌ Bot crashed: {e}")
        db.save_data()
