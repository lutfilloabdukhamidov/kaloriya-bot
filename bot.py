import os
import sqlite3
import base64
from openai import OpenAI
from groq import Groq
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = os.getenv("TELEGRAM_TOKEN")
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TARJIMALAR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MATN = {
    'uz': {
        'salom': "Salom, {ism}! 👋\n\nMen kaloriya yordamchisiman 🥗\n\n✍️ Ovqat yozing: '100g guruch'\n📸 Ovqat rasmi yuboring\n\nQuyidagi tugmalardan foydalaning 👇",
        'til_tanlash': "🌍 Tilni tanlang:",
        'jins_savol': "👤 Jinsingizni tanlang:",
        'erkak': "👨 Erkak",
        'ayol': "👩 Ayol",
        'yosh_savol': "🎂 Yoshingizni yozing:\nMisol: 25",
        'boy_savol': "📏 Bo'yingizni yozing (sm):\nMisol: 175",
        'vazn_savol': "⚖️ Vazningizni yozing (kg):\nMisol: 70",
        'maqsad_savol': "🎯 Maqsadingizni tanlang:",
        'maqsad_1': "🔥 Vazn yo'qotish",
        'maqsad_2': "💪 Vazn yig'ish",
        'maqsad_3': "⚖️ Vaznni saqlash",
        'maqsad_4': "🏃 Sog'lom turmush",
        'tasdiq': "✅ Tasdiqlash",
        'bekor': "❌ Bekor qilish",
        'profil_tekshir': "📋 Ma'lumotlaringiz:\n\n👤 Jins: {jins}\n🎂 Yosh: {yosh}\n📏 Bo'y: {boy} sm\n⚖️ Vazn: {vazn} kg\n🎯 Maqsad: {maqsad}\n\n🔥 Kunlik kaloriya normasi: {kaloriya} kcal\n\nTo'g'rimi?",
        'rahmat': "🎉 Tabriklayman, {ism}!\n\nSizning kunlik kaloriya normangiz: {kaloriya} kcal\n\nEndi ovqat yozishni boshlang! 🥗",
        'xato_yosh': "⚠️ Iltimos, faqat son kiriting.\nMisol: 25",
        'xato_boy': "⚠️ Iltimos, faqat son kiriting.\nMisol: 175",
        'xato_vazn': "⚠️ Iltimos, faqat son kiriting.\nMisol: 70",
        'hisob': "⏳ Hisoblanmoqda...",
        'rasm_hisob': "⏳ Rasm tahlil qilinmoqda...",
        'bugun_bosh': "📭 Bugun hali hech narsa yemagansiz.\n\nOvqat nomini yozing yoki rasm yuboring! 🥗",
        'bugun_sarlavha': "📊 Bugungi holat:\n━━━━━━━━━━━━━━\n",
        'hafta_bosh': "📅 Oxirgi 7 kunda ma'lumot yo'q.\n\nOvqat yozing — statistika to'plana boshlaydi!",
        'qoshildi': "✅ Ro'yxatga qo'shildi!\n\n🔥 Bugungi jami: {jami} kcal\n🎯 Maqsad: {maqsad} kcal\n{holat}\n{bar} {foiz}%",
        'qoshilmadi': "❌ Qo'shilmadi.",
        'maqsad_ozgardi': "✅ Kunlik maqsad: {maqsad} kcal ga o'zgartirildi! 💪",
        'rasm_xato': "😔 Hozirda rasm orqali tahlil qilish vaqtincha mavjud emas.\n\n✍️ Ovqat nomini yozib yuboring:\nMisol: '1 piyola osh' yoki '100g tovuq'",
        'umumiy_xato': "❌ Xatolik yuz berdi. Qayta urinib ko'ring.",
        'qosh_tugma': "✅ Ro'yxatga qo'shish ({kaloriya} kcal)",
        'qoshma_tugma': "❌ Qo'shmaslik",
        'qolgan': "✅ Qolgan: {qolgan} kcal",
        'oshdi': "⚠️ Maqsaddan {qolgan} kcal oshdi!",
        'sozlamalar': "⚙️ Sozlamalar:",
        'kaloriya_maqsad': "🎯 Kaloriya maqsadi: {maqsad} kcal",
        'suv_maqsad': "💧 Suv maqsadi: 2000 ml",
        'profil_yangi': "👤 Profilni yangilash",
        'suv_qoshildi': "✅ {miqdor} ml qo'shildi!\n\n💧 Bugungi suv: {suv} ml / 2000 ml\n{bar} {foiz}%\n\nYana qo'shish:",
        'suv_savol': "💧 Bugungi suv: {suv} ml / 2000 ml\n{bar} {foiz}%\n\nQancha suv ichdingiz?",
        'yordam': "📋 Buyruqlar:\n\n/start — boshlash\n/help — yordam\n/maqsad [son] — kunlik kaloriya maqsadi\n/bugun — bugungi kaloriyalar\n/suv — suv miqdori\n/hafta — haftalik hisobot\n\n✍️ Matn: '100g osh' yoki '1 ta tuxum'\n📸 Rasm: ovqat rasmini yuboring",
        'menu': [
            ["📊 Bugungi statistika", "🎯 Maqsad belgilash"],
            ["💧 Suv miqdori", "📅 Haftalik hisobot"],
            ["⚙️ Sozlamalar", "❓ Yordam"]
        ],
        'ai_prompt': 'Sen kaloriya va ozuqa mutaxassisisan. O\'zbek tilida javob ber.\n\nFoydalanuvchi yozdi: "{matn}"\n\nAgar bu ovqat yoki mahsulot haqida bo\'lsa:\n\n[EMOJI] [Ovqat nomi]\n━━━━━━━━━━━━━━\n🔥 Kaloriya: [son] kcal\n💪 Protein: [son] g\n🧈 Yog\': [son] g\n🍞 Uglevod: [son] g\n━━━━━━━━━━━━━━\n💡 [1-2 qisqa maslahat]\n\nEMOJI: Ichimlik=🥤 Meva=🍎 Sabzavot=🥦 Go\'sht=🍖 Guruch/osh=🍚 Sho\'rva=🍜 Shirinlik=🍰 Tuxum=🍳 Fastfood=🍔 Boshqa=🍽\nMUHIM: Kaloriya qatorida faqat bitta son.\nOvqat emas bo\'lsa — oddiy o\'zbek tilida javob ber.',
    },
    'ru': {
        'salom': "Привет, {ism}! 👋\n\nЯ ваш помощник по калориям 🥗\n\n✍️ Напишите блюдо: '100г риса'\n📸 Отправьте фото еды\n\nИспользуйте кнопки ниже 👇",
        'til_tanlash': "🌍 Выберите язык:",
        'jins_savol': "👤 Выберите пол:",
        'erkak': "👨 Мужской",
        'ayol': "👩 Женский",
        'yosh_savol': "🎂 Введите ваш возраст:\nПример: 25",
        'boy_savol': "📏 Введите ваш рост (см):\nПример: 175",
        'vazn_savol': "⚖️ Введите ваш вес (кг):\nПример: 70",
        'maqsad_savol': "🎯 Выберите вашу цель:",
        'maqsad_1': "🔥 Похудение",
        'maqsad_2': "💪 Набор массы",
        'maqsad_3': "⚖️ Поддержание веса",
        'maqsad_4': "🏃 Здоровый образ жизни",
        'tasdiq': "✅ Подтвердить",
        'bekor': "❌ Отмена",
        'profil_tekshir': "📋 Ваши данные:\n\n👤 Пол: {jins}\n🎂 Возраст: {yosh}\n📏 Рост: {boy} см\n⚖️ Вес: {vazn} кг\n🎯 Цель: {maqsad}\n\n🔥 Дневная норма калорий: {kaloriya} ккал\n\nВсё верно?",
        'rahmat': "🎉 Поздравляю, {ism}!\n\nВаша дневная норма калорий: {kaloriya} ккал\n\nНачните записывать питание! 🥗",
        'xato_yosh': "⚠️ Пожалуйста, введите только цифры.\nПример: 25",
        'xato_boy': "⚠️ Пожалуйста, введите только цифры.\nПример: 175",
        'xato_vazn': "⚠️ Пожалуйста, введите только цифры.\nПример: 70",
        'hisob': "⏳ Подсчёт...",
        'rasm_hisob': "⏳ Анализ фото...",
        'bugun_bosh': "📭 Сегодня вы ещё ничего не ели.\n\nНапишите название блюда или отправьте фото! 🥗",
        'bugun_sarlavha': "📊 Сегодня:\n━━━━━━━━━━━━━━\n",
        'hafta_bosh': "📅 За последние 7 дней данных нет.\n\nЗаписывайте еду — статистика начнёт накапливаться!",
        'qoshildi': "✅ Добавлено в список!\n\n🔥 Итого за сегодня: {jami} ккал\n🎯 Цель: {maqsad} ккал\n{holat}\n{bar} {foiz}%",
        'qoshilmadi': "❌ Не добавлено.",
        'maqsad_ozgardi': "✅ Дневная цель изменена: {maqsad} ккал! 💪",
        'rasm_xato': "😔 Анализ фото временно недоступен.\n\n✍️ Напишите название блюда:\nПример: '1 тарелка плова' или '100г курицы'",
        'umumiy_xato': "❌ Произошла ошибка. Попробуйте ещё раз.",
        'qosh_tugma': "✅ Добавить в список ({kaloriya} ккал)",
        'qoshma_tugma': "❌ Не добавлять",
        'qolgan': "✅ Осталось: {qolgan} ккал",
        'oshdi': "⚠️ Превышение на {qolgan} ккал!",
        'sozlamalar': "⚙️ Настройки:",
        'kaloriya_maqsad': "🎯 Цель калорий: {maqsad} ккал",
        'suv_maqsad': "💧 Цель воды: 2000 мл",
        'profil_yangi': "👤 Обновить профиль",
        'suv_qoshildi': "✅ {miqdor} мл добавлено!\n\n💧 Вода сегодня: {suv} мл / 2000 мл\n{bar} {foiz}%\n\nДобавить ещё:",
        'suv_savol': "💧 Вода сегодня: {suv} мл / 2000 мл\n{bar} {foiz}%\n\nСколько воды выпили?",
        'yordam': "📋 Команды:\n\n/start — начало\n/help — помощь\n/maqsad [число] — дневная цель калорий\n/bugun — калории сегодня\n/suv — вода\n/hafta — недельный отчёт\n\n✍️ Текст: '100г плова' или '1 яйцо'\n📸 Фото: отправьте фото еды",
        'menu': [
            ["📊 Статистика сегодня", "🎯 Установить цель"],
            ["💧 Вода", "📅 Отчёт за неделю"],
            ["⚙️ Настройки", "❓ Помощь"]
        ],
        'ai_prompt': 'Ты эксперт по калориям и питанию. Отвечай на русском языке.\n\nПользователь написал: "{matn}"\n\nЕсли это еда или продукт:\n\n[EMOJI] [Название блюда]\n━━━━━━━━━━━━━━\n🔥 Калории: [число] ккал\n💪 Белки: [число] г\n🧈 Жиры: [число] г\n🍞 Углеводы: [число] г\n━━━━━━━━━━━━━━\n💡 [1-2 коротких совета]\n\nEMOJI: Напиток=🥤 Фрукт=🍎 Овощ=🥦 Мясо=🍖 Рис/плов=🍚 Суп=🍜 Сладкое=🍰 Яйцо=🍳 Фастфуд=🍔 Другое=🍽\nВАЖНО: В строке калорий только одно число.\nЕсли это не еда — ответь обычно на русском.',
    },
    'en': {
        'salom': "Hello, {ism}! 👋\n\nI'm your calorie assistant 🥗\n\n✍️ Type a food: '100g rice'\n📸 Send a food photo\n\nUse the buttons below 👇",
        'til_tanlash': "🌍 Choose your language:",
        'jins_savol': "👤 Select your gender:",
        'erkak': "👨 Male",
        'ayol': "👩 Female",
        'yosh_savol': "🎂 Enter your age:\nExample: 25",
        'boy_savol': "📏 Enter your height (cm):\nExample: 175",
        'vazn_savol': "⚖️ Enter your weight (kg):\nExample: 70",
        'maqsad_savol': "🎯 Choose your goal:",
        'maqsad_1': "🔥 Lose weight",
        'maqsad_2': "💪 Gain muscle",
        'maqsad_3': "⚖️ Maintain weight",
        'maqsad_4': "🏃 Healthy lifestyle",
        'tasdiq': "✅ Confirm",
        'bekor': "❌ Cancel",
        'profil_tekshir': "📋 Your profile:\n\n👤 Gender: {jins}\n🎂 Age: {yosh}\n📏 Height: {boy} cm\n⚖️ Weight: {vazn} kg\n🎯 Goal: {maqsad}\n\n🔥 Daily calorie norm: {kaloriya} kcal\n\nIs this correct?",
        'rahmat': "🎉 Congratulations, {ism}!\n\nYour daily calorie norm: {kaloriya} kcal\n\nStart tracking your meals! 🥗",
        'xato_yosh': "⚠️ Please enter numbers only.\nExample: 25",
        'xato_boy': "⚠️ Please enter numbers only.\nExample: 175",
        'xato_vazn': "⚠️ Please enter numbers only.\nExample: 70",
        'hisob': "⏳ Calculating...",
        'rasm_hisob': "⏳ Analyzing photo...",
        'bugun_bosh': "📭 You haven't eaten anything today.\n\nType a food name or send a photo! 🥗",
        'bugun_sarlavha': "📊 Today's summary:\n━━━━━━━━━━━━━━\n",
        'hafta_bosh': "📅 No data for the last 7 days.\n\nStart logging meals to build stats!",
        'qoshildi': "✅ Added to list!\n\n🔥 Today's total: {jami} kcal\n🎯 Goal: {maqsad} kcal\n{holat}\n{bar} {foiz}%",
        'qoshilmadi': "❌ Not added.",
        'maqsad_ozgardi': "✅ Daily goal updated: {maqsad} kcal! 💪",
        'rasm_xato': "😔 Photo analysis is temporarily unavailable.\n\n✍️ Type the food name:\nExample: '1 bowl of rice' or '100g chicken'",
        'umumiy_xato': "❌ An error occurred. Please try again.",
        'qosh_tugma': "✅ Add to list ({kaloriya} kcal)",
        'qoshma_tugma': "❌ Don't add",
        'qolgan': "✅ Remaining: {qolgan} kcal",
        'oshdi': "⚠️ Exceeded by {qolgan} kcal!",
        'sozlamalar': "⚙️ Settings:",
        'kaloriya_maqsad': "🎯 Calorie goal: {maqsad} kcal",
        'suv_maqsad': "💧 Water goal: 2000 ml",
        'profil_yangi': "👤 Update profile",
        'suv_qoshildi': "✅ {miqdor} ml added!\n\n💧 Water today: {suv} ml / 2000 ml\n{bar} {foiz}%\n\nAdd more:",
        'suv_savol': "💧 Water today: {suv} ml / 2000 ml\n{bar} {foiz}%\n\nHow much water did you drink?",
        'yordam': "📋 Commands:\n\n/start — start\n/help — help\n/maqsad [number] — set daily calorie goal\n/bugun — today's calories\n/suv — water tracker\n/hafta — weekly report\n\n✍️ Text: '100g rice' or '1 egg'\n📸 Photo: send a food photo",
        'menu': [
            ["📊 Today's stats", "🎯 Set goal"],
            ["💧 Water", "📅 Weekly report"],
            ["⚙️ Settings", "❓ Help"]
        ],
        'ai_prompt': 'You are a calorie and nutrition expert. Reply in English.\n\nUser wrote: "{matn}"\n\nIf this is food or a product:\n\n[EMOJI] [Food name]\n━━━━━━━━━━━━━━\n🔥 Calories: [number] kcal\n💪 Protein: [number] g\n🧈 Fat: [number] g\n🍞 Carbs: [number] g\n━━━━━━━━━━━━━━\n💡 [1-2 short tips]\n\nEMOJI: Drink=🥤 Fruit=🍎 Veggie=🥦 Meat=🍖 Rice=🍚 Soup=🍜 Sweet=🍰 Egg=🍳 Fastfood=🍔 Other=🍽\nIMPORTANT: Only one number in the calorie line.\nIf not food — reply normally in English.',
    }
}

def t(user_id, kalit, **kwargs):
    """Foydalanuvchi tilidagi matnni qaytaradi"""
    til = til_olish(user_id)
    matn = MATN.get(til, MATN['uz']).get(kalit, MATN['uz'].get(kalit, kalit))
    if kwargs:
        try:
            return matn.format(**kwargs)
        except:
            return matn
    return matn

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
            til TEXT DEFAULT 'uz',
            jins TEXT,
            yosh INTEGER,
            boy INTEGER,
            vazn REAL,
            maqsad TEXT,
            bmr_kaloriya INTEGER DEFAULT 2000,
            kunlik_maqsad INTEGER DEFAULT 2000,
            royxatdan INTEGER DEFAULT 0
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
    # Conversation state
    cur.execute("""
        CREATE TABLE IF NOT EXISTS holat (
            user_id INTEGER PRIMARY KEY,
            qadam TEXT,
            vaqtinchalik TEXT
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

def til_olish(user_id):
    conn = sqlite3.connect("kaloriya.db")
    cur = conn.cursor()
    cur.execute("SELECT til FROM foydalanuvchilar WHERE user_id = ?", (user_id,))
    natija = cur.fetchone()
    conn.close()
    return natija[0] if natija and natija[0] else 'uz'

def til_saqlash(user_id, til):
    conn = sqlite3.connect("kaloriya.db")
    cur = conn.cursor()
    cur.execute("UPDATE foydalanuvchilar SET til = ? WHERE user_id = ?", (til, user_id))
    conn.commit()
    conn.close()

def profil_saqlash(user_id, jins, yosh, boy, vazn, maqsad, bmr):
    conn = sqlite3.connect("kaloriya.db")
    cur = conn.cursor()
    cur.execute("""
        UPDATE foydalanuvchilar
        SET jins=?, yosh=?, boy=?, vazn=?, maqsad=?,
            bmr_kaloriya=?, kunlik_maqsad=?, royxatdan=1
        WHERE user_id=?
    """, (jins, yosh, boy, vazn, maqsad, bmr, bmr, user_id))
    conn.commit()
    conn.close()

def royxatdan_bormi(user_id):
    conn = sqlite3.connect("kaloriya.db")
    cur = conn.cursor()
    cur.execute("SELECT royxatdan FROM foydalanuvchilar WHERE user_id = ?", (user_id,))
    natija = cur.fetchone()
    conn.close()
    return natija and natija[0] == 1

def holat_saqlash(user_id, qadam, vaqtinchalik=""):
    conn = sqlite3.connect("kaloriya.db")
    cur = conn.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO holat (user_id, qadam, vaqtinchalik)
        VALUES (?, ?, ?)
    """, (user_id, qadam, vaqtinchalik))
    conn.commit()
    conn.close()

def holat_olish(user_id):
    conn = sqlite3.connect("kaloriya.db")
    cur = conn.cursor()
    cur.execute("SELECT qadam, vaqtinchalik FROM holat WHERE user_id = ?", (user_id,))
    natija = cur.fetchone()
    conn.close()
    return natija if natija else (None, "")

def holat_ochir(user_id):
    conn = sqlite3.connect("kaloriya.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM holat WHERE user_id = ?", (user_id,))
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
    cur.execute("INSERT INTO ovqatlar (user_id, ovqat_nomi, kaloriya) VALUES (?, ?, ?)",
                (user_id, ovqat_nomi, kaloriya))
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
# BMR HISOBLASH
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def bmr_hisob(jins, yosh, boy, vazn, maqsad):
    if jins == 'erkak':
        bmr = 88.36 + (13.4 * vazn) + (4.8 * boy) - (5.7 * yosh)
    else:
        bmr = 447.6 + (9.2 * vazn) + (3.1 * boy) - (4.3 * yosh)

    # Maqsadga qarab o'zgartirish
    if 'yo\'qotish' in maqsad or 'похуд' in maqsad or 'lose' in maqsad:
        bmr = bmr * 0.85
    elif 'yig\'ish' in maqsad or 'набор' in maqsad or 'gain' in maqsad:
        bmr = bmr * 1.15

    return int(bmr)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MENYU
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def asosiy_menyu(user_id):
    menu_items = t(user_id, 'menu')
    return ReplyKeyboardMarkup(menu_items, resize_keyboard=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RO'YXATDAN O'TISH
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def til_tanlash_yuborish(update, user_id):
    tugmalar = InlineKeyboardMarkup([[
        InlineKeyboardButton("🇺🇿 O'zbek", callback_data="til_uz"),
        InlineKeyboardButton("🇷🇺 Русский", callback_data="til_ru"),
        InlineKeyboardButton("🇬🇧 English", callback_data="til_en"),
    ]])
    await update.message.reply_text(
        "🌍 Tilni tanlang / Выберите язык / Choose language:",
        reply_markup=tugmalar
    )

async def jins_savol_yuborish(update_or_query, user_id, is_callback=False):
    tugmalar = InlineKeyboardMarkup([[
        InlineKeyboardButton(t(user_id, 'erkak'), callback_data="jins_erkak"),
        InlineKeyboardButton(t(user_id, 'ayol'), callback_data="jins_ayol"),
    ]])
    if is_callback:
        await update_or_query.message.reply_text(
            t(user_id, 'jins_savol'), reply_markup=tugmalar
        )
    else:
        await update_or_query.message.reply_text(
            t(user_id, 'jins_savol'), reply_markup=tugmalar
        )

async def maqsad_savol_yuborish(update_or_query, user_id, is_callback=False):
    tugmalar = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(t(user_id, 'maqsad_1'), callback_data="maqsad_tur_1"),
            InlineKeyboardButton(t(user_id, 'maqsad_2'), callback_data="maqsad_tur_2"),
        ],
        [
            InlineKeyboardButton(t(user_id, 'maqsad_3'), callback_data="maqsad_tur_3"),
            InlineKeyboardButton(t(user_id, 'maqsad_4'), callback_data="maqsad_tur_4"),
        ],
    ])
    if is_callback:
        await update_or_query.message.reply_text(
            t(user_id, 'maqsad_savol'), reply_markup=tugmalar
        )
    else:
        await update_or_query.message.reply_text(
            t(user_id, 'maqsad_savol'), reply_markup=tugmalar
        )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BUYRUQLAR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ism = update.effective_user.first_name
    foydalanuvchi_saqlash(user_id, ism)
    holat_ochir(user_id)

    if royxatdan_bormi(user_id):
        # Allaqachon ro'yxatdan o'tgan
        try:
            with open("welcome.png", "rb") as rasm:
                await update.message.reply_photo(
                    photo=rasm,
                    caption=t(user_id, 'salom', ism=ism),
                    reply_markup=asosiy_menyu(user_id)
                )
        except:
            await update.message.reply_text(
                t(user_id, 'salom', ism=ism),
                reply_markup=asosiy_menyu(user_id)
            )
    else:
        # Yangi foydalanuvchi — til tanlash
        await til_tanlash_yuborish(update, user_id)

async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text(
        t(user_id, 'yordam'),
        reply_markup=asosiy_menyu(user_id)
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
                t(user_id, 'maqsad_ozgardi', maqsad=maqsad),
                reply_markup=asosiy_menyu(user_id)
            )
        else:
            await update.message.reply_text("⚠️ 500 – 5000 oralig'ida bo'lishi kerak.")
    else:
        hozirgi = maqsad_olish(user_id)
        tugmalar = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("1500 kcal", callback_data="kaloriya_maqsad_1500"),
                InlineKeyboardButton("1800 kcal", callback_data="kaloriya_maqsad_1800"),
            ],
            [
                InlineKeyboardButton("2000 kcal", callback_data="kaloriya_maqsad_2000"),
                InlineKeyboardButton("2500 kcal", callback_data="kaloriya_maqsad_2500"),
            ],
            [InlineKeyboardButton("3000 kcal", callback_data="kaloriya_maqsad_3000")]
        ])
        await update.message.reply_text(
            t(user_id, 'kaloriya_maqsad', maqsad=hozirgi) + "\n\nYangi tanlang:",
            reply_markup=tugmalar
        )

async def bugun_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    foydalanuvchi_saqlash(user_id, update.effective_user.first_name)
    ovqatlar = bugungi_ovqatlar(user_id)
    maqsad = maqsad_olish(user_id)
    suv = suv_olish(user_id)

    if not ovqatlar:
        await update.message.reply_text(
            t(user_id, 'bugun_bosh'),
            reply_markup=asosiy_menyu(user_id)
        )
        return

    jami = sum(k for _, k in ovqatlar)
    qolgan = maqsad - jami
    foiz = min(int((jami / maqsad) * 10), 10)
    bar = "🟩" * foiz + "⬜" * (10 - foiz)

    matn = t(user_id, 'bugun_sarlavha')
    for i, (nom, kal) in enumerate(ovqatlar, 1):
        matn += f"{i}. {nom} — {kal} kcal\n"
    matn += "━━━━━━━━━━━━━━\n"
    matn += f"🔥 {jami} kcal\n"
    matn += f"🎯 {maqsad} kcal\n"
    if qolgan > 0:
        matn += t(user_id, 'qolgan', qolgan=qolgan) + "\n"
    else:
        matn += t(user_id, 'oshdi', qolgan=abs(qolgan)) + "\n"
    matn += f"{bar} {int((jami/maqsad)*100)}%\n"
    matn += "━━━━━━━━━━━━━━\n"
    suv_foiz = min(int((suv / 2000) * 10), 10)
    suv_bar = "💧" * suv_foiz + "⬜" * (10 - suv_foiz)
    matn += f"💧 {suv} ml / 2000 ml\n{suv_bar}"

    await update.message.reply_text(matn, reply_markup=asosiy_menyu(user_id))

async def suv_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    foydalanuvchi_saqlash(user_id, update.effective_user.first_name)
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
        t(user_id, 'suv_savol', suv=suv, bar=bar, foiz=int((suv/2000)*100)),
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
            t(user_id, 'hafta_bosh'),
            reply_markup=asosiy_menyu(user_id)
        )
        return

    maqsad = maqsad_olish(user_id)
    matn = "📅\n━━━━━━━━━━━━━━\n"
    jami = 0
    for sana, kaloriya in natija:
        foiz = min(int((kaloriya / maqsad) * 10), 10)
        bar = "🟩" * foiz + "⬜" * (10 - foiz)
        matn += f"{sana}:\n{bar} {kaloriya} kcal\n"
        jami += kaloriya

    ortacha = jami // len(natija)
    matn += f"━━━━━━━━━━━━━━\n📊 {ortacha} kcal/kun"
    await update.message.reply_text(matn, reply_markup=asosiy_menyu(user_id))

async def sozlamalar_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    maqsad = maqsad_olish(user_id)
    tugmalar = InlineKeyboardMarkup([
        [InlineKeyboardButton(t(user_id, 'kaloriya_maqsad', maqsad=maqsad),
                              callback_data="sozlama_kaloriya")],
        [InlineKeyboardButton(t(user_id, 'suv_maqsad'), callback_data="sozlama_suv")],
        [InlineKeyboardButton(t(user_id, 'profil_yangi'), callback_data="sozlama_profil")],
        [InlineKeyboardButton("🌍 Til / Язык / Language", callback_data="sozlama_til")],
    ])
    await update.message.reply_text(t(user_id, 'sozlamalar'), reply_markup=tugmalar)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CALLBACK HANDLER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def callback_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    # TIL TANLASH
    if data.startswith("til_"):
        til = data.split("_")[1]
        til_saqlash(user_id, til)
        await query.edit_message_text(
            "🇺🇿 Til tanlandi!\n🇷🇺 Язык выбран!\n🇬🇧 Language selected!"
        )
        await jins_savol_yuborish(query, user_id, is_callback=True)
        holat_saqlash(user_id, "jins")
        return

    # JINS
    if data.startswith("jins_"):
        jins = data.split("_")[1]
        holat_saqlash(user_id, "yosh", jins)
        await query.edit_message_text(
            f"{t(user_id, 'erkak') if jins == 'erkak' else t(user_id, 'ayol')} ✅"
        )
        await query.message.reply_text(t(user_id, 'yosh_savol'))
        return

    # MAQSAD TUR (ro'yxatdan o'tish)
    if data.startswith("maqsad_tur_"):
        num = data.split("_")[2]
        maqsad_nomi = t(user_id, f'maqsad_{num}')
        qadam, vaqtinchalik = holat_olish(user_id)

        import json
        try:
            malumot = json.loads(vaqtinchalik)
        except:
            malumot = {}

        malumot['maqsad'] = maqsad_nomi

        # BMR hisoblash
        bmr = bmr_hisob(
            malumot.get('jins', 'erkak'),
            int(malumot.get('yosh', 25)),
            int(malumot.get('boy', 170)),
            float(malumot.get('vazn', 70)),
            maqsad_nomi
        )
        malumot['bmr'] = bmr

        await query.edit_message_text(f"{maqsad_nomi} ✅")

        # Tasdiqlash xabari
        jins_matn = t(user_id, 'erkak') if malumot.get('jins') == 'erkak' else t(user_id, 'ayol')
        tasdiq_matn = t(user_id, 'profil_tekshir',
            jins=jins_matn,
            yosh=malumot.get('yosh', '-'),
            boy=malumot.get('boy', '-'),
            vazn=malumot.get('vazn', '-'),
            maqsad=maqsad_nomi,
            kaloriya=bmr
        )

        tugmalar = InlineKeyboardMarkup([
            [InlineKeyboardButton(t(user_id, 'tasdiq'), callback_data="profil_tasdiq")],
            [InlineKeyboardButton(t(user_id, 'bekor'), callback_data="profil_bekor")],
        ])
        holat_saqlash(user_id, "tasdiq", json.dumps(malumot))
        await query.message.reply_text(tasdiq_matn, reply_markup=tugmalar)
        return

    # PROFIL TASDIQLASH
    if data == "profil_tasdiq":
        qadam, vaqtinchalik = holat_olish(user_id)
        import json
        try:
            malumot = json.loads(vaqtinchalik)
        except:
            await query.edit_message_text(t(user_id, 'umumiy_xato'))
            return

        profil_saqlash(
            user_id,
            malumot.get('jins', 'erkak'),
            int(malumot.get('yosh', 25)),
            int(malumot.get('boy', 170)),
            float(malumot.get('vazn', 70)),
            malumot.get('maqsad', ''),
            malumot.get('bmr', 2000)
        )
        holat_ochir(user_id)

        ism = query.from_user.first_name
        await query.edit_message_text(
            t(user_id, 'rahmat', ism=ism, kaloriya=malumot.get('bmr', 2000))
        )
        # Asosiy menyuni yuborish
        await query.message.reply_text(
            "👇",
            reply_markup=asosiy_menyu(user_id)
        )
        return

    # PROFIL BEKOR
    if data == "profil_bekor":
        holat_ochir(user_id)
        await query.edit_message_text(t(user_id, 'qoshilmadi'))
        await til_tanlash_yuborish(query, user_id)
        return

    # SOZLAMALAR
    if data == "sozlama_profil":
        holat_ochir(user_id)
        conn = sqlite3.connect("kaloriya.db")
        cur = conn.cursor()
        cur.execute("UPDATE foydalanuvchilar SET royxatdan=0 WHERE user_id=?", (user_id,))
        conn.commit()
        conn.close()
        await query.edit_message_text("♻️ Profil yangilanmoqda...")
        await jins_savol_yuborish(query, user_id, is_callback=True)
        holat_saqlash(user_id, "jins")
        return

    if data == "sozlama_til":
        await query.edit_message_text("🌍")
        tugmalar = InlineKeyboardMarkup([[
            InlineKeyboardButton("🇺🇿 O'zbek", callback_data="til_uz"),
            InlineKeyboardButton("🇷🇺 Русский", callback_data="til_ru"),
            InlineKeyboardButton("🇬🇧 English", callback_data="til_en"),
        ]])
        await query.message.reply_text(
            "🌍 Tilni tanlang / Выберите язык / Choose language:",
            reply_markup=tugmalar
        )
        return

    if data == "sozlama_kaloriya":
        await query.edit_message_text(t(user_id, 'sozlamalar'))
        await maqsad_cmd(query, ctx)
        return

    # SUV
    if data.startswith("suv_"):
        miqdor = int(data.split("_")[1])
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
            t(user_id, 'suv_qoshildi', miqdor=miqdor, suv=suv, bar=bar, foiz=int((suv/2000)*100)),
            reply_markup=tugmalar
        )
        return

    # KALORIYA MAQSAD
    if data.startswith("kaloriya_maqsad_"):
        maqsad = int(data.split("_")[2])
        maqsad_saqlash(user_id, maqsad)
        await query.edit_message_text(t(user_id, 'maqsad_ozgardi', maqsad=maqsad))
        return

    # OVQAT QO'SHISH
    if data.startswith("qosh_"):
        qismlar = data.split("_", 2)
        kaloriya = int(qismlar[1])
        ovqat_nomi = qismlar[2] if len(qismlar) > 2 else "Noma'lum"
        ovqat_saqlash(user_id, ovqat_nomi, kaloriya)

        maqsad = maqsad_olish(user_id)
        ovqatlar = bugungi_ovqatlar(user_id)
        jami = sum(k for _, k in ovqatlar)
        qolgan = maqsad - jami
        foiz = min(int((jami / maqsad) * 10), 10)
        bar = "🟩" * foiz + "⬜" * (10 - foiz)
        holat_matni = t(user_id, 'qolgan', qolgan=qolgan) if qolgan > 0 else t(user_id, 'oshdi', qolgan=abs(qolgan))

        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text(
            t(user_id, 'qoshildi', jami=jami, maqsad=maqsad, holat=holat_matni, bar=bar, foiz=int((jami/maqsad)*100)),
            reply_markup=asosiy_menyu(user_id)
        )
        return

    if data == "qoshma":
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text(t(user_id, 'qoshilmadi'), reply_markup=asosiy_menyu(user_id))
        return

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MATN HANDLER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def matn_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ism = update.effective_user.first_name
    foydalanuvchi_saqlash(user_id, ism)
    foydalanuvchi_matni = update.message.text

    # Holat tekshirish (ro'yxatdan o'tish jarayoni)
    qadam, vaqtinchalik = holat_olish(user_id)

    if qadam == "yosh":
        if not foydalanuvchi_matni.isdigit():
            await update.message.reply_text(t(user_id, 'xato_yosh'))
            return
        import json
        malumot = {'jins': vaqtinchalik, 'yosh': foydalanuvchi_matni}
        holat_saqlash(user_id, "boy", json.dumps(malumot))
        await update.message.reply_text(t(user_id, 'boy_savol'))
        return

    if qadam == "boy":
        if not foydalanuvchi_matni.isdigit():
            await update.message.reply_text(t(user_id, 'xato_boy'))
            return
        import json
        try:
            malumot = json.loads(vaqtinchalik)
        except:
            malumot = {}
        malumot['boy'] = foydalanuvchi_matni
        holat_saqlash(user_id, "vazn", json.dumps(malumot))
        await update.message.reply_text(t(user_id, 'vazn_savol'))
        return

    if qadam == "vazn":
        try:
            vazn = float(foydalanuvchi_matni.replace(',', '.'))
        except:
            await update.message.reply_text(t(user_id, 'xato_vazn'))
            return
        import json
        try:
            malumot = json.loads(vaqtinchalik)
        except:
            malumot = {}
        malumot['vazn'] = vazn
        holat_saqlash(user_id, "maqsad_tur", json.dumps(malumot))
        await maqsad_savol_yuborish(update, user_id)
        return

    # Tugmalar
    menu = t(user_id, 'menu')
    barcha_tugmalar = [btn for row in menu for btn in row]

    if foydalanuvchi_matni in barcha_tugmalar:
        idx = barcha_tugmalar.index(foydalanuvchi_matni)
        if idx == 0:
            await bugun_cmd(update, ctx)
        elif idx == 1:
            await maqsad_cmd(update, ctx)
        elif idx == 2:
            await suv_cmd(update, ctx)
        elif idx == 3:
            await hafta_cmd(update, ctx)
        elif idx == 4:
            await sozlamalar_cmd(update, ctx)
        elif idx == 5:
            await help_cmd(update, ctx)
        return

    # AI kaloriya hisoblash
    kutish = await update.message.reply_text(t(user_id, 'hisob'))
    prompt = t(user_id, 'ai_prompt').replace('{matn}', foydalanuvchi_matni)

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        javob = response.choices[0].message.content

        kaloriya = 0
        try:
            for qator in javob.split("\n"):
                if any(k in qator for k in ["Kaloriya:", "Калории:", "Calories:"]):
                    sonlar = [s for s in qator.split() if s.isdigit()]
                    if sonlar:
                        kaloriya = int(sonlar[0])
                        break
        except:
            pass

        await kutish.delete()

        if kaloriya > 0:
            tugmalar = InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    t(user_id, 'qosh_tugma', kaloriya=kaloriya),
                    callback_data=f"qosh_{kaloriya}_{foydalanuvchi_matni[:40]}"
                )],
                [InlineKeyboardButton(t(user_id, 'qoshma_tugma'), callback_data="qoshma")]
            ])
            await update.message.reply_text(javob, reply_markup=tugmalar)
        else:
            await update.message.reply_text(javob, reply_markup=asosiy_menyu(user_id))

    except Exception as e:
        await kutish.delete()
        await update.message.reply_text(t(user_id, 'umumiy_xato'))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RASM HANDLER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def rasm_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    foydalanuvchi_saqlash(user_id, update.effective_user.first_name)
    kutish = await update.message.reply_text(t(user_id, 'rasm_hisob'))

    try:
        photo = update.message.photo[-1]
        file = await ctx.bot.get_file(photo.file_id)
        rasm_bytes = await file.download_as_bytearray()
        rasm_base64 = base64.b64encode(rasm_bytes).decode("utf-8")

        til = til_olish(user_id)
        if til == 'ru':
            prompt = "Ты эксперт по калориям. Отвечай на русском. Проанализируй еду на фото:\n\n[EMOJI] [Название]\n━━━━━━━━━━━━━━\n🔥 Калории: [число] ккал\n💪 Белки: [число] г\n🧈 Жиры: [число] г\n🍞 Углеводы: [число] г\n━━━━━━━━━━━━━━\n💡 [1-2 совета]\n\nЕсли не еда — 'На фото не вижу еды 🤔'"
        elif til == 'en':
            prompt = "You are a calorie expert. Reply in English. Analyze the food in the photo:\n\n[EMOJI] [Name]\n━━━━━━━━━━━━━━\n🔥 Calories: [number] kcal\n💪 Protein: [number] g\n🧈 Fat: [number] g\n🍞 Carbs: [number] g\n━━━━━━━━━━━━━━\n💡 [1-2 tips]\n\nIf not food — 'No food visible in the photo 🤔'"
        else:
            prompt = "Sen kaloriya mutaxassisisan. O'zbek tilida javob ber. Rasmdagi ovqatni tahlil qil:\n\n[EMOJI] [Ovqat nomi]\n━━━━━━━━━━━━━━\n🔥 Kaloriya: [son] kcal\n💪 Protein: [son] g\n🧈 Yog': [son] g\n🍞 Uglevod: [son] g\n━━━━━━━━━━━━━━\n💡 [1-2 maslahat]\n\nOvqat ko'rinmasa — 'Rasmda ovqat ko'rinmayapti 🤔'"

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

        kaloriya = 0
        try:
            for qator in javob.split("\n"):
                if any(k in qator for k in ["Kaloriya:", "Калории:", "Calories:"]):
                    sonlar = [s for s in qator.split() if s.isdigit()]
                    if sonlar:
                        kaloriya = int(sonlar[0])
                        break
        except:
            pass

        await kutish.delete()

        if kaloriya > 0:
            tugmalar = InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    t(user_id, 'qosh_tugma', kaloriya=kaloriya),
                    callback_data=f"qosh_{kaloriya}_📸 Rasm orqali"
                )],
                [InlineKeyboardButton(t(user_id, 'qoshma_tugma'), callback_data="qoshma")]
            ])
            await update.message.reply_text(javob, reply_markup=tugmalar)
        else:
            await update.message.reply_text(javob, reply_markup=asosiy_menyu(user_id))

    except Exception as e:
        await kutish.delete()
        if "insufficient_quota" in str(e) or "429" in str(e):
            await update.message.reply_text(
                t(user_id, 'rasm_xato'),
                reply_markup=asosiy_menyu(user_id)
            )
        else:
            await update.message.reply_text(t(user_id, 'umumiy_xato'))

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
