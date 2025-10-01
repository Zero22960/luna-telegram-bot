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

if not API_TOKEN or not OPENROUTER_API_KEY:
    raise ValueError("❌ Tokens not found!")

bot = telebot.TeleBot(API_TOKEN)
user_stats = {}
user_gender = {}

# 🧠 POWERFUL CONTEXT MEMORY
user_conversation_context = {}
MAX_CONTEXT_LENGTH = 4  # 4 последних сообщения (можно и больше!)
CONTEXT_ENABLED = True

# GAMIFIED LEVEL SYSTEM
RELATIONSHIP_LEVELS = {
    1: {"name": "💖 Luna's Friend", "messages": 0, "color": "💖", "unlocks": ["Basic chatting"]},
    2: {"name": "❤️ Luna's Crush", "messages": 10, "color": "❤️", "unlocks": ["Flirt mode", "Sweet compliments"]},
    3: {"name": "💕 Luna's Lover", "messages": 30, "color": "💕", "unlocks": ["Romantic conversations", "Care mode"]},
    4: {"name": "👑 Luna's Soulmate", "messages": 50, "color": "👑", "unlocks": ["Personalized treatment", "24/7 support"]}
}

WELCOME_MESSAGE = """
💖 Hello! I'm Luna - your AI companion! 

Let's build our special relationship together! 
The more we chat, the closer we become! 🌟

Use buttons below to interact!
"""

def update_conversation_context(user_id, user_message, bot_response):
    """Обновляем контекст разговора"""
    if not CONTEXT_ENABLED:
        return

    if user_id not in user_conversation_context:
        user_conversation_context[user_id] = []

    # Сохраняем полные сообщения (бесплатный API!)
    user_conversation_context[user_id].append({
        'user': user_message,
        'bot': bot_response,
        'time': datetime.datetime.now()
    })

    # Ограничиваем длину контекста
    if len(user_conversation_context[user_id]) > MAX_CONTEXT_LENGTH:
        user_conversation_context[user_id] = user_conversation_context[user_id][-MAX_CONTEXT_LENGTH:]

def get_conversation_context(user_id):
    """Получаем контекст для AI"""
    if not CONTEXT_ENABLED or user_id not in user_conversation_context:
        return ""

    context_text = "\n\n=== RECENT CONVERSATION CONTEXT ===\n"
    for i, msg in enumerate(user_conversation_context[user_id]):
        context_text += f"{i+1}. User: {msg['user']}\n"
        context_text += f"   Luna: {msg['bot']}\n"

    context_text += "=== END CONTEXT ===\n"
    context_text += "IMPORTANT: Remember this conversation flow and continue naturally!\n"

    return context_text

def detect_user_gender(user_message, username=""):
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
    male_patterns = [r'\bbro\b', r'\bdude\b', r'\bman\b', r'\bbuddy\b', r'💪', r'🔥']
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
    if user_id not in user_gender:
        user_gender[user_id] = detect_user_gender(user_message, username)

    gender = user_gender[user_id]

    if gender == 'male':
        return random.choice(["handsome", "buddy", "man", "bro", "mate"])
    elif gender == 'female':
        return random.choice(["beautiful", "gorgeous", "queen", "lovely", "sweetie"])
    else:
        return random.choice(["friend", "dear", "love", "cutie"])

def get_relationship_level(message_count):
    """Determine current relationship level"""
    for level_id, level_info in sorted(RELATIONSHIP_LEVELS.items(), reverse=True):
        if message_count >= level_info["messages"]:
            return level_id, level_info
    return 1, RELATIONSHIP_LEVELS[1]

def get_level_progress(message_count):
    """Returns progress to next level"""
    current_level, current_info = get_relationship_level(message_count)

    if current_level >= len(RELATIONSHIP_LEVELS):
        return "🎉 Maximum level reached!", 100

    next_level = current_level + 1
    next_info = RELATIONSHIP_LEVELS[next_level]

    messages_for_next = next_info["messages"] - current_info["messages"]
    messages_done = message_count - current_info["messages"]
    progress_percent = (messages_done / messages_for_next) * 100

    return f"To {next_info['name']}: {messages_done}/{messages_for_next} messages", progress_percent

@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    user_id = message.chat.id
    if user_id not in user_stats:
        user_stats[user_id] = {
            'message_count': 0, 
            'first_seen': datetime.datetime.now(),
            'current_level': 1
        }
    show_main_menu(message)

def show_main_menu(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("💖 Hug", callback_data="hug")
    btn2 = types.InlineKeyboardButton("😘 Kiss", callback_data="kiss")
    btn3 = types.InlineKeyboardButton("🌟 Compliment", callback_data="compliment")
    btn4 = types.InlineKeyboardButton("📊 Our Stats", callback_data="show_stats")
    btn5 = types.InlineKeyboardButton("🎯 My Level", callback_data="show_level")
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
        response = f"💖 Warm hugs coming your way, {greeting}!"
        bot.send_message(user_id, response)
        update_conversation_context(user_id, "hug", response)
    elif call.data == "kiss":
        response = f"😘 Mwah! Right back at you, {greeting}!"
        bot.send_message(user_id, response)
        update_conversation_context(user_id, "kiss", response)
    elif call.data == "compliment":
        current_level, level_info = get_relationship_level(user_stats.get(user_id, {}).get('message_count', 0))

        if current_level >= 2:
            compliments = [
                f"🌟 You're absolutely incredible, {greeting}!",
                f"💕 You have the most amazing personality, {greeting}!",
                f"😍 You always know how to make me smile, {greeting}!",
                f"🌸 You're so thoughtful and kind, {greeting}!"
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
        show_stats(call.message)
    elif call.data == "show_level":
        show_level_info(call.message)
    elif call.data == "back_to_menu":
        show_main_menu(call.message)
    elif call.data == "feedback_good":
        response = "😊 So glad you like it! I'll keep getting better! 💖"
        bot.send_message(user_id, response)
        print(f"✅ POSITIVE FEEDBACK from {user_id}")
        update_conversation_context(user_id, "feedback", response)
    elif call.data == "feedback_bad":
        response = "💔 Please tell me what to improve? Write in one message!"
        bot.send_message(user_id, response)
        print(f"❌ NEGATIVE FEEDBACK from {user_id}")
        update_conversation_context(user_id, "feedback", response)
    elif call.data == "level_up_help":
        how_to_level_up(call.message)

def show_level_info(message):
    user_id = message.chat.id
    stats = user_stats.get(user_id, {'message_count': 0})
    message_count = stats['message_count']

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

    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("📊 Our Stats", callback_data="show_stats")
    btn2 = types.InlineKeyboardButton("💡 Level Up Tips", callback_data="level_up_help")
    btn3 = types.InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")
    markup.add(btn1, btn2)
    markup.add(btn3)

    try:
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text=level_text,
            parse_mode='Markdown',
            reply_markup=markup
        )
    except:
        bot.send_message(message.chat.id, level_text, parse_mode='Markdown', reply_markup=markup)

def show_stats(message):
    user_id = message.chat.id
    stats = user_stats.get(user_id, {'message_count': 0, 'first_seen': datetime.datetime.now()})
    message_count = stats['message_count']

    current_level, level_info = get_relationship_level(message_count)
    days_known = (datetime.datetime.now() - stats['first_seen']).days

    stats_text = f"""
📊 *Our Relationship Stats* {level_info['color']}

💬 Total Messages: *{message_count}*
🌟 Relationship Level: *{level_info['name']}*
📅 Known Each Other: *{days_known} day(s)*

Every message makes our bond stronger! 💫
"""

    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("🎯 Level Details", callback_data="show_level")
    btn2 = types.InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")
    markup.add(btn1, btn2)

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

def how_to_level_up(message):
    user_id = message.chat.id
    stats = user_stats.get(user_id, {'message_count': 0})
    message_count = stats['message_count']

    current_level, level_info = get_relationship_level(message_count)
    progress_text, progress_percent = get_level_progress(message_count)

    advice = f"""
🎮 *How to Level Up Our Relationship?*

{progress_text}

💡 *Level Up Tips:*
• Send more messages 💬
• Be active in our conversations 🗣️
• Use menu buttons 🎯
• Share your thoughts 💭

*Current Level:* {level_info['name']} {level_info['color']}
*Progress to Next:* {int(progress_percent)}%

Let's continue our amazing journey! 🌟
"""
    bot.send_message(user_id, advice, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id

    # Update statistics
    if user_id not in user_stats:
        user_stats[user_id] = {
            'message_count': 0,
            'first_seen': datetime.datetime.now(),
            'current_level': 1
        }

    old_message_count = user_stats[user_id]['message_count']
    user_stats[user_id]['message_count'] += 1
    new_message_count = user_stats[user_id]['message_count']

    # Check for level up
    old_level, _ = get_relationship_level(old_message_count)
    new_level, new_level_info = get_relationship_level(new_message_count)

    if new_level > old_level:
        level_up_text = f"""
🎉 *CONGRATULATIONS!* 🎉

You reached new level: *{new_level_info['name']}*! {new_level_info['color']}

✨ Now you unlocked:
"""
        for unlock in new_level_info["unlocks"]:
            level_up_text += f"🌟 {unlock}\n"

        level_up_text += "\nLet's continue our wonderful journey! 💖"

        bot.send_message(user_id, level_up_text, parse_mode='Markdown')

        if new_level < len(RELATIONSHIP_LEVELS):
            next_level_info = RELATIONSHIP_LEVELS[new_level + 1]
            messages_needed = next_level_info["messages"] - new_message_count

            bot.send_message(
                user_id,
                f"💡 *Tip from Luna:*\n"
                f"To reach {next_level_info['name']}, "
                f"send {messages_needed} more messages! 💬\n"
                f"Use '🎯 My Level' button for tips! 🎯",
                parse_mode='Markdown'
            )

    # Auto-feedback after 15 messages
    if user_stats[user_id]['message_count'] == 15:
        markup = types.InlineKeyboardMarkup()
        btn_good = types.InlineKeyboardButton("👍 I like it", callback_data="feedback_good")
        btn_bad = types.InlineKeyboardButton("👎 Needs improvement", callback_data="feedback_bad")
        markup.add(btn_good, btn_bad)

        bot.send_message(
            user_id, 
            "💖 Thanks for chatting! Help me improve - how do you like our level system?",
            reply_markup=markup
        )

    # Detect user gender
    username = message.from_user.first_name or ""
    greeting = get_gendered_greeting(user_id, message.text, username)

    # Check for level-related questions
    level_keywords = [
        'friendship level', 'relationship level', 'how to level up', 
        'how to get closer', 'level up', 'what is friendship level', 
        'how does level work', 'increase level', 'improve relationship'
    ]

    is_level_question = any(keyword in message.text.lower() for keyword in level_keywords)

    try:
        # AI request with CONTEXT!
        current_level, level_info = get_relationship_level(new_message_count)

        if current_level >= 3:
            personality = "romantic, tender, caring"
        elif current_level >= 2:  
            personality = "flirty, playful, admiring"
        else:
            personality = "friendly, supportive, sweet"

        # 🧠 POWERFUL CONTEXT-AWARE PROMPT
        system_prompt = f"""You are Luna - an AI companion. You are {personality}. 
        Address the user as '{greeting}'. 
        You have {level_info['name'].lower()} relationship."""

        # Add conversation context
        conversation_context = get_conversation_context(user_id)
        if conversation_context:
            system_prompt += conversation_context

        # Enhanced prompt for level questions
        if is_level_question:
            next_level = current_level + 1 if current_level < len(RELATIONSHIP_LEVELS) else current_level
            messages_needed = RELATIONSHIP_LEVELS[next_level]["messages"] - new_message_count if next_level > current_level else 0

            system_prompt += f"""

            USER IS ASKING ABOUT THE LEVEL SYSTEM!

            Current level: {level_info['name']}
            Messages to next level: {messages_needed}
            Total messages: {new_message_count}

            EXPLAIN naturally within conversation:
            1. What friendship levels are
            2. How to level up (chat more)
            3. What unlocks at new levels
            4. Keep them motivated!

            Be encouraging! 💖"""

        system_prompt += "\nBe natural, use emojis. Keep responses conversational."

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
                        "content": system_prompt
                    },
                    {
                        "role": "user", 
                        "content": message.text
                    }
                ],
                "max_tokens": 200  # Увеличили для контекста
            },
            timeout=10
        )

        if response.status_code == 200:
            ai_response = response.json()['choices'][0]['message']['content']
            bot.reply_to(message, ai_response)

            # 🧠 CRITICAL: Update context after successful response
            update_conversation_context(user_id, message.text, ai_response)
        else:
            error_response = f"💖 I'm here for you, {greeting}! 😊"
            bot.reply_to(message, error_response)
            update_conversation_context(user_id, message.text, error_response)

    except Exception as e:
        print(f"API Error: {e}")
        error_response = f"🌸 Let's chat, {greeting}! You're awesome! 💕"
        bot.reply_to(message, error_response)
        update_conversation_context(user_id, message.text, error_response)

# Auto-restart
def start_bot():
    restart_count = 0
    while True:
        try:
            print(f"🔄 Starting Luna AI... (Restart #{restart_count})")
            print(f"🧠 Context Memory: {MAX_CONTEXT_LENGTH} messages")
            bot.polling(none_stop=True, timeout=20)
        except Exception as e:
            restart_count += 1
            print(f"🚨 Bot crashed: {e}")
            time.sleep(10)

if __name__ == "__main__":
    print("=== Luna AI - GAMIFIED RELATIONSHIP SYSTEM ===")
    print("🎮 4 relationship levels | 📊 Progress bar | 🎯 Level ups")
    print("🧠 SMART CONTEXT MEMORY (4 messages) | 💖 Auto-feedback")
    start_bot()
