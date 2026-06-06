import os
import sqlite3
import base64
from openai import OpenAI
from groq import Groq
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = os.getenv("TELEGRAM_TOKEN")
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BAZA
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def baza_yarat():
    conn = sqlite3.connect("kaloriya.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS foydalanuvchilar (
            user_id INTEGER PRIMARY KEY,
            ism TEXT,
            kunlik_maqsad INTEGER DEFAULT 2000
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ovqatlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            ovqat_nomi TEXT,
            kaloriya INTEGER,
            sana TEXT DEFAULT (date('now'))
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS suv (
            user_id INTEGER,
            miqdor INTEGER DEFAULT 0,
            sana TEXT DEFAULT (date('now')),
            PRIMARY KEY (user_id, sana)
        )
    """)
    conn.commit()
    conn.close()

def foydalanuvchi_saqlash(user_id, ism):
    conn = sqlite3.connect("kaloriya.db")
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO foydalanuvchilar (user_id, ism) VALUES (?, ?)", (user_id, ism))
    conn.commit()
    conn.close()

def maqsad_saqlash(user_id, maqsad):
    conn = sqlite3.connect("kaloriya.db")
    cur = conn.cursor()
    cur.execute("UPDATE foydalanuvchilar SET kunlik_maqsad = ? WHERE user_id = ?", (maqsad, user_id))
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
    cur.execute("INSERT INTO ovqatlar (user_id, ovqat_nomi, kaloriya) VALUES (?, ?, ?)", (user_id, ovqat_nomi, kaloriya))
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

def suv_olish(user_id):
    conn = sqlite3.connect("kaloriya.db")
    cur = conn.cursor()
    cur.execute("SELECT miqdor FROM suv WHERE user_id = ? AND sana = date('now')", (user_id,))
    natija = cur.fetchone()
    conn.close()
    return natija[0] if natija else 0

def suv_qosh(user_id, miqdor):
    conn = sqlite3.connect("kaloriya.db")
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO suv (user_id, miqdor, sana)
        VALUES (?, ?, date('now'))
        ON CONFLICT(user_id, sana) DO UPDATE SET miqdor = miqdor + ?
    """, (user_id, miqdor, miqdor))
    conn.commit()
    conn.close()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ASOSIY MENYU
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def asosiy_menyu():
    return ReplyKeyboardMarkup([
        ["📊 Bugungi statistika", "🎯 Maqsad belgilash"],
        ["💧 Suv miqdori", "📅 Haftalik hisobot"],
        ["⚙️ Sozlamalar", "❓ Yordam"]
    ], resize_keyboard=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BUYRUQLAR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ism = update.effective_user.first_name
    foydalanuvchi_saqlash(user_id, ism)

    # Rasm yuborish
    try:
        with open("welcome.png", "rb") as rasm:
            await update.message.reply_photo(
                photo=rasm,
                caption=(
                    f"Salom, {ism}! 👋\n\n"
                    "Men kaloriya yordamchisiman 🥗\n\n"
                    "✍️ Ovqat yozing: '100g guruch'\n"
                    "📸 Ovqat rasmi yuboring\n\n"
                    "Quyidagi tugmalardan foydalaning 👇"
                ),
                reply_markup=asosiy_menyu()
            )
    except:
        await update.message.reply_text(
            f"Salom, {ism}! 👋\n\n"
            "Men kaloriya yordamchisiman 🥗\n\n"
            "✍️ Ovqat yozing: '100g guruch'\n"
            "📸 Ovqat rasmi yuboring\n\n"
            "Quyidagi tugmalardan foydalaning 👇",
            reply_markup=asosiy_menyu()
        )

async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 Buyruqlar:\n\n"
        "/start — boshlash\n"
        "/help — yordam\n"
        "/maqsad [son] — kunlik kaloriya maqsadi\n"
        "/bugun — bugungi kaloriyalar\n"
        "/suv — suv miqdori\n"
        "/hafta — haftalik hisobot\n\n"
        "✍️ Matn: '100g osh' yoki '1 ta tuxum'\n"
        "📸 Rasm: ovqat rasmini yuboring",
        reply_markup=asosiy_menyu()
    )

async def maqsad_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ism = update.effective_user.first_name
    foydalanuvchi_saqlash(user_id, ism)
    if ctx.args and ctx.args[0].isdigit():
        maqsad = int(ctx.args[0])
        if 500 <= maqsad <= 5000:
            maqsad_saqlash(user_id, maqsad)
            await update.message.reply_text(
                f"✅ Kunlik maqsad: {maqsad} kcal\n\nSog'lom ovqatlanish uchun omad! 💪",
                reply_markup=asosiy_menyu()
            )
        else:
            await update.message.reply_text("⚠️ Maqsad 500 dan 5000 gacha bo'lishi kerak.\nMisol: /maqsad 2000")
    else:
        hozirgi = maqsad_olish(user_id)
        tugmalar = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("1500 kcal", callback_data="maqsad_1500"),
                InlineKeyboardButton("1800 kcal", callback_data="maqsad_1800"),
            ],
            [
                InlineKeyboardButton("2000 kcal", callback_data="maqsad_2000"),
                InlineKeyboardButton("2500 kcal", callback_data="maqsad_2500"),
            ],
            [InlineKeyboardButton("3000 kcal", callback_data="maqsad_3000")]
        ])
        await update.message.reply_text(
            f"🎯 Hozirgi kunlik maqsad: {hozirgi} kcal\n\n"
            "Yangi maqsad tanlang yoki /maqsad 2000 deb yozing:",
            reply_markup=tugmalar
        )

async def bugun_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ism = update.effective_user.first_name
    foydalanuvchi_saqlash(user_id, ism)
    ovqatlar = bugungi_ovqatlar(user_id)
    maqsad = maqsad_olish(user_id)
    suv = suv_olish(user_id)

    if not ovqatlar:
        await update.message.reply_text(
            "📭 Bugun hali hech narsa yemagansiz.\n\nOvqat nomini yozing yoki rasm yuboring! 🥗",
            reply_markup=asosiy_menyu()
        )
        return

    jami = sum(k for _, k in ovqatlar)
    qolgan = maqsad - jami
    foiz = min(int((jami / maqsad) * 10), 10)
    bar = "🟩" * foiz + "⬜" * (10 - foiz)

    matn = "📊 Bugungi holat:\n━━━━━━━━━━━━━━\n"
    for i, (nom, kal) in enumerate(ovqatlar, 1):
        matn += f"{i}. {nom} — {kal} kcal\n"
    matn += "━━━━━━━━━━━━━━\n"
    matn += f"🔥 Jami: {jami} kcal\n"
    matn += f"🎯 Maqsad: {maqsad} kcal\n"
    if qolgan > 0:
        matn += f"✅ Qolgan: {qolgan} kcal\n"
    else:
        matn += f"⚠️ Maqsaddan {abs(qolgan)} kcal oshdi!\n"
    matn += f"{bar} {int((jami/maqsad)*100)}%\n"
    matn += "━━━━━━━━━━━━━━\n"
    suv_foiz = min(int((suv / 2000) * 10), 10)
    suv_bar = "💧" * suv_foiz + "⬜" * (10 - suv_foiz)
    matn += f"💧 Suv: {suv} ml / 2000 ml\n{suv_bar}"

    await update.message.reply_text(matn, reply_markup=asosiy_menyu())

async def suv_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ism = update.effective_user.first_name
    foydalanuvchi_saqlash(user_id, ism)
    suv = suv_olish(user_id)
    foiz = min(int((suv / 2000) * 10), 10)
    bar = "💧" * foiz + "⬜" * (10 - foiz)
    tugmalar = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💧 200 ml", callback_data="suv_200"),
            InlineKeyboardButton("💧 300 ml", callback_data="suv_300"),
            InlineKeyboardButton("💧 500 ml", callback_data="suv_500"),
        ],
        [InlineKeyboardButton("💧 1 litr", callback_data="suv_1000")]
    ])
    await update.message.reply_text(
        f"💧 Bugungi suv: {suv} ml / 2000 ml\n"
        f"{bar} {int((suv/2000)*100)}%\n\n"
        "Qancha suv ichdingiz?",
        reply_markup=tugmalar
    )

async def hafta_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conn = sqlite3.connect("kaloriya.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT sana, SUM(kaloriya) FROM ovqatlar
        WHERE user_id = ? AND sana >= date('now', '-7 days')
        GROUP BY sana ORDER BY sana ASC
    """, (user_id,))
    natija = cur.fetchall()
    conn.close()

    if not natija:
        await update.message.reply_text(
            "📅 Oxirgi 7 kunda ma'lumot yo'q.\n\nOvqat yozing — statistika to'plana boshlaydi!",
            reply_markup=asosiy_menyu()
        )
        return

    maqsad = maqsad_olish(user_id)
    matn = "📅 Haftalik hisobot:\n━━━━━━━━━━━━━━\n"
    jami = 0
    for sana, kaloriya in natija:
        foiz = min(int((kaloriya / maqsad) * 10), 10)
        bar = "🟩" * foiz + "⬜" * (10 - foiz)
        matn += f"{sana}:\n{bar} {kaloriya} kcal\n"
        jami += kaloriya

    ortacha = jami // len(natija)
    matn += f"━━━━━━━━━━━━━━\n📊 O'rtacha: {ortacha} kcal/kun"
    await update.message.reply_text(matn, reply_markup=asosiy_menyu())

async def sozlamalar_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    maqsad = maqsad_olish(update.effective_user.id)
    tugmalar = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"🎯 Kaloriya maqsadi: {maqsad} kcal", callback_data="sozlama_kaloriya")],
        [InlineKeyboardButton("💧 Suv maqsadi: 2000 ml", callback_data="sozlama_suv")],
    ])
    await update.message.reply_text("⚙️ Sozlamalar:", reply_markup=tugmalar)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CALLBACK HANDLER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def callback_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    # Suv
    if query.data.startswith("suv_"):
        miqdor = int(query.data.split("_")[1])
        suv_qosh(user_id, miqdor)
        suv = suv_olish(user_id)
        foiz = min(int((suv / 2000) * 10), 10)
        bar = "💧" * foiz + "⬜" * (10 - foiz)
        tugmalar = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("💧 200 ml", callback_data="suv_200"),
                InlineKeyboardButton("💧 300 ml", callback_data="suv_300"),
                InlineKeyboardButton("💧 500 ml", callback_data="suv_500"),
            ],
            [InlineKeyboardButton("💧 1 litr", callback_data="suv_1000")]
        ])
        await query.edit_message_text(
            f"✅ {miqdor} ml qo'shildi!\n\n"
            f"💧 Bugungi suv: {suv} ml / 2000 ml\n"
            f"{bar} {int((suv/2000)*100)}%\n\n"
            "Yana qo'shish:",
            reply_markup=tugmalar
        )

    # Maqsad
    elif query.data.startswith("maqsad_"):
        maqsad = int(query.data.split("_")[1])
        maqsad_saqlash(user_id, maqsad)
        await query.edit_message_text(f"✅ Kunlik maqsad: {maqsad} kcal ga o'zgartirildi! 💪")

    # Ovqat qo'shish
    elif query.data.startswith("qosh_"):
        qismlar = query.data.split("_", 2)
        kaloriya = int(qismlar[1])
        ovqat_nomi = qismlar[2] if len(qismlar) > 2 else "Noma'lum"
        ovqat_saqlash(user_id, ovqat_nomi, kaloriya)

        maqsad = maqsad_olish(user_id)
        ovqatlar = bugungi_ovqatlar(user_id)
        jami = sum(k for _, k in ovqatlar)
        qolgan = maqsad - jami
        foiz = min(int((jami / maqsad) * 10), 10)
        bar = "🟩" * foiz + "⬜" * (10 - foiz)

        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text(
            f"✅ Ro'yxatga qo'shildi!\n\n"
            f"🔥 Bugungi jami: {jami} kcal\n"
            f"🎯 Maqsad: {maqsad} kcal\n"
            f"{'✅ Qolgan: ' + str(qolgan) + ' kcal' if qolgan > 0 else '⚠️ Maqsaddan ' + str(abs(qolgan)) + ' kcal oshdi!'}\n"
            f"{bar} {int((jami/maqsad)*100)}%",
            reply_markup=asosiy_menyu()
        )

    elif query.data == "qoshma":
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text("❌ Qo'shilmadi.", reply_markup=asosiy_menyu())

    elif query.data == "sozlama_kaloriya":
        await query.edit_message_text("🎯 Yangi maqsad yozing:\nMisol: /maqsad 2000")

    elif query.data == "sozlama_suv":
        await query.edit_message_text("💧 Suv maqsadi hozircha 2000 ml ga o'rnatilgan.")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MATN HANDLER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def matn_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ism = update.effective_user.first_name
    foydalanuvchi_saqlash(user_id, ism)
    foydalanuvchi_matni = update.message.text

    # Tugma bosilganda
    if foydalanuvchi_matni == "📊 Bugungi statistika":
        await bugun_cmd(update, ctx)
        return
    if foydalanuvchi_matni == "🎯 Maqsad belgilash":
        await maqsad_cmd(update, ctx)
        return
    if foydalanuvchi_matni == "💧 Suv miqdori":
        await suv_cmd(update, ctx)
        return
    if foydalanuvchi_matni == "📅 Haftalik hisobot":
        await hafta_cmd(update, ctx)
        return
    if foydalanuvchi_matni == "⚙️ Sozlamalar":
        await sozlamalar_cmd(update, ctx)
        return
    if foydalanuvchi_matni == "❓ Yordam":
        await help_cmd(update, ctx)
        return

    kutish = await update.message.reply_text("⏳ Hisoblanmoqda...")

    prompt = f"""Sen kaloriya va ozuqa mutaxassisisan. O'zbek tilida javob ber.

Foydalanuvchi yozdi: "{foydalanuvchi_matni}"

Agar bu ovqat yoki mahsulot haqida bo'lsa:

[EMOJI] [Ovqat nomi]
━━━━━━━━━━━━━━
🔥 Kaloriya: [son] kcal
💪 Protein: [son] g
🧈 Yog': [son] g
🍞 Uglevod: [son] g
━━━━━━━━━━━━━━
💡 [1-2 qisqa maslahat]

EMOJI: Ichimlik=🥤 Meva=🍎 Sabzavot=🥦 Go'sht=🍖 Guruch/osh=🍚 Sho'rva=🍜 Shirinlik=🍰 Tuxum=🍳 Fastfood=🍔 Boshqa=🍽
MUHIM: Kaloriya qatorida faqat bitta son.
Ovqat emas bo'lsa — oddiy o'zbek tilida javob ber."""

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        javob = response.choices[0].message.content

        # Kaloriyani ajratib olamiz
        kaloriya = 0
        try:
            for qator in javob.split("\n"):
                if "Kaloriya:" in qator:
                    sonlar = [s for s in qator.split() if s.isdigit()]
                    if sonlar:
                        kaloriya = int(sonlar[0])
                        break
        except:
            pass

        await kutish.delete()

        # Kaloriya topilsa — tasdiqlash tugmasi
        if kaloriya > 0:
            tugmalar = InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    f"✅ Ro'yxatga qo'shish ({kaloriya} kcal)",
                    callback_data=f"qosh_{kaloriya}_{foydalanuvchi_matni[:40]}"
                )],
                [InlineKeyboardButton("❌ Qo'shmaslik", callback_data="qoshma")]
            ])
            await update.message.reply_text(javob, reply_markup=tugmalar)
        else:
            await update.message.reply_text(javob, reply_markup=asosiy_menyu())

    except Exception as e:
        await kutish.delete()
        await update.message.reply_text("❌ Xatolik yuz berdi. Qayta urinib ko'ring.")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RASM HANDLER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def rasm_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ism = update.effective_user.first_name
    foydalanuvchi_saqlash(user_id, ism)
    kutish = await update.message.reply_text("⏳ Rasm tahlil qilinmoqda...")

    try:
        photo = update.message.photo[-1]
        file = await ctx.bot.get_file(photo.file_id)
        rasm_bytes = await file.download_as_bytearray()
        rasm_base64 = base64.b64encode(rasm_bytes).decode("utf-8")

        prompt = """Sen kaloriya mutaxassisisan. O'zbek tilida javob ber.
Rasmda ko'ringan ovqatni tahlil qil:

[EMOJI] [Ovqat nomi]
━━━━━━━━━━━━━━
🔥 Kaloriya: [son] kcal
💪 Protein: [son] g
🧈 Yog': [son] g
🍞 Uglevod: [son] g
━━━━━━━━━━━━━━
💡 [1-2 qisqa maslahat]

EMOJI: Ichimlik=🥤 Meva=🍎 Sabzavot=🥦 Go'sht=🍖 Guruch/osh=🍚 Sho'rva=🍜 Shirinlik=🍰 Tuxum=🍳 Fastfood=🍔 Boshqa=🍽
Ovqat ko'rinmasa — "Rasmda ovqat ko'rinmayapti 🤔" de."""

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{rasm_base64}"}},
                    {"type": "text", "text": prompt}
                ]
            }],
            max_tokens=500
        )
        javob = response.choices[0].message.content

        # Kaloriyani ajratib olamiz
        kaloriya = 0
        try:
            for qator in javob.split("\n"):
                if "Kaloriya:" in qator:
                    sonlar = [s for s in qator.split() if s.isdigit()]
                    if sonlar:
                        kaloriya = int(sonlar[0])
                        break
        except:
            pass

        await kutish.delete()

        # Kaloriya topilsa — tasdiqlash tugmasi
        if kaloriya > 0:
            tugmalar = InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    f"✅ Ro'yxatga qo'shish ({kaloriya} kcal)",
                    callback_data=f"qosh_{kaloriya}_📸 Rasm orqali"
                )],
                [InlineKeyboardButton("❌ Qo'shmaslik", callback_data="qoshma")]
            ])
            await update.message.reply_text(javob, reply_markup=tugmalar)
        else:
            await update.message.reply_text(javob, reply_markup=asosiy_menyu())

    except Exception as e:
        await kutish.delete()
        if "insufficient_quota" in str(e) or "429" in str(e):
            await update.message.reply_text(
                "😔 Hozirda rasm orqali tahlil qilish vaqtincha mavjud emas.\n\n"
                "✍️ Ovqat nomini yozib yuboring:\n"
                "Misol: '1 piyola osh' yoki '100g tovuq'",
                reply_markup=asosiy_menyu()
            )
        else:
            await update.message.reply_text("❌ Xatolik yuz berdi. Qayta urinib ko'ring.")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ISHGA TUSHIRISH
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if __name__ == "__main__":
    baza_yarat()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("maqsad", maqsad_cmd))
    app.add_handler(CommandHandler("bugun", bugun_cmd))
    app.add_handler(CommandHandler("suv", suv_cmd))
    app.add_handler(CommandHandler("hafta", hafta_cmd))
    app.add_handler(CommandHandler("sozlamalar", sozlamalar_cmd))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.PHOTO, rasm_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, matn_handler))
    print("Bot ishlamoqda... ✅")
    app.run_polling()