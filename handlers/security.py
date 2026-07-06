import os
import re
import base64
import requests
import exifread
from telegram import Update
from telegram.ext import ContextTypes

VT_API_KEY = os.getenv("VIRUSTOTAL_API_KEY")
HIBP_API_KEY = os.getenv("HIBP_API_KEY")


async def scan_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    context.user_data["action"] = None

    if not VT_API_KEY:
        await update.message.reply_text("⚠️ VIRUSTOTAL_API_KEY সেট করা নেই। .env ফাইলে API key যোগ করুন।")
        return

    await update.message.reply_text("🔎 স্ক্যান করা হচ্ছে, একটু অপেক্ষা করুন...")

    try:
        url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
        headers = {"x-apikey": VT_API_KEY}

        resp = requests.get(f"https://www.virustotal.com/api/v3/urls/{url_id}", headers=headers, timeout=15)

        if resp.status_code == 404:
            submit = requests.post(
                "https://www.virustotal.com/api/v3/urls",
                headers=headers, data={"url": url}, timeout=15
            )
            if submit.status_code not in (200, 201):
                await update.message.reply_text("❌ VirusTotal এ সাবমিট করতে ব্যর্থ হয়েছি।")
                return
            await update.message.reply_text("লিংকটি নতুন, VirusTotal এনালাইসিস করছে। কিছুক্ষণ পর আবার চেষ্টা করুন।")
            return

        if resp.status_code != 200:
            await update.message.reply_text(f"❌ VirusTotal API এরর: {resp.status_code}")
            return

        data = resp.json()
        stats = data["data"]["attributes"]["last_analysis_stats"]
        malicious = stats.get("malicious", 0)
        suspicious = stats.get("suspicious", 0)
        harmless = stats.get("harmless", 0)
        undetected = stats.get("undetected", 0)

        verdict = "✅ নিরাপদ মনে হচ্ছে" if malicious == 0 and suspicious == 0 else "⚠️ সন্দেহজনক / ম্যালিশিয়াস হতে পারে!"

        report = (
            f"{verdict}\n\n"
            f"🔗 URL: {url}\n"
            f"🔴 Malicious: {malicious}\n"
            f"🟠 Suspicious: {suspicious}\n"
            f"🟢 Harmless: {harmless}\n"
            f"⚪ Undetected: {undetected}\n"
        )
        await update.message.reply_text(report)

    except Exception as e:
        await update.message.reply_text(f"❌ এরর হয়েছে: {e}")


async def metadata_checker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["action"] = None
    file = update.message.document or (update.message.photo[-1] if update.message.photo else None)

    if update.message.photo and not update.message.document:
        await update.message.reply_text(
            "⚠️ Telegram কম্প্রেসড ছবি থেকে অটোমেটিক EXIF মুছে ফেলে। "
            "মেটাডাটা চেক করতে ছবিটি 'ফাইল' (Document, Compress না করে) হিসেবে পাঠান।"
        )

    try:
        tg_file = await file.get_file()
        path = f"/tmp/{file.file_unique_id}.jpg"
        await tg_file.download_to_drive(path)

        with open(path, "rb") as f:
            tags = exifread.process_file(f, details=False)

        if not tags:
            await update.message.reply_text("ℹ️ এই ছবিতে কোনো EXIF মেটাডাটা পাওয়া যায়নি (আগে থেকেই মুছে ফেলা হয়েছে হতে পারে)।")
            return

        gps_lat = tags.get("GPS GPSLatitude")
        gps_lon = tags.get("GPS GPSLongitude")
        camera_make = tags.get("Image Make")
        camera_model = tags.get("Image Model")
        date_taken = tags.get("EXIF DateTimeOriginal")

        report = "📸 মেটাডাটা রিপোর্ট:\n\n"
        report += f"📍 GPS Location: {'পাওয়া গেছে (' + str(gps_lat) + ', ' + str(gps_lon) + ')' if gps_lat and gps_lon else 'পাওয়া যায়নি'}\n"
        report += f"📷 Camera: {camera_make} {camera_model}\n" if (camera_make or camera_model) else "📷 Camera: তথ্য পাওয়া যায়নি\n"
        report += f"🕒 তোলার সময়: {date_taken if date_taken else 'পাওয়া যায়নি'}"

        await update.message.reply_text(report)
        os.remove(path)

    except Exception as e:
        await update.message.reply_text(f"❌ এরর: {e}")


async def breach_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text.strip()
    context.user_data["action"] = None

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        await update.message.reply_text("⚠️ সঠিক ইমেইল অ্যাড্রেস দিন।")
        return

    if not HIBP_API_KEY:
        await update.message.reply_text(
            "⚠️ HIBP_API_KEY সেট করা নেই।\n"
            "Have I Been Pwned এখন পেইড API কী (haveibeenpwned.com/API/Key) প্রয়োজন করে। "
            "কী নিয়ে .env এ HIBP_API_KEY যোগ করুন।"
        )
        return

    await update.message.reply_text("🔎 চেক করা হচ্ছে...")

    try:
        headers = {"hibp-api-key": HIBP_API_KEY, "user-agent": "TG-Security-Bot"}
        resp = requests.get(
            f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}",
            headers=headers, timeout=15
        )

        if resp.status_code == 404:
            await update.message.reply_text("✅ ভালো খবর! এই ইমেইলটি কোনো পরিচিত ডাটা ব্রিচে পাওয়া যায়নি।")
            return
        if resp.status_code != 200:
            await update.message.reply_text(f"❌ API এরর: {resp.status_code}")
            return

        breaches = resp.json()
        names = ", ".join([b["Name"] for b in breaches])
        await update.message.reply_text(
            f"⚠️ এই ইমেইলটি {len(breaches)}টি ব্রিচে পাওয়া গেছে:\n\n{names}\n\n"
            "👉 এই সাইটগুলোতে ব্যবহৃত পাসওয়ার্ড এখনই পরিবর্তন করুন।"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ এরর: {e}")


async def password_strength(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pwd = update.message.text
    context.user_data["action"] = None

    length = len(pwd)
    has_lower = bool(re.search(r"[a-z]", pwd))
    has_upper = bool(re.search(r"[A-Z]", pwd))
    has_digit = bool(re.search(r"\d", pwd))
    has_special = bool(re.search(r"[^A-Za-z0-9]", pwd))

    score = sum([length >= 8, length >= 12, has_lower, has_upper, has_digit, has_special])

    if score <= 2:
        verdict, emoji = "খুবই দুর্বল", "🔴"
    elif score <= 4:
        verdict, emoji = "মোটামুটি", "🟠"
    elif score == 5:
        verdict, emoji = "ভালো", "🟡"
    else:
        verdict, emoji = "শক্তিশালী", "🟢"

    tips = []
    if length < 12:
        tips.append("কমপক্ষে ১২ ক্যারেক্টার ব্যবহার করুন")
    if not has_upper:
        tips.append("বড় হাতের অক্ষর যোগ করুন")
    if not has_digit:
        tips.append("সংখ্যা যোগ করুন")
    if not has_special:
        tips.append("স্পেশাল ক্যারেক্টার (!@#$%) যোগ করুন")

    report = f"{emoji} পাসওয়ার্ড স্ট্রেংথ: {verdict} ({score}/6)\n\n"
    if tips:
        report += "💡 উন্নত করতে:\n- " + "\n- ".join(tips)
    else:
        report += "✅ এই পাসওয়ার্ডটি যথেষ্ট শক্তিশালী।"

    await update.message.reply_text(report)

    try:
        await update.message.delete()
    except Exception:
        pass
