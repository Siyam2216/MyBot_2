import os
import io
import base64 as b64
from faker import Faker
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ContextTypes
from pypdf import PdfWriter

fake = Faker()


async def send_fake_identity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["action"] = None
    query = update.callback_query

    profile = (
        f"👤 ফেক আইডেন্টিটি (শুধুমাত্র টেস্টিং পারপাসে):\n\n"
        f"নাম: {fake.name()}\n"
        f"ইমেইল: {fake.email()}\n"
        f"ফোন: {fake.phone_number()}\n"
        f"ঠিকানা: {fake.address()}\n"
        f"কোম্পানি: {fake.company()}\n"
        f"জব টাইটেল: {fake.job()}\n"
        f"বার্থডেট: {fake.date_of_birth()}\n"
    )

    if query:
        await query.edit_message_text(profile)
    else:
        await update.message.reply_text(profile)


async def base64_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Encode", callback_data="b64_encode")],
        [InlineKeyboardButton("Decode", callback_data="b64_decode")],
        [InlineKeyboardButton("⬅️ Back", callback_data="menu_dev")],
    ])
    await query.edit_message_text("🔐 Base64: Encode নাকি Decode করবেন?", reply_markup=keyboard)


async def base64_encode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data["action"] = None
    encoded = b64.b64encode(text.encode()).decode()
    await update.message.reply_text(f"🔐 Encoded:\n`{encoded}`", parse_mode="Markdown")


async def base64_decode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    context.user_data["action"] = None
    try:
        decoded = b64.b64decode(text).decode()
        await update.message.reply_text(f"🔓 Decoded:\n{decoded}")
    except Exception as e:
        await update.message.reply_text(f"❌ ভুল Base64 স্ট্রিং: {e}")


async def collect_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    if not doc.file_name.lower().endswith(".pdf"):
        await update.message.reply_text("⚠️ শুধুমাত্র PDF ফাইল পাঠান।")
        return

    tg_file = await doc.get_file()
    path = f"/tmp/{doc.file_unique_id}.pdf"
    await tg_file.download_to_drive(path)

    context.user_data.setdefault("pdf_files", []).append(path)
    count = len(context.user_data["pdf_files"])
    await update.message.reply_text(f"✅ {count}টি PDF যোগ হয়েছে। আরও পাঠান অথবা /done লিখুন।")


async def merge_pdfs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    files = context.user_data.get("pdf_files", [])
    context.user_data["action"] = None

    if len(files) < 2:
        await update.message.reply_text("⚠️ মার্জ করতে কমপক্ষে ২টি PDF ফাইল দরকার।")
        context.user_data["pdf_files"] = []
        return

    try:
        writer = PdfWriter()
        for f in files:
            writer.append(f)

        bio = io.BytesIO()
        writer.write(bio)
        bio.seek(0)
        bio.name = "merged.pdf"

        await update.message.reply_document(document=InputFile(bio), caption="📄 মার্জ করা PDF।")

        for f in files:
            if os.path.exists(f):
                os.remove(f)
        context.user_data["pdf_files"] = []

    except Exception as e:
        await update.message.reply_text(f"❌ এরর: {e}")
