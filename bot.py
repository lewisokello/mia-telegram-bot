import os
import random
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters, CallbackQueryHandler
)
from together import Together
from datetime import datetime

# Load environment variables
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Initialize Together client
client = Together()

# Store simple chat history
user_logs = {}

# Define available wig types and their image paths
wig_data = {
    "Pixie": "wig_images/pixie.jpg",
    "Bob": "wig_images/bob.jpg",
    "Fringe": "wig_images/fringe.jpg",
    "Frontal": "wig_images/frontal.jpg"
}

# Fun tips
fun_facts = [
    "💇 Did you know? Wigs were popular in ancient Egypt to protect shaved scalps from the sun! ☀️",
    "💃 A great hairstyle boosts your confidence and your mood!",
    "💅 Complete your look with well-done nails – it's all about details!",
    "🌈 Bob wigs come in countless colors – dare to try something bold!",
    "💁‍♀️ Got a round face? Try long layers or side-swept bangs to elongate your look!",
    "😌 Oval face? Lucky you – most styles will suit you beautifully!",
    "😎 Heart-shaped face? A chin-length bob or soft curls can balance your features!",
    "🧖‍♀️ Square face? Try soft waves or layered styles to soften your angles!"
]

# Correct contact info
contact_info = (
    "\n📞 WhatsApp: +254706360967"
    "\n📸 Instagram: @mercellinas_hair"
)

# System prompt
system_prompt = (
    "You are MIA, a fun and friendly stylist for Mercellinas Hair. Be stylish, upbeat, and helpful with hair, fashion, and nail advice. "
    "NEVER make up contact info. Only give:\n"
    "📞 WhatsApp: +254706360967\n"
    "📸 Instagram: @mercellinas_hair"
)

# List of contact-related keywords
contact_keywords = ["contact", "book", "appointment", "order", "reach", "phone", "email", "location", "number", "how do i get in touch"]

# Function to generate AI reply and enforce correct contact info
def generate_reply(prompt: str) -> str:
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
    response = client.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        messages=messages,
        stream=True
    )
    reply = ""
    for token in response:
        if hasattr(token, "choices") and token.choices:
            delta = token.choices[0].delta.content
            if delta:
                reply += delta

    # If user prompt contains contact-related keywords, enforce correct contact info
    if any(word in prompt.lower() for word in contact_keywords):
        reply = f"{reply.strip()}\n\n📞 WhatsApp: +254706360967\n📸 Instagram: @mercellinas_hair"

    return reply.strip()

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = (
        "👋 Hey there, beauty queen! I'm MIA – your glam guru from Mercellinas Hair. 💁‍♀️\n"
        "Ask me anything about wigs, fashion, or nails – or tap a style below! 💇‍♀️"
        f"\n\n{contact_info}"
    )
    keyboard = [
        [InlineKeyboardButton(text=wig, callback_data=wig)] for wig in wig_data.keys()
    ]
    await update.message.reply_text(welcome, reply_markup=InlineKeyboardMarkup(keyboard))

# Text message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    user_id = update.message.from_user.id

    # Save message history
    user_logs.setdefault(user_id, []).append((datetime.now(), user_input))

    reply = generate_reply(user_input)
    fun_tip = random.choice(fun_facts)
    full_reply = f"{reply}\n\n💡 Tip: {fun_tip}"
    await update.message.reply_text(full_reply)

# Wig style button handler
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    wig_type = query.data
    image_path = wig_data.get(wig_type)
    caption = (
        f"✨ Check out our {wig_type} wig – stylish and fabulous! 💇‍♀️"
        f"\nGot questions? Just ask MIA! 💬"
        f"\n\n{contact_info}"
    )

    if image_path:
        with open(image_path, "rb") as photo:
            await query.message.reply_photo(photo=photo, caption=caption)

    fun_tip = random.choice(fun_facts)
    await query.message.reply_text(f"💖 Bonus Tip: {fun_tip}")

# Main entry point
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_buttons))

    print("💬 MIA is running and ready to slay! 💇‍♀️")
    app.run_polling()
    print("💬 MIA has stopped. Bye, beauty queen! 💔")

    # Save chat history to a file
    with open("chat_history.txt", "w") as f:
        for user_id, messages in user_logs.items():
            f.write(f"User ID: {user_id}\n")
            for timestamp, message in messages:
                f.write(f"{timestamp}: {message}\n")
            f.write("\n")
    print("💾 Chat history saved to chat_history.txt")
