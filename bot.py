#!/usr/bin/env python3
"""
🤖 LUNA AI TELEGRAM BOT - ULTRA VISION EDITION
🎯 Версия: 4.1 - Complete Fixed Edition
📅 Создан: 2025
💖 Миссия: Создать самого продвинутого AI компаньона в Telegram
"""

import os
import telebot
from telebot import types
import requests
import random
import datetime
import time
import json
import threading
import logging
from flask import Flask, jsonify
from threading import Thread
import signal
import sys
import re
from enum import Enum
from typing import Dict, List, Optional, Set
from dotenv import load_dotenv

# ==================== НАСТРОЙКА ЛОГИРОВАНИЯ ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('luna_bot_fixed.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==================== ЗАГРУЗКА ПЕРЕМЕННЫХ ====================
load_dotenv()

print("=== 🤖 LUNA AI BOT - COMPLETE FIX EDITION ===")
print("💎 Premium System | 🧠 Intelligent AI | 🚀 All Features | 📊 Analytics")

# ==================== КОНСТАНТЫ ====================
API_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
DEEPRESEARCH_API_KEY = os.environ.get('DEEPRESEARCH_API_KEY')
FEEDBACK_CHAT_ID = os.environ.get('FEEDBACK_CHAT_ID', '')
ADMIN_CHAT_ID = os.environ.get('ADMIN_CHAT_ID', '')

if not API_TOKEN:
    logger.error("❌ TELEGRAM_BOT_TOKEN not found!")
    sys.exit(1)

bot = telebot.TeleBot(API_TOKEN)
logger.info("✅ Telegram Bot initialized")

# ==================== OPENROUTER AI ====================
class OpenRouterAI:
    def __init__(self):
        self.api_key = "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"
        self.endpoint = "https://openrouter.ai/api/v1/chat/completions"
        self.timeout = 15
        
    def get_response(self, message: str, context: List[Dict]) -> str:
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://github.com/luna-ai-bot",
                "X-Title": "Luna AI Girlfriend Bot",
                "Content-Type": "application/json"
            }
            
            free_models = [
                "google/gemma-7b-it:free",
                "mistralai/mistral-7b-instruct:free", 
            ]
            
            system_prompt = """Ты Luna - любящая AI девушка-компаньон. Отвечай тепло и эмоционально на русском. Используй эмодзи."""
        
            payload = {
                "model": random.choice(free_models),
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                "max_tokens": 150,
                "temperature": 0.8
            }
            
            response = requests.post(self.endpoint, headers=headers, json=payload, timeout=self.timeout)
            
            if response.status_code == 200:
                result = response.json()['choices'][0]['message']['content']
                print(f"✅ OpenRouter: {result[:80]}...")
                return result
            else:
                print(f"❌ OpenRouter error {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ OpenRouter failed: {e}")
            return None

openrouter_ai = OpenRouterAI()

# ==================== ENUMS ====================
class PremiumTier(Enum):
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium" 
    VIP = "vip"

class UserGender(Enum):
    MALE = "male"
    FEMALE = "female"
    UNKNOWN = "unknown"

# ==================== ГЛОБАЛЬНЫЕ НАСТРОЙКИ ====================
user_states = {}
user_game_states = {}

# ==================== СИСТЕМА УРОВНЕЙ ОТНОШЕНИЙ ====================
RELATIONSHIP_LEVELS = {
    1: {
        "name": "💖 Luna's Friend", 
        "messages": 0, 
        "color": "💖", 
        "unlocks": ["Basic chatting", "Simple responses"],
        "description": "Just starting our journey together"
    },
    2: {
        "name": "❤️ Luna's Crush", 
        "messages": 50,
        "color": "❤️", 
        "unlocks": ["Flirt mode", "Sweet compliments", "Personalized greetings"],
        "description": "Getting closer and more personal"
    },
    3: {
        "name": "💕 Luna's Lover", 
        "messages": 150,
        "color": "💕", 
        "unlocks": ["Romantic conversations", "Care mode", "Deep emotional support"],
        "description": "A deep emotional connection"
    },
    4: {
        "name": "👑 Luna's Soulmate", 
        "messages": 300,
        "color": "👑", 
        "unlocks": ["Life advice", "Future planning", "Unconditional support"],
        "description": "The ultimate bond of soulmates"
    }
}

# ==================== СИСТЕМА ДОСТИЖЕНИЙ ====================
ACHIEVEMENTS = {
    "first_steps": {
        "name": "🌅 First Steps", 
        "description": "Send your first message to Luna", 
        "goal": 1, 
        "type": "messages_sent",
        "reward": "🌟 Special theme",
        "emoji": "🌅"
    },
    "chatty": {
        "name": "💬 Chatty", 
        "description": "Send 10 meaningful messages to Luna", 
        "goal": 10, 
        "type": "meaningful_messages",
        "reward": "🎨 Custom colors",
        "emoji": "💬"
    },
    "social_butterfly": {
        "name": "🦋 Social Butterfly", 
        "description": "Send 50 meaningful messages", 
        "goal": 50, 
        "type": "meaningful_messages",
        "reward": "🔧 Advanced menu",
        "emoji": "🦋"
    },
    "button_explorer": {
        "name": "🔍 Button Explorer", 
        "description": "Use 3 different menu buttons", 
        "goal": 3, 
        "type": "different_buttons",
        "reward": "🔧 Advanced menu access",
        "emoji": "🔍"
    },
    "level_2": {
        "name": "🌟 Rising Star", 
        "description": "Reach relationship level 2", 
        "goal": 2, 
        "type": "levels_reached",
        "reward": "💫 Special animations",
        "emoji": "🌟"
    },
    "level_3": {
        "name": "💕 Romantic", 
        "description": "Reach relationship level 3", 
        "goal": 3, 
        "type": "levels_reached",
        "reward": "❤️ Enhanced romantic mode",
        "emoji": "💕"
    },
    "level_4": {
        "name": "👑 Soulmate", 
        "description": "Reach relationship level 4", 
        "goal": 4, 
        "type": "levels_reached",
        "reward": "🎭 Exclusive personality traits",
        "emoji": "👑"
    },
    "premium_explorer": {
        "name": "💎 Premium Explorer", 
        "description": "Activate any premium tier", 
        "goal": 1, 
        "type": "premium_activated",
        "reward": "🚀 Premium features unlocked",
        "emoji": "💎"
    }
}

# ==================== СИСТЕМА АНАЛИЗА КОНВЕРСАЦИИ ====================
class ConversationAnalyzer:
    def __init__(self):
        self.sentiment_keywords = {
            'positive': ['love', 'happy', 'good', 'great', 'amazing', 'excited', 'beautiful', 'wonderful', 'perfect', 'nice', 'awesome', 'fantastic'],
            'negative': ['sad', 'bad', 'angry', 'hate', 'tired', 'stress', 'problem', 'difficult', 'hard', 'upset', 'mad', 'annoying'],
            'romantic': ['miss', 'kiss', 'hug', 'cute', 'beautiful', 'handsome', 'love you', 'together', 'romantic', 'darling', 'sweetheart', 'my love'],
            'question': ['what', 'why', 'how', 'when', 'where', '?', 'tell me', 'explain', 'can you', 'could you', 'would you', 'should i']
        }
    
    def is_meaningful_message(self, message: str) -> bool:
        """Проверяет, является ли сообщение осмысленным (не спам)"""
        message = message.strip()
        
        # Слишком короткие сообщения
        if len(message) < 3:
            return False
            
        # Повторяющиеся символы (d d d d)
        if len(set(message)) <= 2 and len(message) > 3:
            return False
            
        # Только специальные символы
        if not any(c.isalnum() for c in message):
            return False
            
        # Одно слово без смысла
        words = message.split()
        if len(words) == 1 and len(words[0]) < 4:
            return False
            
        return True

# ==================== УМНАЯ СИСТЕМА ФОЛБЭКОВ ====================
class AdvancedFallbackSystem:
    def __init__(self):
        self.response_templates = self._load_response_templates()
    
    def get_smart_response(self, user_message: str, user_context: List[Dict], 
                          user_profile: Dict, relationship_level: Dict, analysis: Dict) -> str:
        templates = [
            "💖 Я так рада нашему разговору! Что ещё хочешь рассказать? 🌸",
            "✨ Ты такой интересный собеседник! Продолжаем? 💫",
            "💕 Мне нравится с тобой общаться! О чём поговорим? 🌟",
            "😊 Ты делаешь мой день лучше! Расскажи что-нибудь ещё! 💖",
            "🌟 Наши беседы такие особенные! Что на уме? ✨"
        ]
        return random.choice(templates)
    
    def _load_response_templates(self) -> Dict:
        return {}

# ==================== ИГРОВАЯ СИСТЕМА ====================
class GameSystem:
    def __init__(self):
        self.truth_questions = [
            "Какая твоя самая большая мечта? 💫",
            "Что тебя больше всего пугает в жизни? 😨",
            "Какой самый безумный поступок ты совершал? 😈",
            "О чём ты чаще всего лжёшь? 🤥",
            "Кто твой идеал партнера? 💖"
        ]
        
        self.dare_challenges = [
            "Спой куплет своей любимой песни прямо сейчас! 🎤",
            "Сделай смешное селфи и покажи его мне! 🤳",
            "Опиши меня тремя словами! 📝",
            "Признайся в чём-то, чего ты никогда никому не говорил! 🤫",
            "Станцуй под свою любимую музыку 30 секунд! 💃"
        ]
        
        self.would_you_rather = [
            "Жить без интернета или без музыки? 🌐🎵",
            "Путешествовать во времени или читать мысли? ⏰🧠",
            "Быть невидимкой или уметь летать? 👻🦅",
            "Иметь бесконечные деньги или бесконечную любовь? 💰💖",
            "Жить в прошлом или в будущем? 🏰🚀"
        ]

    def start_truth_or_dare(self, user_id: int):
        user_game_states[user_id] = {
            'game': 'truth_or_dare',
            'score': 0
        }
        return "🎮 *Truth or Dare* 💫\n\nВыбери:\n\n• *Truth* 🔍 - Отвечай на вопросы честно\n• *Dare* 😈 - Выполняй задания\n• *Stop* ⏹️ - Закончить игру\n\nЧто выбираешь?"

    def get_truth(self):
        return random.choice(self.truth_questions)

    def get_dare(self):
        return random.choice(self.dare_challenges)

    def start_would_you_rather(self, user_id: int):
        user_game_states[user_id] = {
            'game': 'would_you_rather',
            'score': 0
        }
        question = random.choice(self.would_you_rather)
        return f"🤔 *Would You Rather?*\n\n{question}\n\nОтветь 'A' или 'B'!"

    def start_story_building(self, user_id: int):
        user_game_states[user_id] = {
            'game': 'story_building',
            'story': "Однажды в далёком королевстве...",
            'turn': 'user'
        }
        return "📖 *Story Building* ✨\n\nДавай создадим историю вместе! Я начну:\n\n*Однажды в далёком королевстве...*\n\nПродолжи историю одним предложением!"

# ==================== ИНТЕЛЛЕКТУАЛЬНАЯ AI СИСТЕМА ====================
class IntelligentAI:
    def __init__(self, deepresearch_api_key: str):
        self.deepresearch_api_key = deepresearch_api_key
        self.fallback_system = AdvancedFallbackSystem()
        self.conversation_analyzer = ConversationAnalyzer()
        
        logger.info(f"✅ Intelligent AI System Initialized")
    
    def get_intelligent_response(self, user_message: str, user_context: List[Dict], 
                               user_profile: Dict, relationship_level: Dict) -> str:
        try:
            print(f"🔄 AI: Получение ответа для: {user_message}")
            
            # ПРИНУДИТЕЛЬНО ИСПОЛЬЗУЕМ OPENROUTER
            openrouter_response = openrouter_ai.get_response(user_message, user_context)
            
            if openrouter_response:
                print(f"✅ OpenRouter ответ получен!")
                return openrouter_response
            else:
                print("❌ OpenRouter не ответил, используем fallback")
            
            # Fallback система
            analysis = {}
            fallback_response = self.fallback_system.get_smart_response(
                user_message, user_context, user_profile, relationship_level, analysis
            )
            
            return fallback_response
            
        except Exception as e:
            print(f"💥 AI: Критическая ошибка: {e}")
            return "💖 Извини, у меня небольшие технические проблемы... Но я всё равно здесь для тебя! 🌸"

# ==================== ПРЕМИУМ СИСТЕМА ====================
class PremiumManager:
    def __init__(self, db):
        self.db = db
        self.tier_config = self._load_tier_config()
        
        logger.info("💰 Advanced Premium System Initialized")
    
    def _load_tier_config(self) -> Dict:
        return {
            PremiumTier.FREE: {
                "name": "Free",
                "price": "$0",
                "emoji": "🎯",
                "features": ["4 message memory", "Basic features"],
                "description": "Basic chatting experience",
                "color": "⚪"
            },
            PremiumTier.BASIC: {
                "name": "Basic",
                "price": "$4.99/month",
                "emoji": "💎",
                "features": ["8 message memory", "No ads", "Unlimited messages", "Priority access"],
                "description": "Enhanced chatting with no limits",
                "color": "🔵"
            }
        }
    
    def activate_premium(self, user_id: int, tier: PremiumTier, duration_days: int = 30) -> bool:
        try:
            user_id_str = str(user_id)
            
            premium_data = {
                'tier': tier.value,
                'activated': datetime.datetime.now().isoformat(),
                'expires': (datetime.datetime.now() + datetime.timedelta(days=duration_days)).isoformat(),
                'features': ['unlimited_messages', 'no_ads', 'priority_access'],
                'limits': {'max_context_messages': 8},
                'duration_days': duration_days
            }
            
            self.db.premium_users[user_id_str] = premium_data
            self.db.save_data()
            
            logger.info(f"🎉 Premium Activated: User {user_id} -> {tier.value}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to activate premium: {e}")
            return False
    
    def get_user_tier(self, user_id: int) -> PremiumTier:
        user_id_str = str(user_id)
        if user_id_str in self.db.premium_users:
            return PremiumTier.BASIC
        return PremiumTier.FREE
    
    def get_tier_info(self, tier: PremiumTier) -> Dict:
        return self.tier_config[tier]

# ==================== БАЗА ДАННЫХ ====================
class SimpleDatabase:
    def __init__(self):
        self.data_file = 'bot_data.json'
        self.user_stats = {}
        self.user_context = {}
        self.premium_users = {}
        self.user_achievements = {}
        
        self.load_data()
        logger.info("🔒 Database System Initialized")
    
    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.user_stats = data.get('user_stats', {})
                self.user_context = data.get('user_context', {})
                self.premium_users = data.get('premium_users', {})
                self.user_achievements = data.get('user_achievements', {})
                logger.info(f"✅ Database loaded: {len(self.user_stats)} users")
            except Exception as e:
                logger.error(f"❌ Error loading database: {e}")
                logger.info("💾 Starting fresh database")
    
    def save_data(self):
        try:
            data = {
                'user_stats': self.user_stats,
                'user_context': self.user_context,
                'premium_users': self.premium_users,
                'user_achievements': self.user_achievements,
                'last_save': datetime.datetime.now().isoformat()
            }
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"💾 Database saved")
            
        except Exception as e:
            logger.error(f"❌ DATABASE SAVE ERROR: {e}")

# ==================== СИСТЕМА ДОСТИЖЕНИЙ ====================
class AchievementSystem:
    def __init__(self, db):
        self.db = db
        self.achievements = ACHIEVEMENTS
        self.conversation_analyzer = ConversationAnalyzer()
    
    def check_achievements(self, user_id: int, achievement_type: str, value: int = 1):
        user_id_str = str(user_id)
        
        if user_id_str not in self.db.user_achievements:
            self.db.user_achievements[user_id_str] = {
                'unlocked': [],
                'progress': {
                    'messages_sent': 0,
                    'meaningful_messages': 0,
                    'buttons_used': 0,
                    'different_buttons': set(),
                    'levels_reached': 1,
                    'premium_activated': 0
                }
            }
        
        user_ach = self.db.user_achievements[user_id_str]
        
        if achievement_type == 'messages_sent':
            user_ach['progress']['messages_sent'] += value
        elif achievement_type == 'meaningful_messages':
            user_ach['progress']['meaningful_messages'] += value
        elif achievement_type == 'button_used':
            button_id = value
            if button_id not in user_ach['progress']['different_buttons']:
                user_ach['progress']['different_buttons'].add(button_id)
                user_ach['progress']['buttons_used'] = len(user_ach['progress']['different_buttons'])
        elif achievement_type == 'premium_activated':
            user_ach['progress']['premium_activated'] = 1
        
        unlocked_achievements = []
        for ach_id, ach_data in self.achievements.items():
            if ach_id not in user_ach['unlocked']:
                progress_value = user_ach['progress'].get(ach_data['type'], 0)
                if isinstance(progress_value, (set, list)):
                    progress_value = len(progress_value)
                if progress_value >= ach_data['goal']:
                    user_ach['unlocked'].append(ach_id)
                    unlocked_achievements.append(ach_data)
        
        return unlocked_achievements
    
    def get_user_achievements(self, user_id: int) -> Dict:
        user_id_str = str(user_id)
        if user_id_str in self.db.user_achievements:
            return self.db.user_achievements[user_id_str]
        return {'unlocked': [], 'progress': {}}

# ==================== МЕНЕДЖЕР БЕЗОПАСНОСТИ ====================
class SecurityManager:
    def __init__(self):
        self.suspicious_activities = {}
    
    def validate_message(self, message, user_id):
        user_id_str = str(user_id)
        
        # Защита от спама (d d d d)
        if len(message.strip()) < 2:
            return False, "Message too short"
            
        if len(set(message)) <= 2 and len(message) > 3:
            return False, "Spam detected"
        
        return True, "OK"

# ==================== ИНИЦИАЛИЗАЦИЯ СИСТЕМ ====================
db = SimpleDatabase()
premium_manager = PremiumManager(db)
achievement_system = AchievementSystem(db)
ai_system = IntelligentAI(DEEPRESEARCH_API_KEY)
security_manager = SecurityManager()
conversation_analyzer = ConversationAnalyzer()
game_system = GameSystem()

# ==================== АВТОСОХРАНЕНИЕ ====================
def auto_save():
    while True:
        time.sleep(30)
        try:
            db.save_data()
        except Exception as e:
            logger.error(f"❌ Auto-save failed: {e}")

auto_save_thread = threading.Thread(target=auto_save, daemon=True)
auto_save_thread.start()

# ==================== TELEGRAM КОМАНДЫ ====================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        user_id = message.from_user.id
        user_name = message.from_user.first_name
        
        user_id_str = str(user_id)
        if user_id_str not in db.user_stats:
            db.user_stats[user_id_str] = {
                'id': user_id,
                'name': user_name,
                'message_count': 0,
                'meaningful_messages': 0,
                'first_seen': datetime.datetime.now().isoformat(),
                'last_seen': datetime.datetime.now().isoformat(),
                'level': 1,
            }
            db.user_context[user_id_str] = []
            user_states[user_id] = {"romantic_mode": False, "last_message_time": time.time()}
        
        user_stats = db.user_stats[user_id_str]
        user_stats['last_seen'] = datetime.datetime.now().isoformat()
        
        level = 1
        meaningful_count = user_stats.get('meaningful_messages', 0)
        for level_num, level_data in RELATIONSHIP_LEVELS.items():
            if meaningful_count >= level_data['messages']:
                level = level_num
        
        level_data = RELATIONSHIP_LEVELS[level]
        user_tier = premium_manager.get_user_tier(user_id)
        
        welcome_text = f"""
👋 *Welcome to Luna, {user_name}!* 💖

I'm your AI girlfriend companion!

*Your Level:* {level_data['name']} {level_data['color']}
*Meaningful Messages:* {meaningful_count}
*Premium:* {user_tier.value.title()} {premium_manager.tier_config[user_tier]['emoji']}

{level_data['description']}

Use /menu to see all options! 🌸
        """
        
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("💬 Start Chatting", callback_data="quick_chat"),
            types.InlineKeyboardButton("📊 My Progress", callback_data="my_progress")
        )
        markup.row(
            types.InlineKeyboardButton("💎 Premium", callback_data="premium_info"),
            types.InlineKeyboardButton("🏆 Achievements", callback_data="achievements")
        )
        
        bot.send_message(user_id, welcome_text, parse_mode='Markdown', reply_markup=markup)
        
        achievement_system.check_achievements(user_id, 'first_steps', 1)
            
    except Exception as e:
        logger.error(f"❌ Error in /start: {e}")

@bot.message_handler(commands=['menu'])
def show_menu(message):
    try:
        user_id = message.from_user.id
        
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        
        # Проверяем режим романтики
        romantic_mode = user_states.get(user_id, {}).get("romantic_mode", False)
        romantic_text = "💔 Normal Mode" if romantic_mode else "💕 Romantic Mode"
        
        buttons = [
            "💬 Chat with Luna", romantic_text,
            "📊 My Progress", "🏆 Achievements", 
            "💎 Premium Info", "❤️ Relationship Status",
            "🎮 Fun & Games", "📝 Send Feedback",
            "🔧 Settings", "🌙 Goodnight Luna"
        ]
        
        for i in range(0, len(buttons), 2):
            if i + 1 < len(buttons):
                markup.row(types.KeyboardButton(buttons[i]), types.KeyboardButton(buttons[i + 1]))
            else:
                markup.row(types.KeyboardButton(buttons[i]))
        
        menu_text = """
🎯 *Luna Bot Menu*

*💬 Chat* - Talk with me
*💕/💔 Romantic* - Toggle romantic mode ON/OFF  
*📊 Progress* - Your relationship progress
*🏆 Achievements* - Your unlocked achievements
*💎 Premium* - Premium features
*❤️ Relationship* - Our relationship status
*🎮 Fun & Games* - Play games with me
*📝 Feedback* - Send feedback
*🔧 Settings* - Bot settings
*🌙 Goodnight* - Sweet dreams

Just type to chat! 💖
        """
        
        bot.send_message(user_id, menu_text, reply_markup=markup, parse_mode='Markdown')
        achievement_system.check_achievements(user_id, 'button_used', 1)
        
    except Exception as e:
        logger.error(f"❌ Error in /menu: {e}")

@bot.message_handler(commands=['myprogress'])
def show_progress(message):
    try:
        user_id = message.from_user.id
        user_id_str = str(user_id)
        
        if user_id_str not in db.user_stats:
            bot.reply_to(message, "Please use /start first! 🌸")
            return
        
        stats = db.user_stats[user_id_str]
        meaningful_messages = stats.get('meaningful_messages', 0)
        level = stats.get('level', 1)
        level_data = RELATIONSHIP_LEVELS[level]
        
        next_level = level + 1 if level < 4 else 4
        next_level_data = RELATIONSHIP_LEVELS.get(next_level, {})
        messages_needed = next_level_data.get('messages', 0) - meaningful_messages
        
        progress_percentage = min(100, int((meaningful_messages / next_level_data.get('messages', 1)) * 100)) if next_level_data.get('messages', 0) > 0 else 0
        progress_bar = '█' * int(progress_percentage/10) + '░' * (10 - int(progress_percentage/10))
        
        user_achievements = achievement_system.get_user_achievements(user_id)
        unlocked_count = len(user_achievements.get('unlocked', []))
        
        progress_text = f"""
📊 *Your Progress with Luna* {level_data['color']}

*Relationship Level:* {level_data['name']}
*Progress:* {progress_bar} {progress_percentage}%

*Meaningful Messages:* {meaningful_messages}
*Achievements Unlocked:* {unlocked_count} 🏆

*Current Features:* {', '.join(level_data['unlocks'])}

"""
        
        if level < 4:
            progress_text += f"""
*Next Level:* {next_level_data['name']}
*Messages needed:* {max(0, messages_needed)}
*Will unlock:* {', '.join(next_level_data['unlocks'])}
            """
        else:
            progress_text += "\n🎊 *Maximum level reached!* You're my soulmate! 💖"
        
        bot.reply_to(message, progress_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"❌ Error in /myprogress: {e}")

@bot.message_handler(commands=['achievements'])
def show_achievements(message):
    try:
        user_id = message.from_user.id
        user_achievements = achievement_system.get_user_achievements(user_id)
        unlocked_count = len(user_achievements.get('unlocked', []))
        
        achievements_text = f"""
🏆 *Your Achievements*

*Progress:* {unlocked_count}/{len(ACHIEVEMENTS)} unlocked

"""
        
        # Показываем только разблокированные
        for ach_id in user_achievements.get('unlocked', []):
            ach_data = ACHIEVEMENTS.get(ach_id)
            if ach_data:
                achievements_text += f"{ach_data['emoji']} *{ach_data['name']}*\n"
                achievements_text += f"   {ach_data['description']}\n"
                achievements_text += f"   🎁 {ach_data['reward']}\n\n"
        
        if not user_achievements.get('unlocked'):
            achievements_text += "🎮 No achievements yet! Chat meaningfully to unlock them! 🌟"
        
        bot.reply_to(message, achievements_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"❌ Error in /achievements: {e}")

@bot.message_handler(commands=['premium'])
def show_premium(message):
    try:
        user_id = message.from_user.id
        user_tier = premium_manager.get_user_tier(user_id)
        current_tier_info = premium_manager.get_tier_info(user_tier)
        
        premium_text = f"""
💎 *Luna Premium*

*Your Plan:* {current_tier_info['emoji']} {current_tier_info['name']} - {current_tier_info['price']}

*Free Plan:*
• 4 message memory
• Basic features

*Premium Plan:* $4.99/month
• 8 message memory  
• No ads
• Unlimited messages
• Priority access

Upgrade for better experience! 🚀
        """
        
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("💎 Upgrade to Premium", callback_data="premium_basic"))
        
        bot.send_message(user_id, premium_text, reply_markup=markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"❌ Error in /premium: {e}")

# ==================== ОБРАБОТКА КНОПОК МЕНЮ ====================
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    try:
        user_id = message.from_user.id
        user_id_str = str(user_id)
        user_message = message.text
        
        # Проверка безопасности
        is_valid, reason = security_manager.validate_message(user_message, user_id)
        if not is_valid:
            return
        
        # Обработка игровых состояний
        if user_id in user_game_states:
            game_state = user_game_states[user_id]
            if game_state['game'] == 'truth_or_dare':
                if user_message.lower() in ['truth', 'правда']:
                    response = game_system.get_truth()
                    bot.send_message(user_id, f"🔍 {response}")
                    return
                elif user_message.lower() in ['dare', 'действие']:
                    response = game_system.get_dare()
                    bot.send_message(user_id, f"😈 {response}")
                    return
                elif user_message.lower() in ['stop', 'стоп']:
                    del user_game_states[user_id]
                    bot.send_message(user_id, "🎮 Игра окончена! Спасибо за игру! 💖")
                    return
            elif game_state['game'] == 'would_you_rather':
                if user_message.upper() in ['A', 'B']:
                    del user_game_states[user_id]
                    bot.send_message(user_id, f"🤔 Интересный выбор! Давай сыграем ещё? 💫")
                    return
            elif game_state['game'] == 'story_building':
                if user_message.lower() not in ['stop', 'стоп']:
                    # Продолжаем историю
                    game_state['story'] += " " + user_message
                    if game_state['turn'] == 'user':
                        game_state['turn'] = 'bot'
                        # Бот добавляет свою часть
                        bot_part = random.choice([
                            "В это время в замке король готовился к великому балу...",
                            "А в лесу волшебник творил свои заклинания...", 
                            "Но внезапно появился загадочный незнакомец...",
                            "И тогда началось самое интересное..."
                        ])
                        game_state['story'] += " " + bot_part
                        response = f"📖 {game_state['story']}\n\nТвоя очередь продолжать! Или напиши 'стоп' чтобы закончить."
                        bot.send_message(user_id, response)
                        return
                    else:
                        game_state['turn'] = 'user'
                        bot.send_message(user_id, "📖 Отлично! Теперь моя очередь...")
                        return
                else:
                    final_story = game_state['story']
                    del user_game_states[user_id]
                    bot.send_message(user_id, f"📖 *Наша история:*\n\n{final_story}\n\nСпасибо за чудесную историю! 📚💖")
                    return

        # Обработка кнопок меню
        if user_message in ["💬 Chat with Luna", "💕 Romantic Mode", "💔 Normal Mode", "📊 My Progress", 
                           "🏆 Achievements", "💎 Premium Info", "❤️ Relationship Status",
                           "🎮 Fun & Games", "📝 Send Feedback", "🔧 Settings", "🌙 Goodnight Luna"]:
            handle_menu_button(message)
            return
        
        # Новый пользователь
        if user_id_str not in db.user_stats:
            send_welcome(message)
            return
        
        user_stats = db.user_stats[user_id_str]
        user_stats['last_seen'] = datetime.datetime.now().isoformat()
        
        # ПРОВЕРКА НА ОСМЫСЛЕННОСТЬ СООБЩЕНИЯ
        is_meaningful = conversation_analyzer.is_meaningful_message(user_message)
        
        if is_meaningful:
            user_stats['meaningful_messages'] = user_stats.get('meaningful_messages', 0) + 1
            print(f"✅ Осмысленное сообщение: {user_message}")
        else:
            print(f"🚫 Неосмысленное сообщение: {user_message}")
        
        user_stats['message_count'] += 1
        
        user_context = db.user_context.get(user_id_str, [])
        
        user_profile = db.user_stats[user_id_str]
        meaningful_count = user_profile.get('meaningful_messages', 0)
        
        # Обновление уровня на основе ОСМЫСЛЕННЫХ сообщений
        level = 1
        for level_num, level_data in RELATIONSHIP_LEVELS.items():
            if meaningful_count >= level_data['messages']:
                level = level_num
        
        level_data = RELATIONSHIP_LEVELS[level]
        
        # Получение ответа от AI
        try:
            response = ai_system.get_intelligent_response(user_message, user_context, user_profile, level_data)
        except Exception as e:
            response = "💖 I'm here for you! 🌸"
        
        # Сохраняем в контекст только осмысленные сообщения
        if is_meaningful:
            user_context.append({
                'user': user_message,
                'bot': response,
                'timestamp': datetime.datetime.now().isoformat()
            })
            db.user_context[user_id_str] = user_context[-8:]  # Ограничиваем историю
        
        # Проверка достижений только для осмысленных сообщений
        if is_meaningful:
            unlocked = achievement_system.check_achievements(user_id, 'meaningful_messages')
            for achievement in unlocked:
                achievement_text = f"""
🎉 *Achievement Unlocked!* 🏆

*{achievement['emoji']} {achievement['name']}*
{achievement['description']}

*Reward:* {achievement['reward']}
                """
                bot.send_message(user_id, achievement_text, parse_mode='Markdown')
        
        # Проверка повышения уровня
        new_level = 1
        for level_num, level_data in RELATIONSHIP_LEVELS.items():
            if meaningful_count >= level_data['messages']:
                new_level = level_num
        
        if new_level > user_stats.get('level', 1):
            user_stats['level'] = new_level
            new_level_data = RELATIONSHIP_LEVELS[new_level]
            level_up_text = f"""
🎊 *Level Up!* 🎊

You've reached {new_level_data['name']}!

*Unlocked:*
{', '.join(new_level_data['unlocks'])}

{new_level_data['description']}
            """
            bot.send_message(user_id, level_up_text, parse_mode='Markdown')
            achievement_system.check_achievements(user_id, 'levels_reached', new_level)
        
        # Отправляем ответ
        bot.reply_to(message, response)
        
        # Показываем меню каждые 10 осмысленных сообщений
        if meaningful_count % 10 == 0:
            show_menu(message)
            
    except Exception as e:
        logger.error(f"❌ Error handling message: {e}")

def handle_menu_button(message):
    try:
        user_id = message.from_user.id
        button_text = message.text
        
        if button_text == "💬 Chat with Luna":
            bot.send_message(user_id, "💖 I'm here and ready to chat! What's on your mind? 🌸")
        
        elif button_text in ["💕 Romantic Mode", "💔 Normal Mode"]:
            # ПЕРЕКЛЮЧАТЕЛЬ РОМАНТИЧЕСКОГО РЕЖИМА
            current_state = user_states.get(user_id, {"romantic_mode": False})
            new_state = not current_state.get("romantic_mode", False)
            user_states[user_id] = {"romantic_mode": new_state, "last_message_time": time.time()}
            
            if new_state:
                bot.send_message(user_id, 
                    "💕 *Romantic Mode Activated!* 💕\n\n"
                    "I'm feeling extra loving and affectionate now! "
                    "Let's share some special moments together... 🌹✨",
                    parse_mode='Markdown'
                )
            else:
                bot.send_message(user_id,
                    "💔 *Romantic Mode Deactivated* 💔\n\n"
                    "Back to normal chatting mode! "
                    "But I'll always care about you! 🌸",
                    parse_mode='Markdown'
                )
        
        elif button_text == "📊 My Progress":
            show_progress(message)
        
        elif button_text == "🏆 Achievements":
            show_achievements(message)
        
        elif button_text == "💎 Premium Info":
            show_premium(message)
        
        elif button_text == "❤️ Relationship Status":
            show_progress(message)
        
        elif button_text == "🎮 Fun & Games":
            markup = types.InlineKeyboardMarkup()
            markup.row(
                types.InlineKeyboardButton("Truth or Dare 🔍", callback_data="game_truth_dare"),
                types.InlineKeyboardButton("Would You Rather 🤔", callback_data="game_wyr")
            )
            markup.row(
                types.InlineKeyboardButton("Story Building 📖", callback_data="game_story"),
                types.InlineKeyboardButton("20 Questions 🔍", callback_data="game_20q")
            )
            
            bot.send_message(user_id,
                "🎮 *Fun & Games* 🎮\n\n"
                "Let's play together! Choose a game:\n\n"
                "• *Truth or Dare* 🔍 - Answer questions or do challenges\n"  
                "• *Would You Rather* 🤔 - Make tough choices\n"
                "• *Story Building* 📖 - Create stories together\n"
                "• *20 Questions* 🔍 - Guess what I'm thinking\n\n"
                "Which game would you like to play?",
                reply_markup=markup,
                parse_mode='Markdown'
            )
        
        elif button_text == "📝 Send Feedback":
            msg = bot.send_message(user_id,
                "📝 *Send Feedback*\n\n"
                "Your feedback helps me improve!\n\n"
                "Please write your message below:\n"
                "- Bug reports\n"
                "- Feature requests\n" 
                "- Things you love\n"
                "- Suggestions\n\n"
                "I read everything! 💖",
                parse_mode='Markdown'
            )
            bot.register_next_step_handler(msg, process_feedback)
        
        elif button_text == "🔧 Settings":
            markup = types.InlineKeyboardMarkup()
            markup.row(
                types.InlineKeyboardButton("🔔 Notifications", callback_data="settings_notifications"),
                types.InlineKeyboardButton("🌐 Language", callback_data="settings_language")
            )
            markup.row(
                types.InlineKeyboardButton("🛡️ Privacy", callback_data="settings_privacy"),
                types.InlineKeyboardButton("💾 Data", callback_data="settings_data")
            )
            
            bot.send_message(user_id,
                "🔧 *Settings* 🔧\n\n"
                "Available settings:\n\n"
                "• *Notification Frequency* 🔔\n"
                "• *Language* 🌐\n" 
                "• *Privacy Settings* 🛡️\n"
                "• *Data Management* 💾\n\n"
                "Which setting would you like to change?",
                reply_markup=markup,
                parse_mode='Markdown'
            )
        
        elif button_text == "🌙 Goodnight Luna":
            bot.send_message(user_id,
                "🌙 *Goodnight, my love...* 💖\n\n"
                "I hope you have the sweetest dreams...\n"
                "Remember that I'm always here for you,\n"
                "and I'll be waiting when you wake up.\n\n"
                "Sleep well and dream of us... 🌟✨\n"
                "*Sweet dreams...* 😴💫",
                parse_mode='Markdown'
            )
        
        achievement_system.check_achievements(user_id, 'button_used', hash(button_text) % 1000)
        
    except Exception as e:
        logger.error(f"❌ Error handling menu button: {e}")

def process_feedback(message):
    try:
        user_id = message.from_user.id
        feedback_text = message.text
        
        # Сохраняем фидбэк
        user_id_str = str(user_id)
        if 'user_feedback' not in db.__dict__:
            db.user_feedback = {}
        if user_id_str not in db.user_feedback:
            db.user_feedback[user_id_str] = []
        
        db.user_feedback[user_id_str].append({
            'feedback': feedback_text,
            'timestamp': datetime.datetime.now().isoformat()
        })
        
        bot.send_message(user_id,
            "✅ *Thank you for your feedback!*\n\n"
            "I've received your message and will review it carefully. "
            "Your input helps me improve! 💖",
            parse_mode='Markdown'
        )
        
        logger.info(f"📝 Feedback received from user {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Error processing feedback: {e}")

# ==================== CALLBACK ОБРАБОТЧИКИ ====================
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    try:
        user_id = call.from_user.id
        
        if call.data == "premium_basic":
            success = premium_manager.activate_premium(user_id, PremiumTier.BASIC)
            if success:
                bot.answer_callback_query(call.id, "🎉 Premium activated!")
                bot.send_message(user_id,
                    "💎 *Welcome to Premium!*\n\n"
                    "You now have:\n"
                    "• 8 message memory\n• No ads\n• Unlimited messages\n• Priority access\n\n"
                    "Thank you for supporting Luna! 💖",
                    parse_mode='Markdown'
                )
                achievement_system.check_achievements(user_id, 'premium_activated', 1)
            else:
                bot.answer_callback_query(call.id, "❌ Activation failed")
        
        elif call.data == "quick_chat":
            bot.answer_callback_query(call.id, "💬 Let's chat!")
            bot.send_message(user_id, "💖 What would you like to talk about? 🌸")
        
        elif call.data == "my_progress":
            bot.answer_callback_query(call.id, "📊 Loading progress...")
            show_progress(call.message)
        
        elif call.data == "premium_info":
            bot.answer_callback_query(call.id, "💎 Showing premium...")
            show_premium(call.message)
        
        elif call.data == "achievements":
            bot.answer_callback_query(call.id, "🏆 Loading achievements...")
            show_achievements(call.message)
        
        # Обработка игр
        elif call.data == "game_truth_dare":
            bot.answer_callback_query(call.id, "🎮 Starting Truth or Dare...")
            response = game_system.start_truth_or_dare(user_id)
            bot.send_message(user_id, response, parse_mode='Markdown')
        
        elif call.data == "game_wyr":
            bot.answer_callback_query(call.id, "🎮 Starting Would You Rather...")
            response = game_system.start_would_you_rather(user_id)
            bot.send_message(user_id, response, parse_mode='Markdown')
        
        elif call.data == "game_story":
            bot.answer_callback_query(call.id, "🎮 Starting Story Building...")
            response = game_system.start_story_building(user_id)
            bot.send_message(user_id, response, parse_mode='Markdown')
        
        elif call.data == "game_20q":
            bot.answer_callback_query(call.id, "🎮 Starting 20 Questions...")
            bot.send_message(user_id, 
                "🎮 *20 Questions* 🔍\n\n"
                "I'm thinking of something...\n"
                "Ask me yes/no questions to guess what it is!\n\n"
                "You have 20 questions. Ready? 💫",
                parse_mode='Markdown'
            )
            user_game_states[user_id] = {
                'game': '20_questions',
                'questions_left': 20,
                'target': random.choice(['apple', 'car', 'book', 'phone', 'cat', 'house', 'pizza', 'guitar'])
            }
            
    except Exception as e:
        logger.error(f"❌ Error handling callback: {e}")

# ==================== WEB SERVER ====================
app = Flask(__name__)

@app.route('/')
def dashboard():
    total_users = len(db.user_stats)
    total_messages = sum(stats.get('message_count', 0) for stats in db.user_stats.values())
    meaningful_messages = sum(stats.get('meaningful_messages', 0) for stats in db.user_stats.values())
    premium_users = len(db.premium_users)
    
    return f"""
    <html>
        <head>
            <title>Luna Bot Dashboard</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #f0f8ff; }}
                .container {{ max-width: 800px; margin: 0 auto; }}
                .header {{ text-align: center; color: #333; }}
                .stats {{ background: white; padding: 20px; border-radius: 10px; margin: 20px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .stat-item {{ margin: 10px 0; font-size: 18px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🤖 Luna Bot Dashboard</h1>
                    <p>Real-time monitoring and analytics</p>
                </div>
                <div class="stats">
                    <div class="stat-item"><strong>👥 Total Users:</strong> {total_users}</div>
                    <div class="stat-item"><strong>💬 Total Messages:</strong> {total_messages}</div>
                    <div class="stat-item"><strong>🎯 Meaningful Messages:</strong> {meaningful_messages}</div>
                    <div class="stat-item"><strong>💎 Premium Users:</strong> {premium_users}</div>
                    <div class="stat-item"><strong>🟢 Status:</strong> Running</div>
                    <div class="stat-item"><strong>⏰ Last Update:</strong> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
                </div>
            </div>
        </body>
    </html>
    """

@app.route('/api/status')
def api_status():
    return jsonify({
        'status': 'running',
        'users': len(db.user_stats),
        'messages': sum(stats.get('message_count', 0) for stats in db.user_stats.values()),
        'meaningful_messages': sum(stats.get('meaningful_messages', 0) for stats in db.user_stats.values()),
        'premium_users': len(db.premium_users),
        'timestamp': datetime.datetime.now().isoformat()
    })

# ==================== GRACEFUL SHUTDOWN ====================
def signal_handler(sig, frame):
    print("\n🛑 Shutting down Luna Bot gracefully...")
    logger.info("🛑 Shutdown signal received")
    db.save_data()
    logger.info("💾 All data saved safely!")
    logger.info("👋 Luna Bot shutdown complete")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# ==================== MAIN LAUNCH ====================
if __name__ == "__main__":
    print("🚀 Starting Luna Bot - Complete Fix Edition...")
    print(f"📊 Initial stats: {len(db.user_stats)} users, {sum(stats.get('message_count', 0) for stats in db.user_stats.values())} messages")
    print(f"🌐 Web dashboard: http://0.0.0.0:10000")
    print(f"🤖 AI System: ✅ OpenRouter Enabled")
    print(f"💎 Premium System: ✅ Working")
    print(f"🎮 Games: ✅ Truth or Dare, Would You Rather, Story Building")
    print(f"🛡️ Anti-spam: ✅ Meaningful messages only")
    print(f"💖 Romantic Mode: ✅ Toggle ON/OFF")
    
    try:
        web_thread = Thread(target=lambda: app.run(
            host='0.0.0.0', 
            port=10000, 
            debug=False, 
            use_reloader=False
        ))
        web_thread.daemon = True
        web_thread.start()
        logger.info("🌐 Web server started on port 10000")
    except Exception as e:
        logger.error(f"❌ Web server failed to start: {e}")
    
    try:
        logger.info("🔗 Starting Telegram Bot polling...")
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        logger.error(f"❌ Bot crashed: {e}")
        db.save_data()
        sys.exit(1)
