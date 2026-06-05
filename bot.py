import os
import sqlite3

# load_dotenv ni olib tashlaymiz — Railway o'zi o'qiydi
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_KEY = os.getenv("GROQ_API_KEY")
print(f"GROQ_KEY: {GROQ_KEY[:10] if GROQ_KEY else 'TOPILMADI'}")
client = Groq(api_key=GROQ_KEY)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BAZA — yaratish va ulash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def baza_yarat():
    conn = sqlite3.connect("kaloriya.db")
    cur = conn.cursor()

    # Foydalanuvchilar jadvali
    cur.execute("""
        CREATE TABLE IF NOT EXISTS foydalanuvchilar (
            user_id INTEGER PRIMARY KEY,
            ism TEXT,
            kunlik_maqsad INTEGER DEFAULT 2000
        )
    """)

    # Ovqatlar jadvali
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ovqatlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            ovqat_nomi TEXT,
            kaloriya INTEGER,
            sana TEXT DEFAULT (date('now'))
        )
    """)

    conn.commit()
    conn.close()

def foydalanuvchi_saqlash(user_id, ism):
    conn = sqlite3.connect("kaloriya.db")
    cur = conn.cursor()
    cur.execute("""
        INSERT OR IGNORE INTO foydalanuvchilar (user_id, ism)
        VALUES (?, ?)
    """, (user_id, ism))
    conn.commit()
    conn.close()

def maqsad_saqlash(user_id, maqsad):
    conn = sqlite3.connect("kaloriya.db")
    cur = conn.cursor()
    cur.execute("""
        UPDATE foydalanuvchilar SET kunlik_maqsad = ?
        WHERE user_id = ?
    """, (maqsad, user_id))
    conn.commit()
    conn.close()

def maqsad_olish(user_id):
    conn = sqlite3.connect("kaloriya.db")
    cur = conn.cursor()
    cur.execute("SELECT kunlik_maqsad FROM foydalanuvchilar WHERE user_id = ?", (user_id,))
    natija = cur.fetchone()
    conn.close()
    return natija[0] if natija else 2000

def ovqat_saqlash(user_id, ovqat_nomi, kaloriya):
    conn = sqlite3.connect("kaloriya.db")
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO ovqatlar (user_id, ovqat_nomi, kaloriya)
        VALUES (?, ?, ?)
    """, (user_id, ovqat_nomi, kaloriya))
    conn.commit()
    conn.close()

def bugungi_ovqatlar(user_id):
    conn = sqlite3.connect("kaloriya.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT ovqat_nomi, kaloriya FROM ovqatlar
        WHERE user_id = ? AND sana = date('now')
        ORDER BY id ASC
    """, (user_id,))
    natija = cur.fetchall()
    conn.close()
    return natija

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BOT BUYRUQLARI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ism = update.effective_user.first_name
    foydalanuvchi_saqlash(user_id, ism)
    await update.message.reply_text(
        f"Salom, {ism}! 👋\n\n"
        "Men kaloriya yordamchisiman 🥗\n\n"
        "✍️ Ovqat yozing: '100g guruch'\n"
        "🎯 Maqsad belgilang: /maqsad\n"
        "📊 Bugungi holat: /bugun\n"
        "/help — barcha buyruqlar"
    )

async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 Buyruqlar:\n\n"
        "/start — boshlash\n"
        "/help — yordam\n"
        "/maqsad [son] — kunlik kaloriya maqsadi\n"
        "  Misol: /maqsad 1800\n"
        "/bugun — bugungi kaloriyalar\n\n"
        "✍️ Ovqat nomi yozing — kaloriyasini hisoblayman"
    )

async def maqsad_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ism = update.effective_user.first_name
    foydalanuvchi_saqlash(user_id, ism)

    # /maqsad 1800 — son bor
    if ctx.args and ctx.args[0].isdigit():
        maqsad = int(ctx.args[0])
        if 500 <= maqsad <= 5000:
            maqsad_saqlash(user_id, maqsad)
            await update.message.reply_text(
                f"✅ Kunlik maqsad: {maqsad} kcal\n\n"
                f"Sog'lom ovqatlanish uchun omad! 💪"
            )
        else:
            await update.message.reply_text(
                "⚠️ Maqsad 500 dan 5000 gacha bo'lishi kerak.\n"
                "Misol: /maqsad 2000"
            )
    else:
        # Hozirgi maqsadni ko'rsat
        hozirgi = maqsad_olish(user_id)
        await update.message.reply_text(
            f"🎯 Hozirgi kunlik maqsad: {hozirgi} kcal\n\n"
            "O'zgartirish uchun:\n"
            "/maqsad 1800"
        )

async def bugun_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ism = update.effective_user.first_name
    foydalanuvchi_saqlash(user_id, ism)

    ovqatlar = bugungi_ovqatlar(user_id)
    maqsad = maqsad_olish(user_id)

    if not ovqatlar:
        await update.message.reply_text(
            "📭 Bugun hali hech narsa yemagansiz.\n\n"
            "Ovqat nomini yozing — hisoblayman! 🥗"
        )
        return

    # Ro'yxat va umumiy kaloriya
    jami = sum(k for _, k in ovqatlar)
    qolgan = maqsad - jami

    matn = "📊 Bugungi ovqatlar:\n━━━━━━━━━━━━━━\n"
    for i, (nom, kal) in enumerate(ovqatlar, 1):
        matn += f"{i}. {nom} — {kal} kcal\n"

    matn += f"━━━━━━━━━━━━━━\n"
    matn += f"🔥 Jami: {jami} kcal\n"
    matn += f"🎯 Maqsad: {maqsad} kcal\n"

    if qolgan > 0:
        matn += f"✅ Qolgan: {qolgan} kcal"
        # Progress bar
        foiz = int((jami / maqsad) * 10)
        bar = "🟩" * foiz + "⬜" * (10 - foiz)
        matn += f"\n{bar} {int((jami/maqsad)*100)}%"
    else:
        matn += f"⚠️ Maqsaddan {abs(qolgan)} kcal oshdi!"

    await update.message.reply_text(matn)



async def rasm_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ism = update.effective_user.first_name
    foydalanuvchi_saqlash(user_id, ism)

    await update.message.reply_text("⏳ Rasm tahlil qilinmoqda...")

    try:
        # Rasmni yuklab olamiz
        photo = update.message.photo[-1]
        file = await ctx.bot.get_file(photo.file_id)
        rasm_bytes = bytes(await file.download_as_bytearray())

        prompt = """
Sen kaloriya mutaxassisisan. Rasmda ko'ringan ovqatni tahlil qil.
O'zbek tilida quyidagi formatda javob ber:

🍽 [Ovqat nomi]
━━━━━━━━━━━━━━
🔥 Kaloriya: [son] kcal
💪 Protein: [son] g
🧈 Yog': [son] g
🍞 Uglevod: [son] g
━━━━━━━━━━━━━━
💡 [1-2 qisqa maslahat]

Agar rasm ovqat emas — "Rasmda ovqat ko'rinmayapti" de.
MUHIM: Kaloriya qatorida faqat bitta son bo'lsin.
"""

        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                types.Part.from_bytes(data=rasm_bytes, mime_type="image/jpeg"),
                types.Part.from_text(text=prompt)
            ]
        )

        javob = response.text

        # Kaloriyani bazaga saqlaymiz
        try:
            for qator in javob.split("\n"):
                if "Kaloriya:" in qator:
                    sonlar = [s for s in qator.split() if s.isdigit()]
                    if sonlar:
                        kaloriya = int(sonlar[0])
                        ovqat_saqlash(user_id, "📸 Rasm orqali", kaloriya)
                        break
        except:
            pass

        await update.message.reply_text(javob)

    except Exception as e:
        await update.message.reply_text(f"❌ Xatolik: {e}")



async def matn_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ism = update.effective_user.first_name
    foydalanuvchi_saqlash(user_id, ism)
    foydalanuvchi_matni = update.message.text

    # Kutish xabari
    kutish = await update.message.reply_text("⏳ Hisoblanmoqda...")

    prompt = f"""
Sen kaloriya va ozuqa mutaxassisisan. Foydalanuvchi sening bilan o'zbek tilida gaplashadi.

Foydalanuvchi yozdi: "{foydalanuvchi_matni}"

Agar bu ovqat yoki mahsulot haqida bo'lsa, quyidagi formatda javob ber:

[EMOJI] [Ovqat nomi]
━━━━━━━━━━━━━━
🔥 Kaloriya: [faqat son] kcal
💪 Protein: [son] g
🧈 Yog': [son] g
🍞 Uglevod: [son] g
━━━━━━━━━━━━━━
💡 [1-2 qisqa maslahat]

[EMOJI] tanlash qoidasi:
- Ichimliklar (suv, choy, qahva, sharbat, kola, juice): 🥤
- Mevalar: 🍎
- Sabzavotlar: 🥦
- Go'sht taomlar: 🍖
- Guruch, non, pasta taomlar: 🍚
- Sho'rva, osh, lagmon: 🍜
- Shirinliklar, tort, pechenye: 🍰
- Tuxum taomlar: 🍳
- Sut mahsulotlari: 🥛
- Fast food: 🍔
- Boshqa ovqatlar: 🍽

MUHIM: Kaloriya qatorida faqat bitta son bo'lsin. Masalan: "Kaloriya: 350 kcal"

Agar ovqat bilan bog'liq bo'lmasa — oddiy o'zbek tilida javob ber.
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        javob = response.choices[0].message.content

        # Kaloriyani bazaga saqlaymiz
        try:
            for qator in javob.split("\n"):
                if "Kaloriya:" in qator:
                    sonlar = [s for s in qator.split() if s.isdigit()]
                    if sonlar:
                        kaloriya = int(sonlar[0])
                        ovqat_saqlash(user_id, foydalanuvchi_matni[:50], kaloriya)
                        break
        except:
            pass

        # Kutish xabarini o'chirib, javob yuboramiz
        await kutish.delete()
        await update.message.reply_text(javob)

    except Exception as e:
        await kutish.delete()
        await update.message.reply_text(f"❌ Xatolik: {e}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ISHGA TUSHIRISH
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if __name__ == "__main__":
    baza_yarat()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO, rasm_handler))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("maqsad", maqsad_cmd))
    app.add_handler(CommandHandler("bugun", bugun_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, matn_handler))

    print("Bot ishlamoqda... ✅")
    app.run_polling()