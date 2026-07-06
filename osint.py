import io
import requests
import qrcode
import ipaddress
import whois
from gtts import gTTS
from langdetect import detect
from telegram import Update, InputFile
from telegram.ext import ContextTypes


async def ip_tracker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ip = update.message.text.strip()
    context.user_data["action"] = None

    try:
        resp = requests.get(f"http://ip-api.com/json/{ip}", timeout=10)
        data = resp.json()

        if data.get("status") != "success":
            await update.message.reply_text(f"❌ তথ্য পাওয়া যায়নি: {data.get('message', 'অজানা এরর')}")
            return

        report = (
            f"🔍 IP: {data.get('query')}\n\n"
            f"🌍 দেশ: {data.get('country')}\n"
            f"🏙️ শহর: {data.get('city')}\n"
            f"📮 জিপ কোড: {data.get('zip')}\n"
            f"🕒 টাইমজোন: {data.get('timezone')}\n"
            f"🏢 ISP: {data.get('isp')}\n"
            f"🏛️ Organization: {data.get('org')}\n"
        )
        await update.message.reply_text(report)
    except Exception as e:
        await update.message.reply_text(f"❌ এরর: {e}")


async def url_tool(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    context.user_data["action"] = None

    try:
        resp = requests.head(url, allow_redirects=True, timeout=10)
        final_url = resp.url

        if final_url != url:
            await update.message.reply_text(f"🌐 আসল ডেস্টিনেশন:\n{final_url}")
            return

        shorten_resp = requests.get(
            "https://tinyurl.com/api-create.php", params={"url": url}, timeout=10
        )
        if shorten_resp.status_code == 200:
            await update.message.reply_text(f"🔗 শর্ট লিংক:\n{shorten_resp.text}")
        else:
            await update.message.reply_text("❌ শর্ট করতে ব্যর্থ হয়েছি।")

    except Exception as e:
        await update.message.reply_text(f"❌ এরর: {e}\n\nলিংকটি সঠিক কিনা (http:// বা https:// সহ) চেক করুন।")


async def qr_generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data["action"] = None

    try:
        img = qrcode.make(text)
        bio = io.BytesIO()
        bio.name = "qrcode.png"
        img.save(bio, "PNG")
        bio.seek(0)
        await update.message.reply_photo(photo=InputFile(bio), caption="🖼️ আপনার QR কোড তৈরি হয়েছে।")
    except Exception as e:
        await update.message.reply_text(f"❌ এরর: {e}")


async def text_to_speech(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data["action"] = None

    try:
        try:
            lang = detect(text)
            lang = "bn" if lang == "bn" else "en"
        except Exception:
            lang = "en"

        tts = gTTS(text=text, lang=lang)
        bio = io.BytesIO()
        tts.write_to_fp(bio)
        bio.seek(0)
        bio.name = "voice.mp3"

        await update.message.reply_voice(voice=InputFile(bio))
    except Exception as e:
        await update.message.reply_text(f"❌ এরর: {e}")


async def whois_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    domain = update.message.text.strip()
    context.user_data["action"] = None

    try:
        w = whois.whois(domain)
        report = (
            f"📡 WHOIS: {domain}\n\n"
            f"📝 Registrar: {w.registrar}\n"
            f"📅 তৈরি হয়েছে: {w.creation_date}\n"
            f"⏳ মেয়াদ শেষ: {w.expiration_date}\n"
            f"🏢 Organization: {getattr(w, 'org', 'N/A')}\n"
            f"🌐 Name Servers: {', '.join(w.name_servers) if w.name_servers else 'N/A'}\n"
        )
        await update.message.reply_text(report)
    except Exception as e:
        await update.message.reply_text(f"❌ এরর: {e}\n\nডোমেইন নামটি সঠিক কিনা চেক করুন।")


async def subnet_calculator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cidr = update.message.text.strip()
    context.user_data["action"] = None

    try:
        net = ipaddress.ip_network(cidr, strict=False)
        hosts = list(net.hosts())
        report = (
            f"🧮 Subnet: {cidr}\n\n"
            f"🌐 Network Address: {net.network_address}\n"
            f"📡 Broadcast Address: {net.broadcast_address}\n"
            f"🎭 Subnet Mask: {net.netmask}\n"
            f"👥 Total Hosts: {net.num_addresses}\n"
            f"✅ Usable Hosts: {max(net.num_addresses - 2, 0)}\n"
            f"📊 First Usable: {hosts[0] if hosts else 'N/A'}\n"
            f"📊 Last Usable: {hosts[-1] if hosts else 'N/A'}\n"
        )
        await update.message.reply_text(report)
    except Exception as e:
        await update.message.reply_text(f"❌ ভুল CIDR ফরম্যাট: {e}\n\nউদাহরণ: 192.168.1.0/24")
