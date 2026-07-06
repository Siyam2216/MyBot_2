# 🛡️ TG Security & OSINT Bot

Telegram এর জন্য অল-ইন-ওয়ান সিকিউরিটি, OSINT ও ডেভেলপার টুলকিট বট।

## ✅ ফিচার লিস্ট

**Security:** Scan Link (VirusTotal), Metadata/EXIF Checker, Breach Check (HIBP), Password Strength Auditor
**OSINT & Utility:** IP Tracker, URL Expander/Shortener, QR Generator, Text-to-Speech, WHOIS Lookup, Subnet Calculator
**Dev Tools:** Fake Identity Generator, Base64 Encode/Decode, PDF Merger

## 📁 প্রজেক্ট স্ট্রাকচার

```
tg-security-bot/
├── main.py
├── requirements.txt
├── render.yaml
├── .env.example
└── handlers/
    ├── security.py
    ├── osint.py
    └── dev_tools.py
```

## 🔑 দরকারি API Key গুলো

| Key | কোথায় পাবেন | ফ্রি? |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Telegram এ [@BotFather](https://t.me/BotFather) থেকে `/newbot` | হ্যাঁ |
| `VIRUSTOTAL_API_KEY` | virustotal.com → Sign up → Profile → API Key | হ্যাঁ (limited rate) |
| `HIBP_API_KEY` | haveibeenpwned.com/API/Key | ❌ পেইড (~$3.95/মাস) |

> HIBP key না দিলেও বট চলবে, শুধু Breach Check ফিচারটি একটি সতর্কবার্তা দেখাবে।

## 🖥️ লোকালি রান করা (টেস্টের জন্য)

```bash
git clone <your-repo-url>
cd tg-security-bot
pip install -r requirements.txt
cp .env.example .env
# .env ফাইলে আপনার আসল key গুলো বসান
python main.py
```

## ☁️ GitHub এ আপলোড করা

```bash
cd tg-security-bot
git init
git add .
git commit -m "Initial commit: TG Security Bot"
git branch -M main
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```

⚠️ `.env` ফাইলটি `.gitignore` এ আছে, তাই এটি GitHub এ যাবে না। আসল key কখনো পাবলিক রিপোতে কমিট করবেন না।

## 🚀 Render এ ডিপ্লয় করা

এই বট **long polling** দিয়ে চলে (webhook না), তাই Render এ এটাকে **Background Worker** হিসেবে ডিপ্লয় করতে হবে (Web Service না)।

### ধাপে ধাপে:

1. [render.com](https://render.com) এ লগইন করুন, GitHub একাউন্ট কানেক্ট করুন।
2. **New +** → **Background Worker** সিলেক্ট করুন।
3. আপনার `tg-security-bot` রিপোজিটরি সিলেক্ট করুন।
4. সেটিংস:
   - **Name:** `tg-security-bot`
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python main.py`
5. **Environment Variables** সেকশনে যোগ করুন:
   - `TELEGRAM_BOT_TOKEN`
   - `VIRUSTOTAL_API_KEY`
   - `HIBP_API_KEY` (অপশনাল)
6. **Create Background Worker** ক্লিক করুন।

> `render.yaml` ফাইলটি রিপোতে আছে, চাইলে Render এর **Blueprint** ফিচার দিয়ে (New + → Blueprint) পুরো সেটআপ অটোমেটিক করতে পারবেন — শুধু env var গুলোর ভ্যালু বসাতে হবে।

### ⚠️ গুরুত্বপূর্ণ নোট

- **Background Worker** Render এর ফ্রি প্ল্যানে নেই — সবচেয়ে সস্তা `Starter` প্ল্যান (~$7/মাস) লাগবে, কারণ এটা ২৪/৭ চলা দরকার।
- ফ্রি-তে চালাতে চাইলে বিকল্প হলো Web Service + webhook mode এ কনভার্ট করা, কিন্তু Render এর ফ্রি Web Service ১৫ মিনিট নিষ্ক্রিয় থাকলে স্লিপ হয়ে যায় — বট তখন রেসপন্স করবে না।

## 🧪 ব্যবহার

Telegram এ বট চালু করে `/start` লিখুন → বাটন মেনু থেকে ক্যাটাগরি ও টুল সিলেক্ট করুন → ইনপুট (লিংক/ইমেইল/ছবি/ইত্যাদি) পাঠান।

PDF মার্জের ক্ষেত্রে একাধিক PDF একে একে পাঠিয়ে শেষে `/done` লিখুন।

## 🔒 লিগ্যাল নোট

Fake Identity Generator শুধুমাত্র ফর্ম টেস্টিং/QA পারপাসে — বাস্তব প্রতারণা বা জাল ডকুমেন্টে ব্যবহার করবেন না। Password Strength চেকার ইনপুট করা পাসওয়ার্ড মেসেজ চেকের পর অটোমেটিক ডিলিট করার চেষ্টা করে, তবুও রিয়েল/লাইভ পাসওয়ার্ড শেয়ার না করাই ভালো।
