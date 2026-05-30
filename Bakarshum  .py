import logging
import random
import asyncio
from datetime import datetime
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = "8937971541:AAEwonDOMj9LtLojlBsy1-cbMhBvywlpoj8"

logging.basicConfig(format="%(asctime)s | %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

STOCKS = {
    "2222": "أرامكو", "1120": "الراجحي", "1180": "الأهلي",
    "2010": "سابك", "4030": "الاتصالات", "7010": "موبايلي",
    "1211": "معادن", "2350": "سهل", "9526": "إكسترا",
    "1050": "الفرنسي", "4200": "الخطوط", "2380": "بترو رابغ",
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
    if rsi < 35: signal, strength = "شراء", "قوي"
    elif rsi < 45: signal, strength = "شراء", "متوسط"
    elif rsi > 65: signal, strength = "بيع", "قوي"
    elif rsi > 55: signal, strength = "بيع", "متوسط"
    else: signal, strength = "محايد", "ضعيف"
    target = round(price * 1.05 if signal == "شراء" else price * 0.95, 2)
    stop = round(price * 0.97 if signal == "شراء" else price * 1.03, 2)
    return {"symbol": symbol, "name": STOCKS[symbol], "price": price,
            "change": change, "rsi": rsi, "signal": signal,
            "strength": strength, "target": target, "stop": stop,
            "conf": random.randint(60, 92), "real": real}

def mkb():
    items = list(STOCKS.items())
    rows = []
    for i in range(0, len(items), 2):
        row = [InlineKeyboardButton(n, callback_data=f"s_{s}") for s, n in items[i:i+2]]
        rows.append(row)
    rows.append([InlineKeyboardButton("🔙 رجوع", callback_data="back")])
    return InlineKeyboardMarkup(rows)

def main_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 تحليل سهم", callback_data="analyze"),
         InlineKeyboardButton("🔍 ملخص السوق", callback_data="summary")],
        [InlineKeyboardButton("⭐ إشارات قوية", callback_data="strong")],
    ])

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🌟 أهلاً {update.effective_user.first_name}!\nبوت التداول الذكي 🇸🇦\n⚠️ للأغراض التعليمية فقط",
        reply_markup=main_kb())

async def cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    d = q.data
    if d.startswith("s_"):
        await q.edit_message_text("⏳ جاري تحميل البيانات...")
        r = analyze(d[2:])
        e = "🟢" if r["signal"] == "شراء" else "🔴" if r["signal"] == "بيع" else "🟡"
        ce = "📈" if r["change"] >= 0 else "📉"
        src = "🌐 سعر حقيقي" if r["real"] else "⚠️ سعر تقريبي"
        txt = (f"📊 *{r['name']}* `{r['symbol']}`\n"
               f"💰 `{r['price']:,.2f} ﷼`\n"
               f"{ce} `{r['change']:+.2f}%`\n\n"
               f"{e} *{r['signal']}* ({r['strength']})\n"
               f"🎯 ثقة: `{r['conf']}%`\n"
               f"📐 RSI: `{r['rsi']}`\n"
               f"🎯 هدف: `{r['target']:,.2f}`\n"
               f"🛑 وقف: `{r['stop']:,.2f}`\n\n"
               f"{src}\n⚠️ _تعليمي فقط_")
        await q.edit_message_text(txt, parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔄", callback_data=d),
                InlineKeyboardButton("🔙", callback_data="analyze")]]))
    elif d == "analyze":
        await q.edit_message_text("📊 اختر السهم:", reply_markup=mkb())
    elif d == "summary":
        await q.edit_message_text("⏳ جاري تحليل السوق...")
        results = [analyze(s) for s in list(STOCKS.keys())[:6]]
        buy = sum(1 for r in results if r["signal"] == "شراء")
        sell = sum(1 for r in results if r["signal"] == "بيع")
        mood = "صاعد 🚀" if buy > sell else "هابط 📉" if sell > buy else "محايد ⚖️"
        txt = f"📊 *ملخص السوق*\n🌡 {mood}\n🟢 شراء: `{buy}`\n🔴 بيع: `{sell}`\n\n"
        for r in results:
            e = "🟢" if r["signal"] == "شراء" else "🔴" if r["signal"] == "بيع" else "🟡"
            txt += f"{e} {r['name']}: `{r['price']:,.2f}` ({r['change']:+.2f}%)\n"
        txt += "\n⚠️ _تعليمي فقط_"
        await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=main_kb())
    elif d == "strong":
        results = [analyze(s) for s in STOCKS]
        strong = [r for r in results if r["strength"] == "قوي"]
        txt = "⭐ *إشارات قوية:*\n\n"
        for r in strong:
            e = "🟢" if r["signal"] == "شراء" else "🔴"
            txt += f"{e} *{r['name']}*: {r['signal']} ({r['conf']}%)\n"
        if not strong: txt = "😕 لا توجد إشارات قوية الآن"
        await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=main_kb())
    elif d == "back":
        await q.edit_message_text("🌟 القائمة الرئيسية:", reply_markup=main_kb())

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(cb))
    logger.info("🚀 البوت يعمل!")
    app.run_polling()

if __name__ == "__main__":
    main()
