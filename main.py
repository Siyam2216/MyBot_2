import logging
import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)

from handlers import security, osint, dev_tools

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

MAIN_MENU = InlineKeyboardMarkup([
    [InlineKeyboardButton("🛡️ Security Tools", callback_data="menu_security")],
    [InlineKeyboardButton("⚙️ OSINT & Utility", callback_data="menu_osint")],
    [InlineKeyboardButton("👤 Dev & Testing Tools", callback_data="menu_dev")],
])

SECURITY_MENU = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔗 Scan Link", callback_data="act_scan_link")],
    [InlineKeyboardButton("📸 Metadata Checker", callback_data="act_metadata")],
    [InlineKeyboardButton("📧 Breach Check", callback_data="act_breach")],
    [InlineKeyboardButton("🔐 Password Strength", callback_data="act_password")],
    [InlineKeyboardButton("⬅️ Back", callback_data="menu_main")],
])

OSINT_MENU = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔍 IP Tracker", callback_data="act_ip")],
    [InlineKeyboardButton("🌐 URL Expand/Shorten", callback_data="act_url")],
    [InlineKeyboardButton("🖼️ QR Generator", callback_data="act_qr")],
    [InlineKeyboardButton("📝 Text to Speech", callback_data="act_tts")],
    [InlineKeyboardButton("📡 WHOIS Lookup", callback_data="act_whois")],
    [InlineKeyboardButton("🧮 Subnet Calculator", callback_data="act_subnet")],
    [InlineKeyboardButton("⬅️ Back", callback_data="menu_main")],
])

DEV_MENU = InlineKeyboardMarkup([
    [InlineKeyboardButton("👤 Fake Identity", callback_data="act_fake_identity")],
    [InlineKeyboardButton("🔐 Base64 Encode/Decode", callback_data="act_base64")],
    [InlineKeyboardButton("📄 PDF Merge", callback_data="act_pdf_merge")],
    [InlineKeyboardButton("⬅️ Back", callback_data="menu_main")],
])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "স্বাগতম! 👋\nআমি একটি অল-ইন-ওয়ান সিকিউরিটি ও OSINT বট।\nনিচ থেকে একটি ক্যাটাগরি বেছে নিন:",
        reply_markup=MAIN_MENU
    )


ACTION_PROMPTS = {
    "act_scan_link": ("awaiting_link", "🔗 চেক করতে চাওয়া লিংকটি পাঠান:"),
    "act_metadata": ("awaiting_photo", "📸 মেটাডাটা চেক করতে একটি ছবি ফাইল (Document/Compress না করে) হিসেবে পাঠান:"),
    "act_breach": ("awaiting_email", "📧 চেক করতে চাওয়া ইমেইল অ্যাড্রেসটি পাঠান:"),
    "act_password": ("awaiting_password", "🔐 চেক করতে চাওয়া পাসওয়ার্ডটি পাঠান:\n(⚠️ শুধু টেস্টিং পারপাসে ব্যবহার করুন)"),
    "act_ip": ("awaiting_ip", "🔍 চেক করতে চাওয়া আইপি অ্যাড্রেসটি পাঠান:"),
    "act_url": ("awaiting_url", "🌐 লিংকটি পাঠান (শর্ট বা লং, দুটোই কাজ করবে):"),
    "act_qr": ("awaiting_qr_text", "🖼️ QR কোডে কনভার্ট করতে চাওয়া টেক্সট/লিংক পাঠান:"),
    "act_tts": ("awaiting_tts_text", "📝 ভয়েসে কনভার্ট করতে চাওয়া টেক্সট পাঠান (বাংলা বা ইংরেজি):"),
    "act_whois": ("awaiting_whois_domain", "📡 চেক করতে চাওয়া ডোমেইন নামটি পাঠান (যেমন: google.com):"),
    "act_subnet": ("awaiting_subnet", "🧮 CIDR নোটেশনে সাবনেট পাঠান (যেমন: 192.168.1.0/24):"),
    "act_fake_identity": ("fake_identity_now", None),
    "act_pdf_merge": ("awaiting_pdf_files", "📄 মার্জ করতে চাওয়া PDF ফাইলগুলো একে একে পাঠান। শেষ হলে /done লিখুন।"),
}


async def menu_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "menu_main":
        context.user_data.clear()
        await query.edit_message_text("মেইন মেনু:", reply_markup=MAIN_MENU)
    elif data == "menu_security":
        await query.edit_message_text("🛡️ Security Tools:", reply_markup=SECURITY_MENU)
    elif data == "menu_osint":
        await query.edit_message_text("⚙️ OSINT & Utility Tools:", reply_markup=OSINT_MENU)
    elif data == "menu_dev":
        await query.edit_message_text("👤 Dev & Testing Tools:", reply_markup=DEV_MENU)
    elif data == "act_base64":
        await dev_tools.base64_menu(update, context)
    elif data == "b64_encode":
        context.user_data["action"] = "awaiting_base64_encode"
        await query.edit_message_text("🔐 এনকোড করতে চাওয়া টেক্সট পাঠান:")
    elif data == "b64_decode":
        context.user_data["action"] = "awaiting_base64_decode"
        await query.edit_message_text("🔓 ডিকোড করতে চাওয়া Base64 স্ট্রিং পাঠান:")
    elif data.startswith("act_"):
        action, prompt = ACTION_PROMPTS.get(data, (None, None))
        if action == "fake_identity_now":
            await dev_tools.send_fake_identity(update, context)
            return
        context.user_data["action"] = action
        if action == "awaiting_pdf_files":
            context.user_data["pdf_files"] = []
        await query.edit_message_text(prompt)


async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    action = context.user_data.get("action")
    if not action:
        await update.message.reply_text("একটি টুল বেছে নিতে /start লিখুন।")
        return

    if action == "awaiting_link":
        await security.scan_link(update, context)
    elif action == "awaiting_email":
        await security.breach_check(update, context)
    elif action == "awaiting_password":
        await security.password_strength(update, context)
    elif action == "awaiting_ip":
        await osint.ip_tracker(update, context)
    elif action == "awaiting_url":
        await osint.url_tool(update, context)
    elif action == "awaiting_qr_text":
        await osint.qr_generate(update, context)
    elif action == "awaiting_tts_text":
        await osint.text_to_speech(update, context)
    elif action == "awaiting_whois_domain":
        await osint.whois_lookup(update, context)
    elif action == "awaiting_subnet":
        await osint.subnet_calculator(update, context)
    elif action == "awaiting_base64_encode":
        await dev_tools.base64_encode(update, context)
    elif action == "awaiting_base64_decode":
        await dev_tools.base64_decode(update, context)
    else:
        await update.message.reply_text("দুঃখিত, বুঝতে পারিনি। /start দিয়ে আবার শুরু করুন।")


async def photo_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    action = context.user_data.get("action")
    if action == "awaiting_photo":
        await security.metadata_checker(update, context)
    else:
        await update.message.reply_text("এই মুহূর্তে ছবি প্রয়োজন নেই। /start দিয়ে মেনু দেখুন।")


async def document_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    action = context.user_data.get("action")
    if action == "awaiting_photo":
        await security.metadata_checker(update, context)
    elif action == "awaiting_pdf_files":
        await dev_tools.collect_pdf(update, context)
    else:
        await update.message.reply_text("এই মুহূর্তে ফাইলের প্রয়োজন নেই। /start দিয়ে মেনু দেখুন।")


async def done_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("action") == "awaiting_pdf_files":
        await dev_tools.merge_pdfs(update, context)
    else:
        await update.message.reply_text("করার মতো কিছু নেই।")


def main():
    if not TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN .env এ সেট করুন।")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("done", done_command))
    app.add_handler(CallbackQueryHandler(menu_router))
    app.add_handler(MessageHandler(filters.PHOTO, photo_router))
    app.add_handler(MessageHandler(filters.Document.ALL, document_router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))

    logger.info("Bot চালু হচ্ছে...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
