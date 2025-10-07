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

# ==================== ОСТАЛЬНОЙ КОД ====================
# [ЗДЕСЬ ДОЛЖЕН БЫТЬ ВЕСЬ ОСТАЛЬНОЙ КОД БОТА]
# Классы MessageQueue, LunaDatabase, все функции и обработчики
# которые у тебя уже есть в рабочем боте!

# ВСТАВЬ СЮДА ВЕСЬ СВОЙ РАБОЧИЙ КОД ОТСЮДА:
# - Класс MessageQueue
# - Класс LunaDatabase  
# - Все функции (get_relationship_level, show_main_menu, и т.д.)
# - Все обработчики (@bot.message_handler)
# - Функция process_text_message
# - Функция start_bot()

def start_bot():
    """Запуск бота для Railway"""
    restart_count = 0
    max_restarts = 100
    
    while restart_count < max_restarts:
        try:
            print(f"🚀 Starting Luna Bot on Railway...")
            bot.polling(none_stop=True, timeout=30)
        except Exception as e:
            restart_count += 1
            print(f"🚨 Bot crashed: {e}")
            time.sleep(5)
    
    print("🔴 Max restarts reached")

if __name__ == "__main__":
    start_bot()
