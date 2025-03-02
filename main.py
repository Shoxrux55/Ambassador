import json
import telebot
from flask import Flask, request

# TOKEN DETAILS
TOKEN = "Ball"
BOT_TOKEN = "7580694173:AAERNuW1PATTh_LC_WyKahR2pmR052RDUjc"
PAYMENT_CHANNEL = "@Endoland"
OWNER_ID = 725821571
CHANNELS = ["@Endoland"]
Daily_bonus = 1
Per_Refer = 1

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

ADMIN_GROUP_USERNAME = "@endocrineqatnashchi"

# Log yozuvlari uchun ro'yxat
log_messages = []

@app.route('/')
def hello_world():
    return 'Bot is running!'

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def receive_update():
    try:
        json_str = request.get_data().decode('UTF-8')
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
        log_messages.append(json_str)
        app.logger.info(f"Received update: {json_str}")
        return '', 200
    except Exception as e:
        app.logger.error(f"Error processing update: {e}")
        return '', 500

@app.route('/webhook', methods=['POST'])
def webhook():
    return receive_update()

@app.route('/logs')
def get_logs():
    return '<br>'.join(log_messages)

# Bot funksiyalari
def check(id):
    for i in CHANNELS:
        check = bot.get_chat_member(i, id)
        if check.status != 'left':
            pass
        else:
            return False
    return True

bonus = {}

def menu(id):
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('🆔 Mening hisobim')
    keyboard.row('🙌🏻 Maxsus linkim')
    keyboard.row('🎁 Mening sovg\'am')
    if id == OWNER_ID:
        keyboard.row('📊 Statistika')
    bot.send_message(id, "Asosiy menyu👇", reply_markup=keyboard)

def load_users_data():
    try:
        with open('users.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "referred": {},
            "referby": {},
            "checkin": {},
            "DailyQuiz": {},
            "balance": {},
            "dollar_balance": {},
            "withd": {},
            "id": {},
            "username": {},  # Username’lar uchun yangi maydon
            "total": 0,
            "refer": {}
        }

def save_users_data(data):
    with open('users.json', 'w') as f:
        json.dump(data, f)

def send_videos(user_id, video_file_ids):
    for video_file_id in video_file_ids:
        bot.send_video(user_id, video_file_id, supports_streaming=True)

def send_gift_video(user_id):
    data = load_users_data()
    balance = data['balance'].get(str(user_id), 0)
    if 0 <= balance < 10:
        video_file_ids = ["https://t.me/marafonbotbazasi/7"]
        send_videos(user_id, video_file_ids)
        bot.send_message(user_id, '1-dars video sizga jo‘natildi.')
    elif 10 <= balance < 20:
        video_file_ids = ["https://t.me/marafonbotbazasi/7", "https://t.me/marafonbotbazasi/8"]
        send_videos(user_id, video_file_ids)
        bot.send_message(user_id, '1-dars va 2-dars videolar sizga jo‘natildi.')
    elif balance >= 20:
        video_file_ids = ["https://t.me/marafonbotbazasi/7", "https://t.me/marafonbotbazasi/8", "https://t.me/marafonbotbazasi/9"]
        send_videos(user_id, video_file_ids)
        bot.send_message(user_id, '1-dars, 2-dars, va 3-dars videolar sizga jo‘natildi.')
    else:
        bot.send_message(user_id, 'Kechirasiz, ballaringiz yetarli emas.')

@bot.message_handler(commands=['start'])
def start(message):
    try:
        user_id = message.chat.id
        username = message.chat.username
        msg = message.text
        user = str(user_id)
        data = load_users_data()
        referrer = None if msg == '/start' else msg.split()[1]

        if user not in data['referred']:
            data['referred'][user] = 0
            data['total'] += 1
        if user not in data['referby']:
            data['referby'][user] = referrer if referrer else user
            if referrer and referrer in data['referred']:
                data['referred'][referrer] = data['referred'].get(referrer, 0) + 1
                data['balance'][referrer] = data['balance'].get(referrer, 0) + Per_Refer
                if referrer not in data['dollar_balance']:
                    data['dollar_balance'][referrer] = 0.0
        if user not in data['checkin']:
            data['checkin'][user] = 0
        if user not in data['DailyQuiz']:
            data['DailyQuiz'][user] = "0"
        if user not in data['balance']:
            data['balance'][user] = 0
        if user not in data['dollar_balance']:
            data['dollar_balance'][user] = 0.0
        if user not in data['withd']:
            data['withd'][user] = 0
        if user not in data['id']:
            data['id'][user] = data['total'] + 1
        if user not in data['username']:
            data['username'][user] = username if username else "Noma’lum"
        save_users_data(data)

        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton(
            text='Marafon kanaliga qo‘shilish', url='https://t.me/Endoland'))
        markup.add(telebot.types.InlineKeyboardButton(
            text='Obunani tekshirish', callback_data='check'))
        msg_start = """Tabriklayman! Siz marafon qatnashchisi bo'lishga yaqin qoldingiz..."""
        bot.send_message(user_id, msg_start, reply_markup=markup)
    except Exception as e:
        bot.send_message(user_id, "Bu buyruqda xatolik bor, iltimos admin xatoni tuzatishini kuting")
        bot.send_message(OWNER_ID, f"Xatolik: {str(e)}")

@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    try:
        ch = check(call.message.chat.id)
        if call.data == 'check':
            if ch:
                data = load_users_data()
                user_id = call.message.chat.id
                user = str(user_id)
                username = call.message.chat.username
                bot.answer_callback_query(callback_query_id=call.id, text='Siz kanalga qo‘shildingiz, omad tilaymiz')

                if user not in data['refer']:
                    data['refer'][user] = True
                    if user not in data['referby']:
                        data['referby'][user] = user
                    if int(data['referby'][user]) != user_id:
                        ref_id = data['referby'][user]
                        ref = str(ref_id)
                        if ref not in data['balance']:
                            data['balance'][ref] = 0
                        if ref not in data['referred']:
                            data['referred'][ref] = 0
                        data['balance'][ref] += Per_Refer
                        data['referred'][ref] += 1
                        bot.send_message(ref_id, f"Do'stingiz kanalga qo'shildi va siz +{Per_Refer} {TOKEN} ishlab oldingiz")
                    save_users_data(data)

                markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                markup.add(telebot.types.KeyboardButton(text='Raqamni ulashish', request_contact=True))
                bot.send_message(user_id, f"Salom, @{username}! \nRaqamingizni tasdiqlang:", reply_markup=markup)
            else:
                bot.answer_callback_query(callback_query_id=call.id, text='Siz hali kanalga qo‘shilmadingiz')
                markup = telebot.types.InlineKeyboardMarkup()
                markup.add(telebot.types.InlineKeyboardButton(
                    text='Obunani tekshirish', callback_data='check'))
                bot.send_message(call.message.chat.id, "Kanalga qo‘shiling:\n- @Endoland", reply_markup=markup)
    except Exception as e:
        bot.send_message(call.message.chat.id, "Xatolik yuz berdi")
        bot.send_message(OWNER_ID, f"Xatolik: {str(e)}")

@bot.message_handler(content_types=['contact'])
def contact(message):
    if message.contact is not None:
        contact = message.contact.phone_number
        username = message.from_user.username
        bot.send_message(ADMIN_GROUP_USERNAME, f"Foydalanuvchi: @{username}\nTelefon raqami: {contact}")

        inline_markup = telebot.types.InlineKeyboardMarkup()
        inline_markup.add(telebot.types.InlineKeyboardButton(text="Sovg'angiz👇", callback_data='gift'))
        gift_message = """Siz uchun tayyorlab qo'ygan sovg'alarimizni kutib oling🤗..."""
        bot.send_message(message.chat.id, gift_message, reply_markup=inline_markup)
        menu(message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data in ['account', 'ref_link', 'gift'])
def account_or_ref_link_handler(call):
    try:
        user_id = call.message.chat.id
        data = load_users_data()
        user = str(user_id)
        username = call.message.chat.username

        if call.data == 'account':
            balance = data['balance'].get(user, 0)
            dollar_balance = data['dollar_balance'].get(user, 0.0)
            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(telebot.types.InlineKeyboardButton(text=f"Balans: {balance} Ball", callback_data='balance'))
            msg = f"Foydalanuvchi: @{username}\nBallar: {balance} {TOKEN}\nDollar balans: ${dollar_balance}"
            bot.send_message(user_id, msg, reply_markup=markup)
        elif call.data == 'ref_link':
            send_invite_link(user_id)
        elif call.data == 'gift':
            send_gift_video(user_id)
    except Exception as e:
        bot.send_message(user_id, "Xatolik yuz berdi")
        bot.send_message(OWNER_ID, f"Xatolik: {str(e)}")

def send_invite_link(user_id):
    data = load_users_data()
    bot_name = bot.get_me().username
    user = str(user_id)
    if user not in data['referred']:
        data['referred'][user] = 0
    save_users_data(data)
    ref_link = f'https://telegram.me/{bot_name}?start={user_id}'
    msg = f"ENDOKRINOLOGIYA BOʻYICHA OCHIQ DARSLAR\n\nTaklifnoma havolasi: {ref_link}"
    bot.send_message(user_id, msg)

@bot.message_handler(commands=['addstudent'])
def add_student(message):
    if message.chat.id != OWNER_ID:
        bot.send_message(message.chat.id, "Bu buyruq faqat bot egasiga mavjud.")
        return
    
    try:
        args = message.text.split()
        if len(args) != 2:
            bot.send_message(message.chat.id, "To‘g‘ri format: /addstudent @username")
            return
        
        username = args[1].replace('@', '')
        data = load_users_data()
        
        buyer_id = None
        for user_id, stored_username in data['username'].items():
            if stored_username == username:
                buyer_id = user_id
                break
        
        if not buyer_id:
            bot.send_message(message.chat.id, f"@{username} botda topilmadi.")
            return
        
        referrer = data['referby'].get(buyer_id, buyer_id)
        if referrer == buyer_id or referrer not in data['dollar_balance']:
            bot.send_message(message.chat.id, f"@{username} hech kim tomonidan taklif qilinmagan.")
            return
        
        referrer = str(referrer)
        if referrer not in data['dollar_balance']:
            data['dollar_balance'][referrer] = 0.0
        data['dollar_balance'][referrer] += 5.0
        save_users_data(data)
        
        bot.send_message(message.chat.id, f"@{username} {referrer} uchun qayd qilindi. +5$ qo‘shildi.")
        bot.send_message(referrer, f"Siz taklif qilgan @{username} yopiq guruhga qo‘shildi! +5$ qo‘shildi.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Xatolik: {str(e)}")

@bot.message_handler(content_types=['text'])
def send_text(message):
    try:
        if message.text == '🆔 Mening hisobim':
            data = load_users_data()
            user_id = message.chat.id
            user = str(user_id)
            balance = data['balance'].get(user, 0)
            dollar_balance = data['dollar_balance'].get(user, 0.0)
            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(telebot.types.InlineKeyboardButton(text=f"Balans: {balance} Ball", callback_data='balance'))
            msg = f"Foydalanuvchi: @{message.from_user.username}\nBallar: {balance} {TOKEN}\nDollar balans: ${dollar_balance}"
            bot.send_message(user_id, msg, reply_markup=markup)
        elif message.text == '🙌🏻 Maxsus linkim':
            send_invite_link(message.chat.id)
        elif message.text == '🎁 Mening sovg\'am':
            send_gift_video(message.chat.id)
        elif message.text == "📊 Statistika" and message.chat.id == OWNER_ID:
            data = load_users_data()
            bot.send_message(message.chat.id, f"Jami foydalanuvchilar: {data['total']}")
    except Exception as e:
        bot.send_message(message.chat.id, "Xatolik yuz berdi")
        bot.send_message(OWNER_ID, f"Xatolik: {str(e)}")

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
