from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro')

user_states = {} #track user mode(eg.Gemini,about,help)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(" Chat with Gemini", callback_data="gemini")],
        [InlineKeyboardButton(" About", callback_data="about")],
        [InlineKeyboardButton(" Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(" Welcome! Choose an option:", reply_markup=reply_markup)
    
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if query.data == "gemini":
        user_states[user_id] = "gemini"
        await query.edit_message_text("You're now chatting with Gemini.\n\nType your message, or send /back to go to main menu.")

    elif query.data == "about":
        await query.edit_message_text("This bot uses Gemini API to reply to your messages use /back to exit ")

    elif query.data == "help":
        await query.edit_message_text("Use /start to go back to menu.\nUse /back to exit Gemini mode.")

async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_states.pop(update.message.from_user.id, None)
    await start(update, context)
    
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_states.get(user_id) == "gemini":
        try:
            response = model.generate_content(update.message.text)
            await update.message.reply_text(response.text)
        except Exception as e:
            await update.message.reply_text(" Error: " + str(e))

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("back", back))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print(" Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
