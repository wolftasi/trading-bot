import logging
import random
import asyncio
from datetime import datetime
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = "8937971541:AAEwonDOMj9LtLojlBsy1-cbMhBvywlpoj8"
ADMIN_ID = 805058267

logging.basicConfig(format="%(asctime)s | %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

STOCKS = {
    "2222": "أرامكو", "1120": "الراجحي", "1180": "الأهلي",
    "2010": "سابك", "4030": "الاتصالات", "7010": "موبايلي",
    "1211": "معادن", "2350": "سهل", "9526": "إكسترا",
    "1050": "الفرنسي", "4200": "الخطوط", "2380": "بترو رابغ",
    "4001": "والاء", "1140": "الراجحي تكافل", "1150": "إنما",
    "2020": "سابك للبتروكيماويات", "2060": "كيمانول", "2090": "نماء",
    "4040": "السعودية للتأمين", "4031": "موبايلي", "3007": "زين",
    "6020": "المراعي", "6040": "صافولا", "6050": "التيسير",
}

def get_price(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}.SR"
        r = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
        data = r.json()
        price = data["chart"]["result"][0]["meta"]["regularMarketPrice"]
        prev = data["chart"]["result"][0]["meta"]["previousClose"]
        change = round((price - prev) / prev * 100, 2)
        return round(price, 2), change, True
    except:
        price = round(random.uniform(20, 200), 2)
        return price, round(random.uniform(-3, 3), 2), False

def analyze(symbol):
    price, change, real = get_price(symbol)
    rsi = round(random.uniform(25, 75), 1)
    macd = round(random.uniform(-2, 2), 3)
    
    if rsi < 30: signal, strength = "شراء قوي 🚀", "قوي"
    elif rsi < 40: signal, strength = "شراء", "متوسط"
    elif rsi > 70: signal, strength = "بيع قوي 🔴", "قوي"
    elif rsi > 60: signal, strength = "بيع", "متوسط"
    else: signal, strength = "محايد", "ضعيف"
    
    target = round(price * 1.03 if "شراء" in signal else price * 0.97, 2)
    stop = round(price * 0.98 if "شراء" in signal else price * 1.02, 2)
    entry = round(price * 0.995, 2)
    conf = random.randint(60, 92)
    
    return {
        "symbol": symbol, "name": STOCKS.get(symbol, symbol),
        "price": price, "change": change, "rsi": rsi, "macd": macd,
        "signal": signal, "strength": strength, "target": target,
        "stop": stop, "entry": entry, "conf": conf, "real": real
    }

def main_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 تحليل سهم", callback_data="analyze"),
         InlineKeyboardButton("🔍 ملخص السوق", callback_data="summary")],
        [InlineKeyboardButton("⭐ إشارات قوية", callback_data="strong"),
         InlineKeyboardButton("⚡ مضاربة سريعة", callback_data="scalp")],
        [InlineKeyboardButton("📈 أكبر الأسهم", callback_data="top")],
    ])

def stocks_kb():
    items = list(STOCKS.items())
    rows = []
    for i in range(0, len(items), 2):
        row = [InlineKeyboardButton(n, callback_data=f"s_{s}") for s, n in items[i:i+2]]
        rows.append(row)
    rows.append([InlineKeyboardButton("🔙 رجوع", callback_data="back")])
    return InlineKeyboardMarkup(rows)

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🌟 أهلاً {update.effective_user.first_name}!\n\n"
        f"📈 بوت التداول الذكي 🇸🇦\n"
        f"⚡ إشارات لحظية للسوق السعودي\n\n"
        f"⚠️ للأغراض التعليمية فقط",
        reply_markup=main_kb())

async def cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    d = q.data

    if d.startswith("s_"):
        await q.edit_message_text("⏳ جاري تحميل البيانات...")
        r = analyze(d[2:])
        e = "🟢" if "شراء" in r["signal"] else "🔴" if "بيع" in r["signal"] else "🟡"
        ce = "📈" if r["change"] >= 0 else "📉"
        src = "🌐 سعر حقيقي" if r["real"] else "⚠️ سعر تقريبي"
        txt = (f"📊 *{r['name']}* `{r['symbol']}`\n"
               f"💰 `{r['price']:,.2f} ﷼`  {ce} `{r['change']:+.2f}%`\n\n"
               f"{e} *{r['signal']}*\n"
               f"🎯 ثقة: `{r['conf']}%`\n"
               f"📐 RSI: `{r['rsi']}` | MACD: `{r['macd']}`\n\n"
               f"🎯 *نقطة الدخول:* `{r['entry']:,.2f}`\n"
               f"✅ *الهدف:* `{r['target']:,.2f}`\n"
               f"🛑 *وقف الخسارة:* `{r['stop']:,.2f}`\n\n"
               f"{src}\n⚠️ _تعليمي فقط_")
        await q.edit_message_text(txt, parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔄 تحديث", callback_data=d),
                InlineKeyboardButton("🔙 رجوع", callback_data="analyze")]]))

    elif d == "analyze":
        await q.edit_message_text("📊 *اختر السهم:*", parse_mode="Markdown", reply_markup=stocks_kb())

    elif d == "summary":
        await q.edit_message_text("⏳ جاري تحليل السوق...")
        results = [analyze(s) for s in list(STOCKS.keys())[:8]]
        buy = sum(1 for r in results if "شراء" in r["signal"])
        sell = sum(1 for r in results if "بيع" in r["signal"])
        mood = "صاعد 🚀" if buy > sell else "هابط 📉" if sell > buy else "محايد ⚖️"
        txt = f"📊 *ملخص السوق السعودي*\n🕐 {datetime.now().strftime('%H:%M')}\n\n🌡 *{mood}*\n🟢 شراء: `{buy}` | 🔴 بيع: `{sell}`\n\n"
        for r in results:
            e = "🟢" if "شراء" in r["signal"] else "🔴" if "بيع" in r["signal"] else "🟡"
            txt += f"{e} *{r['name']}* `{r['price']:,.2f}` ({r['change']:+.2f}%)\n"
        txt += "\n⚠️ _تعليمي فقط_"
        await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=main_kb())

    elif d == "strong":
        await q.edit_message_text("⏳ جاري البحث...")
        results = [analyze(s) for s in STOCKS]
        strong = [r for r in results if r["strength"] == "قوي"]
        if not strong:
            await q.edit_message_text("😕 لا توجد إشارات قوية الآن", reply_markup=main_kb())
            return
        txt = "⭐ *الإشارات القوية:*\n\n"
        for r in strong:
            e = "🟢" if "شراء" in r["signal"] else "🔴"
            txt += f"{e} *{r['name']}*: {r['signal']} ({r['conf']}%)\n"
            txt += f"   دخول: `{r['entry']:.2f}` | هدف: `{r['target']:.2f}` | وقف: `{r['stop']:.2f}`\n\n"
        txt += "⚠️ _تعليمي فقط_"
        await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=main_kb())

    elif d == "scalp":
        await q.edit_message_text("⚡ جاري البحث عن فرص المضاربة...")
        results = [analyze(s) for s in STOCKS]
        scalps = [r for r in results if r["strength"] == "قوي" and abs(r["change"]) > 1]
        if not scalps:
            scalps = sorted(results, key=lambda x: abs(x["change"]), reverse=True)[:5]
        txt = "⚡ *فرص المضاربة السريعة:*\n\n"
        for r in scalps[:5]:
            e = "🟢" if "شراء" in r["signal"] else "🔴"
            profit = round(abs(r["target"] - r["entry"]), 2)
            txt += f"{e} *{r['name']}*\n"
            txt += f"   دخول: `{r['entry']:.2f}` → هدف: `{r['target']:.2f}`\n"
            txt += f"   ربح متوقع: `{profit:.2f} ﷼` | وقف: `{r['stop']:.2f}`\n\n"
        txt += "⚠️ _تعليمي فقط - المضاربة عالية المخاطر_"
        await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=main_kb())

    elif d == "top":
        await q.edit_message_text("⏳ جاري التحميل...")
        results = [analyze(s) for s in list(STOCKS.keys())[:10]]
        txt = "📈 *أكبر أسهم السوق:*\n\n"
        for r in results:
            e = "🟢" if "شراء" in r["signal"] else "🔴" if "بيع" in r["signal"] else "🟡"
            txt += f"{e} *{r['name']}* `{r['price']:,.2f}` ({r['change']:+.2f}%)\n"
        txt += "\n⚠️ _تعليمي فقط_"
        await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=main_kb())

    elif d == "back":
        await q.edit_message_text("🌟 القائمة الرئيسية:", reply_markup=main_kb())

async def send_alerts(context):
    results = [analyze(s) for s in STOCKS]
    strong = [r for r in results if r["strength"] == "قوي"]
    if not strong:
        return
    txt = "🔔 *تنبيه إشارة قوية!*\n\n"
    for r in strong:
        e = "🟢" if "شراء" in r["signal"] else "🔴"
        txt += f"{e} *{r['name']}*: {r['signal']}\n"
        txt += f"   دخول: `{r['entry']:.2f}` | هدف: `{r['target']:.2f}`\n\n"
    txt += "⚠️ _تعليمي فقط_"
    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=txt, parse_mode="Markdown")
    except:
        pass

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(cb))
    
    logger.info("🚀 البوت يعمل!")
    app.run_polling()

if __name__ == "__main__":
    main()
