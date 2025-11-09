import os
import json
import random
import asyncio
import aiofiles
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.error import Forbidden, TelegramError
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# 🔐 Загрузка токена
load_dotenv()
TOKEN = os.getenv("8240784830:AAH4FXWAOGu-17imAZbVno7xbMqLktoISiQ")
if not TOKEN:
    raise ValueError("❌ Токен не найден!")

DATA_FILE = "data.json"
items = {1: "Камень", 2: "Ножницы", 3: "Бумага"}
scores = {}
total_wins = {}

async def load_data():
    global scores, total_wins
    if os.path.exists(DATA_FILE):
        async with aiofiles.open(DATA_FILE, "r", encoding="utf-8") as f:
            content = await f.read()
            data = json.loads(content)
            scores = data.get("scores", {})
            total_wins = data.get("total_wins", {})
        print("✅ Данные загружены.")

async def save_data():
    async with aiofiles.open(DATA_FILE, "w", encoding="utf-8") as f:
        await f.write(json.dumps({"scores": scores, "total_wins": total_wins}, ensure_ascii=False, indent=4))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎮 Играть", callback_data="menu_play"),
         InlineKeyboardButton("📜 Правила", callback_data="menu_rules")],
        [InlineKeyboardButton("🏆 Топ", callback_data="menu_top"),
         InlineKeyboardButton("ℹ️ Помощь", callback_data="menu_help")]
    ]
    await update.message.reply_text("👋 Привет! Выбери действие 👇",
                                    reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    user_choice = int(query.data) if query.data.isdigit() else None
    if not user_choice:
        return
    bot_choice = random.randint(1, 3)
    result = ""
    if user_choice == bot_choice:
        result = "🤝 Ничья!"
    elif (user_choice, bot_choice) in [(1,2),(2,3),(3,1)]:
        result = "🎉 Ты победил!"
        scores[user_id] = scores.get(user_id, 0) + 1
    else:
        result = "😤 Бот победил!"
    text = f"🤖 Бот: {items[bot_choice]}\n👤 Ты: {items[user_choice]}\n\n{result}\n📊 Счёт: {scores.get(user_id,0)}/3"
    await query.edit_message_text(text, parse_mode="Markdown")
    await save_data()

async def main():
    await load_data()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(play))
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
