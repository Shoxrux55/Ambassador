import json
import telebot
from flask import Flask, request

# TOKEN DETAILS
TOKEN = "Ball"
BOT_TOKEN = "7580694173:AAERNuW1PATTh_LC_WyKahR2pmR052RDUjc"
PAYMENT_CHANNEL = "@Endoland"  # Add payment channel here including the '@' sign
OWNER_ID = 725821571  # Write owner's user id here, get it from @MissRose_Bot by /id
CHANNELS = ["@Endoland"]  # Add channels to be checked here in the format - ["Channel 1", "Channel 2"]
Daily_bonus = 1  # Put daily bonus amount here
Per_Refer = 1  # Add per refer bonus here

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

ADMIN_GROUP_USERNAME = "@endocrineqatnashchi"  # Replace with your admin group username

# Log yozuvlarini saqlash uchun ro'yxat
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

@app.route('/logs')
def get_logs():
    return '<br>'.join(log_messages)

# Your existing bot functions go here...
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
            "withd": {},
            "id": {},
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
        video_file_ids = ["https://t.me/marafonbotbazasi/7"]  # Replace with actual video file ID
        send_videos(user_id, video_file_ids)
        bot.send_message(user_id, '1-dars video sizga jo‘natildi.')
    elif 10 <= balance < 20:
        video_file_ids = [
            "https://t.me/marafonbotbazasi/7",  # Replace with actual video file ID
            "https://t.me/marafonbotbazasi/8"   # Replace with actual video file ID
        ]
        send_videos(user_id, video_file_ids)
        bot.send_message(user_id, '1-dars va 2-dars videolar sizga jo‘natildi.')
    elif balance >= 20:
        video_file_ids = [
            "https://t.me/marafonbotbazasi/7",  # Replace with actual video file ID
            "https://t.me/marafonbotbazasi/8",  # Replace with actual video file ID
            "https://t.me/marafonbotbazasi/9"   # Replace with actual video file ID
        ]
        send_videos(user_id, video_file_ids)
        bot.send_message(user_id, '1-dars, 2-dars, va 3-dars videolar sizga jo‘natildi.')
    else:
        bot.send_message(user_id, 'Kechirasiz, ballaringiz yetarli emas.')

@bot.message_handler(commands=['start'])
def start(message):
    try:
        user = message.chat.id
        msg = message.text
        user = str(user)
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
        if user not in data['withd']:
            data['withd'][user] = 0
        if user not in data['id']:
            data['id'][user] = data['total'] + 1
        save_users_data(data)
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton(
            text='Marafon kanaliga qo‘shilish', url='https://t.me/medstone_usmle'))
        markup.add(telebot.types.InlineKeyboardButton(
            text='Obunani tekshirish', callback_data='check'))
        msg_start = """Tabriklayman! Siz marafon qatnashchisi bo'lishga yaqin qoldingiz.
7 kunlik bepul marafon davomida quyidagi mavzularni o'rganamiz:

✅- Diabet
\n✅- Diabet skriningi
\n✅- PCOS
\n✅- Giperandrogenizm
\n✅- Qandsiz diabet
\n✅- Osteoporoz

Shu mavzulardagi eng so'nggi yangiliklarni o'zlashtirishni xohlasangiz hoziroq marafon bo'lib o'tadigan kanalga qo'shiling."""
        bot.send_message(user, msg_start, reply_markup=markup)
    except Exception as e:
        bot.send_message(message.chat.id, "Bu buyruqda xatolik bor, iltimos admin xatoni tuzatishini kuting")
        bot.send_message(OWNER_ID,
                         "Botingizda xatolik bor, uni tezda tuzating!\n Xato komandada: " + message.text + "\nXatolik: " + str(e))
        return

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
                        bot.send_message(
                            ref_id,
                            f"Do'stingiz kanalga qo'shildi va siz +{Per_Refer} {TOKEN} ishlab oldingiz"
                        )
                    save_users_data(data)

                # Send message asking for phone number confirmation
                markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                markup.add(telebot.types.KeyboardButton(text='Raqamni ulashish', request_contact=True))
                bot.send_message(call.message.chat.id, f"Salom, @{username}! \nSizga bonuslarimizni bera olishimiz uchun raqamingizni tasdiqlay olasizmi?\nPastdagi maxsus tugmani bossangiz kifoya.", reply_markup=markup)

            else:
                bot.answer_callback_query(callback_query_id=call.id, text='Siz hali kanalga qo‘shilmadingiz')
                markup = telebot.types.InlineKeyboardMarkup()
                markup.add(telebot.types.InlineKeyboardButton(
                    text='Obunani tekshirish', callback_data='check'))
                msg_start = "Ushbu botdan foydalanish uchun quyidagi kanalga qo‘shiling\nva Obunani tekshirish tugmasini bosing\n\n - @medstone_usmle"
                bot.send_message(call.message.chat.id, msg_start, reply_markup=markup)
    except Exception as e:
        bot.send_message(call.message.chat.id, "Bu buyruqda xatolik bor, iltimos admin xatoni tuzatishini kuting")
        bot.send_message(OWNER_ID, f"Botingizda xatolik bor, uni tezda tuzating!\n Xato komandada: {call.data}\nXatolik: {str(e)}")
        return

@bot.message_handler(content_types=['contact'])
def contact(message):
    if message.contact is not None:
        contact = message.contact.phone_number
        username = message.from_user.username
        bot.send_message(ADMIN_GROUP_USERNAME, f"Foydalanuvchi: @{username}\nTelefon raqami: {contact}")

        # Xabar va inline tugmalar
        inline_markup = telebot.types.InlineKeyboardMarkup()
        inline_markup.add(telebot.types.InlineKeyboardButton(text="Sovg'angiz👇", callback_data='gift'))

        gift_message = """Siz uchun tayyorlab qo'ygan sovg'alarimizni kutib oling🤗

1️⃣. Kanalimizning yangi mehmonlari uchun Shoxrux Botirov tomonidan maxsus tayyorlangan bonus video darsni raqamingizni tasdiqlash orqali qabul qilib oling
Uni pastdagi "Raqamni ulashish📞 va Mening sovgʻam🎁" tugmasini bosish orqali olishingiz mumkin.

2️⃣. Bor yo'g'i 10 ta odam qo'shish orqali avval 650 mingdan sotilgan leksiyalar to'plamiga mansub 1 ta dolzarb mavzu leksiyasini BEPUL olish imkoniyati

3️⃣. 20 ta odam qo'shish orqali avval 650 mingdan sotilgan leksiyalar to'plamiga mansub 2 ta video darsni case tahlillari bilan birga BEPUL olish imkoniyati.

4️⃣. 30 ta odam qo'shish orqali yuqoridagi pullik kanalga tegishli 3 ta darsni batafsil case tahlillari bilan BEPUL qo'lga kiritish imkoniyati.

Taklif qilish uchun maxsus linkingizni oling va do'stlaringizni jamoamizga taklif qiling.
Sizning maxsus linkingiz bu faqat sizga tegishli havola bo'lib, u orqali kanalga qo'shilgan har bir doʻstingiz sizga 1️⃣ ball olib keladi.

Maxsus linkingizni olish uchun pastdagi "Maxsus linkim" tugmasini bosing.

Ballaringizni ko'rish uchun pastdagi "Mening hisobim" tugmasini bosing"""

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
            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(telebot.types.InlineKeyboardButton(text=f"Balans: {balance} Ball", callback_data='balance'))
            msg = f"Foydalanuvchi: {username}\nBalans: {balance} {TOKEN}"
            bot.send_message(call.message.chat.id, msg, reply_markup=markup)

        elif call.data == 'ref_link':
            send_invite_link(call.message.chat.id)

        elif call.data == 'gift':
            send_gift_video(user_id)

    except Exception as e:
        bot.send_message(call.message.chat.id, "Bu buyruqda xatolik bor, iltimos admin xatoni tuzatishini kuting")
        bot.send_message(OWNER_ID, f"Botingizda xatolik bor, uni tezda tuzating!\n Xato komandada: {call.data}\nXatolik: {str(e)}")

def send_invite_link(user_id):
    data = load_users_data()
    bot_name = bot.get_me().username
    user = str(user_id)

    if user not in data['referred']:
        data['referred'][user] = 0
    save_users_data(data)

    ref_link = f'https://telegram.me/{bot_name}?start={user_id}'
    msg = (f"ENDOKRINOLOGIYA BOʻYICHA OCHIQ DARSLAR\n\nKlinik Endokrinologiya bo'yicha unikal hisoblangan kurs asosida tayyorlangan BEPUL marafonda "
           f"qatnashmoqchi bo'lsangiz quyidagi havola orqali jamoamizga qo'shiling!\n"
           f"Vaqt va joylar chegaralangan ekanligini unutmang azizlar!\n"
           f"Yana bir marta eslatib o'taman Marafon hamma uchun ochiq va bepul.\n\n"
           f"Taklifnoma havolasi: {ref_link}")
    bot.send_message(user_id, msg)

@bot.message_handler(content_types=['text'])
def send_text(message):
    try:
        if message.text == '🆔 Mening hisobim':
            data = load_users_data()
            user_id = message.chat.id
            user = str(user_id)
            balance = data['balance'].get(user, 0)
            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(telebot.types.InlineKeyboardButton(text=f"Balans: {balance} Ball", callback_data='balance'))
            msg = f"Foydalanuvchi: {message.from_user.username}\nBalans: {balance} {TOKEN}"
            bot.send_message(message.chat.id, msg, reply_markup=markup)
        if message.text == '🙌🏻 Maxsus linkim':
            send_invite_link(message.chat.id)
        if message.text == '🎁 Mening sovg\'am':
            send_gift_video(message.chat.id)
        if message.text == "📊 Statistika":
            if message.chat.id == OWNER_ID:
                user_id = message.chat.id
                user = str(user_id)
                data = load_users_data()
                msg = "Jami foydalanuvchilar: {} foydalanuvchilar"
                msg = msg.format(data['total'])
                bot.send_message(user_id, msg)
            else:
                bot.send_message(message.chat.id, "Ushbu buyruq faqat bot egasiga mavjud.")
            return
    except Exception as e:
        bot.send_message(message.chat.id, "Bu buyruqda xatolik bor, iltimos admin xatoni tuzatishini kuting")
        bot.send_message(OWNER_ID, "Botingizda xatolik bor, uni tezda tuzating!\n Xato komandada: " + message.text + "\nXatolik: " + str(e))
        return

@bot.message_handler(content_types=['video'])
def handle_video(message):
    # Video fayl ID sini olish
    video_file_id = message.video.file_id
    bot.send_message(message.chat.id, f"Video fayl ID si: {video_file_id}")

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
