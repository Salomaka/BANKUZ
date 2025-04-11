import telebot
from math import pow

TOKEN = "BOT_TOKENINGIZNI_BU_YERGA_QOYING"
bot = telebot.TeleBot(TOKEN)

user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
                     "Assalomu alaykum! Kredit Kalkulyatori botiga xush kelibsiz.\n"
                     "Iltimos, kredit summasini kiriting (so'mda):")
    user_data[message.chat.id] = {}

@bot.message_handler(func=lambda msg: msg.chat.id in user_data and 'summa' not in user_data[msg.chat.id])
def get_sum(msg):
    try:
        summa = int(msg.text.replace(',', '').replace(' ', ''))
        user_data[msg.chat.id]['summa'] = summa
        bot.send_message(msg.chat.id, "Endi kredit muddatini kiriting (oylarda):")
    except:
        bot.send_message(msg.chat.id, "Noto‘g‘ri format. Iltimos, faqat son kiriting.")

@bot.message_handler(func=lambda msg: msg.chat.id in user_data and 'oy' not in user_data[msg.chat.id])
def get_months(msg):
    try:
        oy = int(msg.text)
        user_data[msg.chat.id]['oy'] = oy
        bot.send_message(msg.chat.id, "Endi yillik foiz stavkasini kiriting (masalan: 20):")
    except:
        bot.send_message(msg.chat.id, "Noto‘g‘ri format. Iltimos, faqat son kiriting.")

@bot.message_handler(func=lambda msg: msg.chat.id in user_data and 'foiz' not in user_data[msg.chat.id])
def get_foiz(msg):
    try:
        foiz = float(msg.text)
        user_data[msg.chat.id]['foiz'] = foiz

        markup = telebot.types.InlineKeyboardMarkup()
        btn1 = telebot.types.InlineKeyboardButton("Annuitet usulda hisoblash", callback_data="annuitet")
        btn2 = telebot.types.InlineKeyboardButton("Kamayuvchi usulda hisoblash", callback_data="kamayuvchi")
        markup.add(btn1, btn2)

        bot.send_message(msg.chat.id,
                         "Hisoblash usulini tanlang:",
                         reply_markup=markup)
    except:
        bot.send_message(msg.chat.id, "Noto‘g‘ri format. Iltimos, faqat son kiriting.")

@bot.callback_query_handler(func=lambda call: call.data in ["annuitet", "kamayuvchi"])
def hisobla(call):
    data = user_data[call.message.chat.id]
    summa = data['summa']
    oy = data['oy']
    foiz = data['foiz']
    oylik_foiz = foiz / 12 / 100

    if call.data == "annuitet":
        annuitet = (summa * oylik_foiz) / (1 - pow((1 + oylik_foiz), -oy))
        jami = annuitet * oy
        bot.send_message(call.message.chat.id,
                         f"**Annuitet usulda**\n"
                         f"Oylik to‘lov: {round(annuitet):,} so‘m\n"
                         f"Jami to‘lov: {round(jami):,} so‘m",
                         parse_mode="Markdown")
    else:
        asosiy_qism = summa / oy
        tolovlar = []
        jami = 0
        for i in range(oy):
            qolgan_summa = summa - asosiy_qism * i
            foiz_tolovi = qolgan_summa * oylik_foiz
            oylik_tolov = asosiy_qism + foiz_tolovi
            tolovlar.append(round(oylik_tolov))
            jami += oylik_tolov

        birinchi = tolovlar[0]
        oxirgi = tolovlar[-1]
        bot.send_message(call.message.chat.id,
                         f"**Kamayuvchi usulda**\n"
                         f"1-oy to‘lov: {round(birinchi):,} so‘m\n"
                         f"So‘nggi oy to‘lov: {round(oxirgi):,} so‘m\n"
                         f"Jami to‘lov: {round(jami):,} so‘m",
                         parse_mode="Markdown")

    # Reset user state
    user_data.pop(call.message.chat.id, None)

bot.polling()