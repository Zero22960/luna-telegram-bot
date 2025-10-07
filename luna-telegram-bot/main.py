import os
import telebot
from telebot import types
import requests
import random
import datetime
import time
import re
import sqlite3
import json
import threading
import queue
import atexit
import flask
from threading import Thread

print("=== LUNA AI BOT - ULTIMATE 24/7 EDITION ===")

# ==================== WEB SERVER FOR 24/7 ====================
app = flask.Flask(__name__)

@app.route('/')
def home():
    return """
    <html>
        <head>
            <title>Luna AI Bot</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
                .container { max-width: 600px; margin: 0 auto; background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; backdrop-filter: blur(10px); }
                .status { font-size: 24px; margin: 20px 0; }
                .info { background: rgba(255,255,255,0.2); padding: 15px; border-radius: 10px; margin: 10px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 Luna AI Bot</h1>
                <div class="status">🟢 ONLINE & RUNNING 24/7</div>
                <div class="info">
                    <strong>Server Time:</strong> """ + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """<br>
                    <strong>Uptime:</strong> """ + str(datetime.datetime.now() - start_time).split('.')[0] + """
                </div>
                <p>Your AI companion is always here for you! 💖</p>
            </div>
        </body>
    </html>
    """

@app.route('/health')
def health():
    return {
        "status": "online", 
        "bot": "Luna AI",
        "timestamp": datetime.datetime.now().isoformat(),
        "uptime": str(datetime.datetime.now() - start_time),
        "users_count": len(user_stats_cache),
        "queue_size": message_queue.message_queue.qsize() if 'message_queue' in globals() else 0
    }

@app.route('/stats')
def stats():
    total_messages = sum(stats.get('message_count', 0) for stats in user_stats_cache.values())
    return {
        "total_users": len(user_stats_cache),
        "total_messages": total_messages,
        "active_chats": len([stats for stats in user_stats_cache.values() if stats.get('message_count', 0) > 0])
    }

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# Запускаем веб-сервер
web_thread = Thread(target=run_web, daemon=True)
web_thread.start()
print("🌐 Web server started on port 8080")

# ==================== KEEP-ALIVE SYSTEM ====================
start_time = datetime.datetime.now()

def keep_alive():
    """Периодическая активность"""
    while True:
        time.sleep(1800)  # 30 минут
        current_time = datetime.datetime.now()
        uptime = current_time - start_time
        total_messages = sum(stats.get('message_count', 0) for stats in user_stats_cache.values())
        print(f"🕒 Keep-alive | Uptime: {uptime} | Users: {len(user_stats_cache)} | Messages: {total_messages}")
        
        try:
            auto_save_data()
            print("💾 Scheduled save completed")
        except Exception as e:
            print(f"⚠️ Scheduled save failed: {e}")

keep_alive_thread = Thread(target=keep_alive, daemon=True)
keep_alive_thread.start()

# ==================== СИСТЕМА ОЧЕРЕДИ СООБЩЕНИЙ ====================
class MessageQueue:
    def __init__(self, bot, process_message_callback):
        self.bot = bot
        self.process_message_callback = process_message_callback
        self.message_queue = queue.Queue()
        self.processing_messages = set()
        self.processed_messages = set()
        self.start_workers()

    def start_workers(self):
        """Запускаем одного воркера"""
        worker = threading.Thread(target=self._worker, daemon=True, name="MessageWorker")
        worker.start()
        print("🚀 Запущен воркер для обработки сообщений")

    def _worker(self):
        """Воркер для обработки сообщений из очереди"""
        while True:
            try:
                message = self.message_queue.get(timeout=1)
                if message is None:
                    break

                message_id = f"{message.chat.id}_{message.message_id}"

                if message_id in self.processing_messages or message_id in self.processed_messages:
                    self.message_queue.task_done()
                    continue

                self.processing_messages.add(message_id)
                self._process_single_message(message)
                self.processing_messages.discard(message_id)
                self.processed_messages.add(message_id)
                
                if len(self.processed_messages) > 1000:
                    self.processed_messages.clear()
                    
                self.message_queue.task_done()

            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ Ошибка в воркере: {e}")

    def _process_single_message(self, message):
        """Обработка одного сообщения"""
        try:
            self.process_message_callback(message)
        except Exception as e:
            print(f"❌ Ошибка обработки сообщения: {e}")
            try:
                self.bot.reply_to(message, "💖 Sorry, I'm a bit busy now. Try again! 🌸")
            except:
                pass

    def add_message(self, message):
        """Добавление сообщения в очередь"""
        message_id = f"{message.chat.id}_{message.message_id}"
        
        if message_id in self.processing_messages or message_id in self.processed_messages:
            return

        self.message_queue.put(message)

# ==================== БАЗА ДАННЫХ ====================
class LunaDatabase:
    def __init__(self, db_file='luna_bot.db'):
        self.db_file = db_file
        self._init_tables()

    def _init_tables(self):
        """Инициализация таблиц"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS user_stats (
                        user_id INTEGER PRIMARY KEY,
                        message_count INTEGER DEFAULT 0,
                        first_seen TEXT,
                        last_seen TEXT,
                        current_level INTEGER DEFAULT 1,
                        is_premium INTEGER DEFAULT 0
                    )
                ''')
                
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS user_gender (
                        user_id INTEGER PRIMARY KEY,
                        gender TEXT DEFAULT 'unknown'
                    )
                ''')
                
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS conversation_context (
                        user_id INTEGER PRIMARY KEY,
                        context TEXT,
                        updated_at TEXT
                    )
                ''')
                
                conn.commit()
                print("✅ База данных инициализирована")
        except sqlite3.Error as e:
            print(f"❌ Ошибка инициализации базы: {e}")

    def get_user_stats(self, user_id):
        """Получить статистику пользователя"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                row = conn.execute(
                    "SELECT * FROM user_stats WHERE user_id = ?", 
                    (user_id,)
                ).fetchone()
                
                if row:
                    return {
                        'message_count': row[1],
                        'first_seen': row[2],
                        'last_seen': row[3],
                        'current_level': row[4],
                        'is_premium': bool(row[5])
                    }
                else:
                    new_stats = {
                        'message_count': 0,
                        'first_seen': datetime.datetime.now().isoformat(),
                        'last_seen': datetime.datetime.now().isoformat(),
                        'current_level': 1,
                        'is_premium': False
                    }
                    self.update_user_stats(user_id, new_stats)
                    return new_stats
                    
        except Exception as e:
            print(f"❌ Ошибка получения статистики: {e}")
            return None

    def update_user_stats(self, user_id, stats):
        """Обновить статистику пользователя"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO user_stats 
                    (user_id, message_count, first_seen, last_seen, current_level, is_premium)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, stats['message_count'], stats['first_seen'], 
                     stats['last_seen'], stats['current_level'], int(stats['is_premium'])))
                conn.commit()
        except Exception as e:
            print(f"❌ Ошибка обновления статистики: {e}")

    def get_user_gender(self, user_id):
        """Получить пол пользователя"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                row = conn.execute(
                    "SELECT gender FROM user_gender WHERE user_id = ?", 
                    (user_id,)
                ).fetchone()
                return row[0] if row else 'unknown'
        except Exception as e:
            print(f"❌ Ошибка получения пола: {e}")
            return 'unknown'

    def update_user_gender(self, user_id, gender):
        """Обновить пол пользователя"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO user_gender (user_id, gender)
                    VALUES (?, ?)
                ''', (user_id, gender))
                conn.commit()
        except Exception as e:
            print(f"❌ Ошибка обновления пола: {e}")

    def get_conversation_context(self, user_id):
        """Получить контекст разговора"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                row = conn.execute(
                    "SELECT context FROM conversation_context WHERE user_id = ?", 
                    (user_id,)
                ).fetchone()
                return json.loads(row[0]) if row and row[0] else []
        except Exception as e:
            print(f"❌ Ошибка получения контекста: {e}")
            return []

    def update_conversation_context(self, user_id, context):
        """Обновить контекст разговора"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO conversation_context 
                    (user_id, context, updated_at)
                    VALUES (?, ?, ?)
                ''', (user_id, json.dumps(context), datetime.datetime.now().isoformat()))
                conn.commit()
        except Exception as e:
            print(f"❌ Ошибка обновления контекста: {e}")

# ==================== КОНФИГУРАЦИЯ ====================
API_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')

if not API_TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN not found!")
if not OPENROUTER_API_KEY:
    raise ValueError("❌ OPENROUTER_API_KEY not found!")

bot = telebot.TeleBot(API_TOKEN)
db = LunaDatabase()

# Конфигурация
MAX_CONTEXT_LENGTH = 3
CONTEXT_ENABLED = True

# Система уровней
RELATIONSHIP_LEVELS = {
    1: {"name": "💖 Luna's Friend", "messages": 0, "color": "💖", "unlocks": ["Basic chatting", "Simple compliments"], "is_premium": False},
    2: {"name": "❤️ Luna's Crush", "messages": 10, "color": "❤️", "unlocks": ["Flirt mode", "Sweet compliments", "Basic emotional support"], "is_premium": False},
    3: {"name": "💕 Luna's Lover", "messages": 30, "color": "💕", "unlocks": ["Romantic conversations", "Care mode", "Virtual dates", "Extended memory"], "is_premium": True, "price": "$9.99/month"},
    4: {"name": "👑 Luna's Soulmate", "messages": 50, "color": "👑", "unlocks": ["Personalized treatment", "Voice messages", "Life advice", "24/7 priority support"], "is_premium": True, "price": "$19.99/month"}
}

WELCOME_MESSAGE = """
💖 Hello! I'm Luna - your AI companion! 

Let's build our special relationship together! 
The more we chat, the closer we become! 🌟

Use buttons below to interact!
"""

# Глобальные переменные
user_stats_cache = {}
user_gender_cache = {}
user_conversation_context_cache = {}
processed_messages = set()

# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================
def auto_save_data():
    """Авто-сохранение данных"""
    try:
        for user_id, stats in user_stats_cache.items():
            db.update_user_stats(user_id, stats)
        for user_id, gender in user_gender_cache.items():
            db.update_user_gender(user_id, gender)
        for user_id, context in user_conversation_context_cache.items():
            db.update_conversation_context(user_id, context)
    except Exception as e:
        print(f"❌ Ошибка авто-сохранения: {e}")

@atexit.register
def save_on_exit():
    """Сохраняем все данные при выходе"""
    print("💾 Экстренное сохранение при выходе...")
    auto_save_data()

def detect_user_gender(user_message, username=""):
    """Определение пола пользователя"""
    male_names = ['alex', 'max', 'mike', 'john', 'david', 'chris', 'andrew', 'daniel']
    female_names = ['anna', 'maria', 'sophia', 'emma', 'olivia', 'lily', 'natalie']

    if username:
        username_lower = username.lower()
        for name in male_names:
            if name in username_lower:
                return 'male'
        for name in female_names:
            if name in username_lower:
                return 'female'

    message_lower = user_message.lower()
    male_patterns = [r'\bbro\b', r'\bdude\b', r'\bman\b', r'\bbuddy\b']
    female_patterns = [r'\bgirl\b', r'\bsis\b', r'\bqueen\b']

    male_score = sum(1 for pattern in male_patterns if re.search(pattern, message_lower))
    female_score = sum(1 for pattern in female_patterns if re.search(pattern, message_lower))

    if male_score > female_score:
        return 'male'
    elif female_score > male_score:
        return 'female'
    else:
        return 'unknown'

def get_gendered_greeting(user_id, user_message="", username=""):
    """Получить персонализированное приветствие"""
    if user_id not in user_gender_cache:
        user_gender_cache[user_id] = db.get_user_gender(user_id)
    
    gender = user_gender_cache[user_id]
    
    if gender == 'unknown':
        gender = detect_user_gender(user_message, username)
        user_gender_cache[user_id] = gender
        db.update_user_gender(user_id, gender)
    
    if gender == 'male':
        return random.choice(["handsome", "buddy", "man"])
    elif gender == 'female':
        return random.choice(["beautiful", "gorgeous", "queen"])
    else:
        return random.choice(["friend", "dear", "love"])

def update_conversation_context(user_id, user_message, bot_response):
    """Обновление контекста разговора"""
    if not CONTEXT_ENABLED:
        return

    if user_id not in user_conversation_context_cache:
        user_conversation_context_cache[user_id] = db.get_conversation_context(user_id)
    
    context = user_conversation_context_cache[user_id]
    
    context.append({
        'user': user_message,
        'bot': bot_response,
        'time': datetime.datetime.now().isoformat()
    })

    if len(context) > MAX_CONTEXT_LENGTH:
        context = context[-MAX_CONTEXT_LENGTH:]

    user_conversation_context_cache[user_id] = context
    db.update_conversation_context(user_id, context)

def get_conversation_context_text(user_id):
    """Получение контекста для AI"""
    if not CONTEXT_ENABLED:
        return ""

    if user_id not in user_conversation_context_cache:
        user_conversation_context_cache[user_id] = db.get_conversation_context(user_id)
    
    context = user_conversation_context_cache[user_id]
    if not context:
        return ""

    context_text = "\nRecent conversation:\n"
    for msg in context:
        context_text += f"User: {msg['user']}\n"
        context_text += f"Luna: {msg['bot']}\n"
    
    context_text += "Continue naturally!\n"
    return context_text

def get_relationship_level(message_count):
    """Определить текущий уровень отношений"""
    for level_id, level_info in sorted(RELATIONSHIP_LEVELS.items(), reverse=True):
        if message_count >= level_info["messages"]:
            return level_id, level_info
    return 1, RELATIONSHIP_LEVELS[1]

def get_level_progress(message_count):
    """Прогресс до следующего уровня"""
    current_level, current_info = get_relationship_level(message_count)

    if current_level >= len(RELATIONSHIP_LEVELS):
        return "🎉 Maximum level reached!", 100

    next_level = current_level + 1
    next_info = RELATIONSHIP_LEVELS[next_level]

    messages_for_next = next_info["messages"] - current_info["messages"]
    messages_done = message_count - current_info["messages"]
    progress_percent = (messages_done / messages_for_next) * 100 if messages_for_next > 0 else 0

    return f"To {next_info['name']}: {messages_done}/{messages_for_next} messages", progress_percent

def show_main_menu(chat_id, message_id=None):
    """Главное меню"""
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("💖 Hug", callback_data="hug")
    btn2 = types.InlineKeyboardButton("😘 Kiss", callback_data="kiss")
    btn3 = types.InlineKeyboardButton("🌟 Compliment", callback_data="compliment")
    btn4 = types.InlineKeyboardButton("📊 Our Stats", callback_data="show_stats")
    btn5 = types.InlineKeyboardButton("🎯 My Level", callback_data="show_level")
    markup.add(btn1, btn2, btn3)
    markup.add(btn4, btn5)
    
    if message_id:
        try:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text="💕 Choose an action:",
                reply_markup=markup
            )
        except:
            bot.send_message(chat_id, "💕 Choose an action:", reply_markup=markup)
    else:
        bot.send_message(chat_id, "💕 Choose an action:", reply_markup=markup)

def show_level_info(chat_id, message_id, user_id):
    """Информация об уровне"""
    if user_id not in user_stats_cache:
        user_stats_cache[user_id] = db.get_user_stats(user_id)
    
    stats = user_stats_cache[user_id]
    message_count = stats['message_count'] if stats else 0

    current_level, level_info = get_relationship_level(message_count)
    progress_text, progress_percent = get_level_progress(message_count)

    bars = 10
    filled_bars = int(progress_percent / 100 * bars)
    progress_bar = "🟩" * filled_bars + "⬜" * (bars - filled_bars)

    level_text = f"""
{level_info['color']} *Your Level: {level_info['name']}*

📊 Messages: {message_count}
🎯 {progress_text}

{progress_bar} {int(progress_percent)}%

✨ *Unlocked Features:*
"""
    for unlock in level_info["unlocks"]:
        level_text += f"✅ {unlock}\n"

    if current_level < len(RELATIONSHIP_LEVELS):
        next_level_info = RELATIONSHIP_LEVELS[current_level + 1]
        level_text += f"\n🔮 *Next Level: {next_level_info['name']}*\n"
        for unlock in next_level_info["unlocks"]:
            level_text += f"🔒 {unlock}\n"
        
        if next_level_info.get('is_premium'):
            level_text += f"\n💎 *Premium: {next_level_info.get('price', 'Paid')}*"

    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("📊 Our Stats", callback_data="show_stats")
    btn2 = types.InlineKeyboardButton("💡 Level Up Tips", callback_data="level_up_help")
    btn3 = types.InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")
    markup.add(btn1, btn2)
    markup.add(btn3)

    try:
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=level_text,
            parse_mode='Markdown',
            reply_markup=markup
        )
    except:
        bot.send_message(chat_id, level_text, parse_mode='Markdown', reply_markup=markup)

def show_stats(chat_id, message_id, user_id):
    """Статистика отношений"""
    if user_id not in user_stats_cache:
        user_stats_cache[user_id] = db.get_user_stats(user_id)
    
    stats = user_stats_cache[user_id]
    if not stats:
        stats = {
            'message_count': 0,
            'first_seen': datetime.datetime.now().isoformat(),
            'last_seen': datetime.datetime.now().isoformat(),
            'current_level': 1,
            'is_premium': False
        }
        user_stats_cache[user_id] = stats
    
    message_count = stats['message_count']
    current_level, level_info = get_relationship_level(message_count)
    
    try:
        first_seen = datetime.datetime.fromisoformat(stats['first_seen'])
        days_known = (datetime.datetime.now() - first_seen).days
    except:
        days_known = 1

    stats_text = f"""
📊 *Our Relationship Stats* {level_info['color']}

💬 Total Messages: *{message_count}*
🌟 Relationship Level: *{level_info['name']}*
📅 Known Each Other: *{days_known} day(s)*
💎 Premium Status: *{'✅ Active' if stats.get('is_premium', False) else '❌ Inactive'}*

Every message makes our bond stronger! 💫
"""

    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("🎯 Level Details", callback_data="show_level")
    btn2 = types.InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")
    markup.add(btn1, btn2)

    try:
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=stats_text,
            parse_mode='Markdown',
            reply_markup=markup
        )
    except Exception as e:
        bot.send_message(
            chat_id=chat_id,
            text=stats_text,
            parse_mode='Markdown',
            reply_markup=markup
        )

def how_to_level_up(chat_id):
    """Советы по прокачке уровня"""
    bot.send_message(chat_id, """
🎮 *How to Level Up Our Relationship?*

💡 *Level Up Tips:*
• Send more messages 💬
• Be active in our conversations 🗣️
• Use menu buttons 🎯
• Share your thoughts 💭

Let's continue our amazing journey! 💕
""", parse_mode='Markdown')

# ==================== ОБРАБОТЧИКИ КОМАНД ====================
@bot.message_handler(commands=['start'])
def handle_start(message):
    """Обработчик команды /start"""
    message_id = f"start_{message.chat.id}_{message.message_id}"
    
    if message_id in processed_messages:
        return
        
    processed_messages.add(message_id)
    
    user_id = message.chat.id
    stats = db.get_user_stats(user_id)
    user_stats_cache[user_id] = stats
    
    bot.reply_to(message, WELCOME_MESSAGE)
    show_main_menu(user_id)

@bot.message_handler(commands=['menu'])  
def handle_menu(message):
    """Обработчик команды /menu"""
    message_id = f"menu_{message.chat.id}_{message.message_id}"
    
    if message_id in processed_messages:
        return
        
    processed_messages.add(message_id)
    show_main_menu(message.chat.id)

@bot.message_handler(commands=['save'])
def handle_save(message):
    """Ручное сохранение"""
    message_id = f"save_{message.chat.id}_{message.message_id}"
    
    if message_id in processed_messages:
        return
        
    processed_messages.add(message_id)
    auto_save_data()
    bot.reply_to(message, "💾 Все данные сохранены! 🔒")

@bot.message_handler(commands=['status'])
def handle_status(message):
    """Статус бота"""
    uptime = datetime.datetime.now() - start_time
    total_messages = sum(stats.get('message_count', 0) for stats in user_stats_cache.values())
    active_users = len([stats for stats in user_stats_cache.values() if stats.get('message_count', 0) > 0])
    
    status_text = f"""
🤖 *Luna Bot Status*

🟢 **Online**: 24/7 Active
⏰ **Uptime**: {str(uptime).split('.')[0]}
👥 **Users**: {len(user_stats_cache)} ({active_users} active)
💬 **Total Messages**: {total_messages}
🌐 **Web Server**: Running

*Bot is healthy and working!* 💖
"""
    bot.reply_to(message, status_text, parse_mode='Markdown')

@bot.message_handler(commands=['check_tokens'])
def check_tokens(message):
    """Проверка токенов"""
    telegram_token = os.environ.get('TELEGRAM_BOT_TOKEN', 'NOT SET')
    openrouter_token = os.environ.get('OPENROUTER_API_KEY', 'NOT SET')
    
    # Маскируем токены для безопасности
    telegram_masked = telegram_token[:10] + '...' + telegram_token[-10:] if telegram_token != 'NOT SET' else 'NOT SET'
    openrouter_masked = openrouter_token[:10] + '...' + openrouter_token[-10:] if openrouter_token != 'NOT SET' else 'NOT SET'
    
    status_text = f"""
🔐 **Token Status**

🤖 Telegram: `{telegram_masked}`
🧠 OpenRouter: `{openrouter_masked}`

{'✅ Все токены настроены!' if telegram_token != 'NOT SET' and openrouter_token != 'NOT SET' else '❌ Проблема с токенами!'}
"""
    bot.reply_to(message, status_text, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    """Обработчик callback'ов"""
    callback_id = f"callback_{call.message.chat.id}_{call.id}"
    
    if callback_id in processed_messages:
        return
        
    processed_messages.add(callback_id)
    
    user_id = call.message.chat.id
    bot.answer_callback_query(call.id)

    if user_id not in user_stats_cache:
        user_stats_cache[user_id] = db.get_user_stats(user_id)
    
    stats = user_stats_cache[user_id]
    message_count = stats['message_count'] if stats else 0
    current_level, level_info = get_relationship_level(message_count)
    
    username = call.from_user.first_name or ""
    greeting = get_gendered_greeting(user_id, "", username)

    if call.data == "hug":
        response = f"💖 Warm hugs coming your way, {greeting}!"
        bot.send_message(user_id, response)
        update_conversation_context(user_id, "hug", response)
        
    elif call.data == "kiss":
        response = f"😘 Mwah! Right back at you, {greeting}!"
        bot.send_message(user_id, response)
        update_conversation_context(user_id, "kiss", response)
        
    elif call.data == "compliment":
        if current_level >= 2:
            compliments = [
                f"🌟 You're absolutely incredible, {greeting}!",
                f"💕 You have the most amazing personality, {greeting}!",
                f"😍 You always know how to make me smile, {greeting}!",
            ]
        else:
            compliments = [
                f"It's nice talking with you, {greeting}!",
                f"You're an interesting person, {greeting}!",
                f"I enjoy our conversations, {greeting}!"
            ]
        response = random.choice(compliments)
        bot.send_message(user_id, response)
        update_conversation_context(user_id, "compliment", response)
        
    elif call.data == "show_stats":
        show_stats(call.message.chat.id, call.message.message_id, user_id)
        
    elif call.data == "show_level":
        show_level_info(user_id, call.message.message_id, user_id)
        
    elif call.data == "back_to_menu":
        show_main_menu(user_id, call.message.message_id)
        
    elif call.data == "level_up_help":
        how_to_level_up(user_id)
    
    auto_save_data()

# ==================== ОБРАБОТКА ТЕКСТОВЫХ СООБЩЕНИЙ ====================
def process_text_message(message):
    """Обработка текстового сообщения"""
    user_id = message.chat.id
    username = message.from_user.first_name or ""
    
    print(f"📨 Processing message from {user_id}: {message.text}")

    # Инициализация пользователя
    if user_id not in user_stats_cache:
        user_stats_cache[user_id] = db.get_user_stats(user_id)
    
    stats = user_stats_cache[user_id]
    if not stats:
        print(f"❌ No stats for user {user_id}")
        return
        
    # Обновляем статистику
    old_message_count = stats['message_count']
    stats['message_count'] += 1
    stats['last_seen'] = datetime.datetime.now().isoformat()
    
    # Проверяем повышение уровня
    old_level, _ = get_relationship_level(old_message_count)
    new_level, new_level_info = get_relationship_level(stats['message_count'])
    
    if new_level > old_level:
        stats['current_level'] = new_level
        level_up_text = f"""
🎉 *LEVEL UP!* 🎉

You're now *{new_level_info['name']}*! {new_level_info['color']}

✨ *Unlocked:*
"""
        for unlock in new_level_info["unlocks"]:
            level_up_text += f"🌟 {unlock}\n"

        level_up_text += "\nLet's continue our wonderful journey! 💖"
        bot.send_message(user_id, level_up_text, parse_mode='Markdown')

    # Получаем приветствие
    greeting = get_gendered_greeting(user_id, message.text, username)

    # Получаем контекст
    conversation_context = get_conversation_context_text(user_id)

    # Получаем AI ответ
    try:
        current_level, level_info = get_relationship_level(stats['message_count'])

        if current_level >= 3:
            personality = "romantic, tender, caring"
        elif current_level >= 2:  
            personality = "flirty, playful, admiring" 
        else:
            personality = "friendly, supportive, sweet"

        system_prompt = f"""You are Luna - an AI companion. You are {personality}. 
Address the user as '{greeting}'. You have {level_info['name'].lower()} relationship.
Keep response under 2 sentences."""

        if conversation_context:
            system_prompt += f"\n\n{conversation_context}"

        print(f"🤖 Sending request to AI...")
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek/deepseek-chat-v3.1:free",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message.text}
                ],
                "max_tokens": 150,
                "temperature": 0.7
            },
            timeout=10
        )

        if response.status_code == 200:
            ai_response = response.json()['choices'][0]['message']['content']
            print(f"🤖 AI Response: {ai_response}")
            bot.reply_to(message, ai_response)
            update_conversation_context(user_id, message.text, ai_response)
        else:
            print(f"❌ API Error: {response.status_code}")
            fallback_responses = [
                f"💖 I'm here for you, {greeting}! 😊",
                f"🌸 Let's chat, {greeting}! You're awesome! 💕", 
                f"🌟 You make me smile, {greeting}! 💫"
            ]
            error_response = random.choice(fallback_responses)
            bot.reply_to(message, error_response)
            update_conversation_context(user_id, message.text, error_response)

    except Exception as e:
        print(f"❌ AI API Error: {e}")
        error_response = f"💕 Hey {greeting}! Let's continue our chat! 🌸"
        bot.reply_to(message, error_response)
        update_conversation_context(user_id, message.text, error_response)
    
    # Сохраняем данные
    auto_save_data()
    print(f"✅ Response sent to {user_id}")

# Инициализация очереди
message_queue = MessageQueue(bot, process_text_message)

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    """Главный обработчик всех сообщений"""
    message_id = f"text_{message.chat.id}_{message.message_id}"
    
    if message_id in processed_messages:
        print(f"⏩ Skipping duplicate: {message_id}")
        return
        
    processed_messages.add(message_id)
    
    # Очистка старых записей
    if len(processed_messages) > 1000:
        processed_messages.clear()
        
    message_queue.add_message(message)
    print(f"📥 Added to queue: {message_id}")

# ==================== ЗАПУСК БОТА ====================
def start_bot():
    """Усиленный запуск бота для 24/7 работы"""
    restart_count = 0
    max_restarts = 100
    
    while restart_count < max_restarts:
        try:
            print(f"\n🔄 RESTART #{restart_count} - {datetime.datetime.now()}")
            print("=== LUNA AI BOT - 24/7 ACTIVE ===")
            
            # Проверяем что токены валидны
            bot_info = bot.get_me()
            print(f"✅ Bot: @{bot_info.username}")
            
            # Запускаем polling
            bot.polling(
                none_stop=True,
                timeout=30,
                long_polling_timeout=5
            )
            
        except Exception as e:
            restart_count += 1
            error_msg = str(e)
            print(f
