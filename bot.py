import sqlite3
import random

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

TOKEN = "8649692039:AAGaJQSTBn5ub5CtENMZNZcrjQvI-MQR8QY"


# ---------------- DATABASE ----------------

def get_random_albums(limit=2):
    conn = sqlite3.connect("albums.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT rowid, Artist, Title, Genre, `AOTY User Score`
        FROM albums
        WHERE status = 'not_listened'
        ORDER BY RANDOM()
        LIMIT 20
    """)

    albums = cur.fetchall()

    if not albums:
        conn.close()
        return []

    selected = random.sample(albums, min(limit, len(albums)))

    for album in selected:
        cur.execute("""
            UPDATE albums
            SET status='recommended'
            WHERE rowid=?
        """, (album[0],))

    conn.commit()
    conn.close()

    return selected


def mark_action(rowid, action):
    conn = sqlite3.connect("albums.db")
    cur = conn.cursor()

    if action == "like":
        cur.execute("""
            UPDATE albums
            SET user_action='like',
                weight = weight + 1
            WHERE rowid=?
        """, (rowid,))

    elif action == "dislike":
        cur.execute("""
            UPDATE albums
            SET user_action='dislike',
                weight = max(weight - 0.5, 0.1)
            WHERE rowid=?
        """, (rowid,))

    elif action == "listened":
        cur.execute("""
            UPDATE albums
            SET status='listened'
            WHERE rowid=?
        """, (rowid,))

    conn.commit()
    conn.close()


# ---------------- HANDLERS ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎵 Бот работает. Используй /today")


async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    albums = get_random_albums()

    if not albums:
        await update.message.reply_text("Альбомы закончились.")
        return

    for rowid, artist, title, genre, score in albums:

        text = (
            f"🎵 {artist} — {title}\n"
            f"🎸 {genre}\n"
            f"⭐ {score}/100"
        )

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔥 Нравится", callback_data=f"like_{rowid}"),
                InlineKeyboardButton("👎 Не нравится", callback_data=f"dislike_{rowid}")
            ],
            [
                InlineKeyboardButton("✅ Прослушал", callback_data=f"listened_{rowid}")
            ]
        ])

        await update.message.reply_text(text, reply_markup=keyboard)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    action, rowid = query.data.split("_")
    rowid = int(rowid)

    mark_action(rowid, action)

    messages = {
        "like": "🔥 Запомнил твой вкус",
        "dislike": "👎 Учту и буду реже показывать",
        "listened": "✅ Отмечено как прослушанное"
    }

    await query.edit_message_text(messages.get(action, "Ок"))


# ---------------- MAIN ----------------

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("today", today))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()