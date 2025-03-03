import json
import telebot
from flask import Flask, request
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

# Bot sozlamalari
TOKEN = "Ball"
BOT_TOKEN = "7580694173:AAERNuW1PATTh_LC_WyKahR2pmR052RDUjc"
PAYMENT_CHANNEL = "@Endoland"
OWNER_ID = 725821571
CHANNELS = ["@Endoland"]
Daily_bonus = 1
Per_Refer = 1

ADMIN_GROUP_USERNAME = "@endocrineqatnashchi"

# Log yozuvlari uchun ro'yxat
log_messages = []

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# Google Sheets sozlamalari
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
try:
    creds_json = json.loads(os.environ.get('GOOGLE_SHEETS_CREDENTIALS'))
    app.logger.info("GOOGLE_SHEETS_CREDENTIALS successfully loaded")
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
    client = gspread.authorize(creds)
    sheet = client.open("Ambassador").sheet1
    app.logger.info("Successfully connected to Google Sheets")
except Exception as e:
    error_msg = f"Google Sheets ulanishda xatolik: {str(e)}"
    print(error_msg)
    app.logger.error(error_msg)
    raise

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
    app.logger.info(f"Checking membership for user {id} in channels: {CHANNELS}")
    for i in CHANNELS:
        try:
            check = bot.get_chat_member(i, id)
            app.logger.info(f"Channel {i} membership status for user {id}: {check.status}")
            if check.status == 'left':
                return False
        except Exception as e:
            app.logger.error(f"Error checking membership in channel {i} for user {id}: {str(e)}")
            return False
    return True

bonus = {}

def menu(id):
    if id == OWNER_ID:
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.row('🆔 Mening hisobim')
        keyboard.row('🙌🏻 Maxsus linkim')
        keyboard.row('📊 Statistika')
        keyboard.row('Talabalarni hisoblash')
        bot.send_message(id, "Asosiy menyu👇", reply_markup=keyboard)
    else:
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.row('🆔 Mening hisobim')
        keyboard.row('🙌🏻 Maxsus linkim')
        bot.send_message(id, "Asosiy menyu👇", reply_markup=keyboard)

def load_users_data():
    try:
        data = sheet.get_all_records()
        if not data:
            return {
                "referred": {},
                "referby": {},
                "checkin": {},
                "DailyQuiz": {},
                "balance": {},
                "dollar_balance": {},
                "withd": {},
                "id": {},
                "username": {},
                "total": 0,
                "refer": {}
            }
        
        result = {
            "referred": {},
            "referby": {},
            "checkin": {},
            "DailyQuiz": {},
            "balance": {},
            "dollar_balance": {},
            "withd": {},
            "id": {},
            "username": {},
            "total": int(sheet.cell(1, 2).value or 0),
            "refer": {}
        }
        for row in data:
            user_id = str(row["user_id"])
            result["referred"][user_id] = row.get("referred", 0)
            result["referby"][user_id] = row.get("referby", user_id)
            result["checkin"][user_id] = row.get("checkin", 0)
            result["DailyQuiz"][user_id] = row.get("DailyQuiz", "0")
            result["balance"][user_id] = row.get("balance", 0)
            result["dollar_balance"][user_id] = row.get("dollar_balance", 0.0)
            result["withd"][user_id] = row.get("withd", 0)
            result["id"][user_id] = row.get("id", 0)
            result["username"][user_id] = row.get("username", "Noma'lum")
            result["refer"][user_id] = row.get("refer", False)
        return result
    except Exception as e:
        print(f"Xatolik load_users_data’da: {e}")
        return {
            "referred": {},
            "referby": {},
            "checkin": {},
            "DailyQuiz": {},
            "balance": {},
            "dollar_balance": {},
            "withd": {},
            "id": {},
            "username": {},
            "total": 0,
            "refer": {}
        }

def save_users_data(data):
    try:
        sheet.clear()
        headers = ["user_id", "referred", "referby", "checkin", "DailyQuiz", "balance", 
                   "dollar_balance", "withd", "id", "username", "refer"]
        sheet.append_row(headers)
        for user_id in data["referred"].keys():
            row = [
                user_id,
                data["referred"].get(user_id, 0),
                data["referby"].get(user_id, user_id),
                data["checkin"].get(user_id, 0),
                data["DailyQuiz"].get(user_id, "0"),
                data["balance"].get(user_id, 0),
                data["dollar_balance"].get(user_id, 0.0),
                data["withd"].get(user_id, 0),
                data["id"].get(user_id, 0),
                data["username"].get(user_id, "Noma'lum"),
                data["refer"].get(user_id, False)
            ]
            sheet.append_row(row)
        sheet.update_cell(1, 2, data["total"])
    except Exception as e:
        print(f"Xatolik save_users_data’da: {e}")

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
                data['referred'][referrer] += 1
                data['balance'][referrer] += Per_Refer
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

        gift_message = """Taklif qilish uchun maxsus linkingizni oling va do'stlaringizni jamoamizga taklif qiling.
Sizning maxsus linkingiz bu faqat sizga tegishli havola bo'lib, u orqali kanalga qo'shilgan har bir doʻstingiz sizga 1️⃣ ball olib keladi.

Maxsus linkingizni olish uchun pastdagi "Maxsus linkim" tugmasini bosing.

Ballaringizni ko'rish uchun pastdagi "Mening hisobim" tugmasini bosing"""
        bot.send_message(message.chat.id, gift_message)
        menu(message.chat.id)

@bot.message_handler(content_types=['text'])
def send_text(message):
    try:
        user_id = message.chat.id
        if message.text == '🆔 Mening hisobim':
            data = load_users_data()
            user = str(user_id)
            balance = data['balance'].get(user, 0)
            dollar_balance = data['dollar_balance'].get(user, 0.0)
            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(telebot.types.InlineKeyboardButton(text=f"Balans: {balance} Ball", callback_data='balance'))
            msg = f"Foydalanuvchi: @{message.from_user.username}\nBallar: {balance} {TOKEN}\nDollar balans: ${dollar_balance}"
            bot.send_message(user_id, msg, reply_markup=markup)
        elif message.text == '🙌🏻 Maxsus linkim':
            send_invite_link(user_id)
        elif message.text == "📊 Statistika" and user_id == OWNER_ID:
            data = load_users_data()
            bot.send_message(user_id, f"Jami foydalanuvchilar: {data['total']}")
        elif message.text == "Talabalarni hisoblash" and user_id == OWNER_ID:
            bot.send_message(user_id, "Iltimos, qo'shilgan talabaning username'ni kiriting (masalan, @username):")
            bot.register_next_step_handler(message, process_student_username)
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
        
        referrer = data['referby'].get(str(buyer_id), str(buyer_id))
        app.logger.info(f"Checking addstudent for @{username}: buyer_id={buyer_id}, referrer={referrer}")
        
        if str(referrer) not in data['dollar_balance']:
            data['dollar_balance'][str(referrer)] = 0.0
            app.logger.info(f"Created dollar_balance for referrer {referrer} with value 0.0")
        
        referrer = str(referrer)
        data['dollar_balance'][referrer] += 5.0
        save_users_data(data)
        
        bot.send_message(message.chat.id, f"@{username} {referrer} uchun qayd qilindi. +5$ qo‘shildi.")
        bot.send_message(referrer, f"Siz taklif qilgan @{username} yopiq guruhga qo‘shildi! +5$ qo‘shildi.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Xatolik: {str(e)}")
        app.logger.error(f"Error in add_student: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data == 'calculate_students')
def handle_calculate_students(call):
    try:
        user_id = call.message.chat.id
        if user_id != OWNER_ID:
            bot.answer_callback_query(callback_query_id=call.id, text="Bu funksiya faqat bot egasiga mavjud.")
            return
            
        app.logger.info(f"Admin {user_id} pressed 'Talabalarni hisoblash' button")
        bot.send_message(user_id, "Iltimos, qo'shilgan talabaning username'ni kiriting (masalan, @username):")
        bot.register_next_step_handler(call.message, process_student_username)
    except Exception as e:
        bot.send_message(user_id, "Xatolik yuz berdi")
        bot.send_message(OWNER_ID, f"Xatolik handle_calculate_students’da: {str(e)}")
        app.logger.error(f"Error in handle_calculate_students: {str(e)}")

def process_student_username(message):
    try:
        user_id = message.chat.id
        if user_id != OWNER_ID:
            bot.send_message(user_id, "Bu funksiya faqat bot egasiga mavjud.")
            return
            
        app.logger.info(f"Admin {user_id} entered username: {message.text}")
        username = message.text.replace('@', '')
        mock_message = type('MockMessage', (), {'chat': type('Chat', (), {'id': user_id}), 'text': f'/addstudent @{username}'})()
        add_student(mock_message)
    except Exception as e:
        bot.send_message(user_id, "Xatolik yuz berdi")
        bot.send_message(OWNER_ID, f"Xatolik process_student_username’da: {str(e)}")
        app.logger.error(f"Error in process_student_username: {str(e)}")

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
