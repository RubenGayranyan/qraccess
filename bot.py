import qrcode
import random
from datetime import datetime
import telebot
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
import threading
import mysql.connector as MySQL


MySQL_HOST = "141.8.192.151";
MySQL_USER = "f0658097_tg";
MySQL_PASSWORD = "hapaumucdi";
MySQL_DB = "f0658097_tg";

dbHandle = MySQL.connect(host = MySQL_HOST, user = MySQL_USER, password = MySQL_PASSWORD, database = MySQL_DB)

print(dbHandle)

lock = threading.Lock()

bot = telebot.TeleBot("5239236978:AAFYs8tCXGI9sGh5UhIjNCh9uOqANi1Yp8Y")

eCreate = 0
eMessID = 0
eventName = ""

cur = dbHandle.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS eventsList (
    `rID` INTEGER PRIMARY KEY AUTOINCREMENT,
    `eID` VARCHAR UNIQUE NOT NULL,
    `eName` VARCHAR NOT NULL,
    `eCreator` VARCHAR NOT NULL,
    `cDate` VARCHAR NOT NULL,
    `rDate` VARCHAR DEFAULT 0,
    `chatID` INTEGER NOT NULL,
    `messageID1` INTEGER NOT NULL,
    `messageID2` INTEGER NOT NULL
)''')

dbHandle.commit();

def setCreate(arg):
    global eCreate
    eCreate = arg

def setMessID(arg):
    global eMessID
    eMessID = arg

def setEvName(arg):
    global eventName
    eventName = arg

cLetters = [ "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z" ]
sLetters = [ "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z" ]
numbers = [ "0", "1", "2", "3", "4", "5", "6", "7", "8", "9" ]

idCharacters = cLetters + sLetters + numbers

qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=5)
        
@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    fName = message.from_user.first_name
    bot.send_message(message.chat.id, "Hi " + fName + "! I'll help you to create an event.\n\n\
/newevent - Add a new event.\n\
/myevents - Check your events list\n\
/allevents - Check all events list.", parse_mode="HTML")

@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def cal(c):
    result, key, step = DetailedTelegramCalendar().process(c.data)
    if not result and key:
        bot.edit_message_text(f"Please select the {LSTEP[step]}",
                              c.message.chat.id,
                              c.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"The date has been selected: {result}",
                              c.message.chat.id,
                              c.message.message_id)
        global eventDate
        eventDate = result
        setCreate(3)
        bot.send_message(eMessID.from_user.id, f"Please enter the time (HH:MM):")

@bot.callback_query_handler(func=lambda call:True)
def callback_worker(call):
    with lock:
        cur.execute("SELECT eID, eName FROM eventsList WHERE 1")
        data = list(cur)
    for row in data:
        if call.data == "join_" + str(row[0]):
            with lock:
                cur.execute("SELECT * FROM {0} WHERE userID = '{1}'".format(row[0], call.from_user.id))
                userData = list(cur)
            if len(userData) == 0:
                send_code(call.from_user, row[0], row[1])
            else:
                bot.send_message(call.from_user.id, "You've already joined that event. (<b>{0}</b>)".format(row[0]), parse_mode="HTML")
            break
        if call.data == "un_" + str(row[0]):
            with lock:
                cur.execute("SELECT messageID1, messageID2 FROM {0} WHERE userID = '{1}'".format(row[0], call.from_user.id))
                userData = list(cur)
            if len(userData) != 0:
                bot.edit_message_text("You leaved the event [ <b>{0}</b> ]! Your QR was removed from database.".format(row[1]), call.from_user.id, userData[0][1], parse_mode="html")
                cur.execute("DELETE FROM '{0}' WHERE `userID` = {1}".format(str(row[0]), call.from_user.id))
            else:
                bot.send_message(call.from_user.id, "You've not joined the event yet. (<b>{0}</b>)".format(row[0]), parse_mode="HTML")
            break
        if call.data == "delete_" + str(row[0]):
            with lock:
                cur.execute("SELECT chatID, messageID1, messageID2, eName FROM eventsList WHERE eID = '{0}'".format(row[0]))
                eventInfo = list(cur)

            bot.edit_message_text("<i>Event <b>{0}</b> has been removed!</i>".format(eventInfo[0][3]), eventInfo[0][0], eventInfo[0][1], parse_mode="html")
            bot.edit_message_text("<i>Your event was removed from database! (<b>{0}</b>)</i>".format(eventInfo[0][3]), call.from_user.id, eventInfo[0][2], parse_mode="html")
            cur.execute("DROP TABLE IF EXISTS {0}".format(str(row[0])))
            cur.execute("DELETE FROM 'eventsList' WHERE `eID` = {0}".format(call.data))


@bot.message_handler(commands=["newevent"])
def new_event(message):
    if bot.get_chat_member(message.chat.id, message.from_user.id).status == "creator" or bot.get_chat_member(message.chat.id, message.from_user.id).status == "administrator":
        bot.send_message(message.from_user.id, "Please enter event's name:")
        setMessID(message)
        setCreate(1)

@bot.message_handler(content_types=["text"])
def get_new_event_info(message):
        if eCreate == 1:
            global eventName
            setEvName(message.text)
            setCreate(2)
            calendar, step = DetailedTelegramCalendar().build()
            bot.send_message(message.from_user.id, f"Please select the {LSTEP[step]}:", reply_markup=calendar)
        if eCreate == 3:
            global eventDate
            eventDate = str(eventDate) + " " + message.text
            create_new_event(eMessID, eventName, eventDate)

def send_code(user, evID, evName):
    now = datetime.now()

    uID = user.id
    uName = user.username

    fName = user.first_name
    lName = user.last_name
    currentDate = now.strftime("%Y-%m-%d %H:%M")

    tempID = random.sample(idCharacters, 24)
    unicalID = "".join(tempID)

    input_data = {
        "unicalID": unicalID,
        "userID": uID,
        "userName": uName,
        "eventID": evID,
        "fName": fName,
        "lName": lName,
        "cDate": currentDate
    }

    qr.add_data(input_data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    img.save('database/'+ unicalID + '.png')
    message = bot.send_photo(user.id, open('database/' + unicalID + '.png', 'rb'))

    string = "You've joined the event [ <b>{0}</b> ]! Here's your unique QR.".format(evName)
    keyboard = telebot.types.InlineKeyboardMarkup()
    button_join = telebot.types.InlineKeyboardButton(text='Cancel', callback_data='un_' + evID)
    keyboard.add(button_join)
    message1 = bot.send_message(user.id, string, parse_mode="HTML", reply_markup=keyboard)

    sqlStr = '''INSERT INTO {0} (unicalID, userID, userName, fName, lName, cDate, rDate, messageID1, messageID2) VALUES ('{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '0', {7}, {8})'''.format(input_data['eventID'], input_data['unicalID'], input_data['userID'], input_data['userName'], input_data['fName'], input_data['lName'], input_data['cDate'], message.message_id, message1.message_id)
    cur.execute(sqlStr)
    dbHandle.commit()

def create_new_event(eMessID, eName, eDate):
    tempID = random.sample(idCharacters, 6)
    tempUnique = "".join(tempID)
    eventUnique = "Event_" + tempUnique
    now = datetime.now()
    postObject = {
        "eID": eventUnique,
        "eCreator": eMessID.from_user.first_name,
        "cDate": now.strftime("%Y-%m-%d %H:%M:%S"),
        "rDate": eDate + ":00"
    }
    cur.execute('''CREATE TABLE {0} (
        `rKey` INTEGER PRIMARY KEY AUTOINCREMENT,
        `unicalID` VARCHAR UNIQUE NOT NULL,
        `userID` INTEGER NOT NULL,
        `userName` VARCHAR NOT NULL,
        `fName` VARCHAR NOT NULL,
        `lName` VARCHAR NOT NULL,
        `cDate` VARCHAR NOT NULL,
        `rDate` VARCHAR NOT NULL,
        `messageID1` INTEGER NOT NULL,
        `messageID2` INTEGER NOT NULL
      )'''.format(eventUnique))
    dbHandle.commit();

    keyboard1 = telebot.types.InlineKeyboardMarkup()
    button_join1 = telebot.types.InlineKeyboardButton(text='Edit', callback_data='edit_' + eventUnique)
    keyboard1.add(button_join1)
    button_join2 = telebot.types.InlineKeyboardButton(text='Delete', callback_data='delete_' + eventUnique)
    keyboard1.add(button_join2)
    messagec = bot.send_message(eMessID.from_user.id, "You've created an event <b>{0}</b>!".format(eName), parse_mode="HTML", reply_markup=keyboard1)
    str = "<b>{0}</b> created an event [ <b>{1}</b> - <b>{2}</b> ].\nWould you like to join?".format(eMessID.from_user.first_name, eName, eDate)
    keyboard = telebot.types.InlineKeyboardMarkup()
    button_join = telebot.types.InlineKeyboardButton(text='Join the event!', callback_data='join_' + eventUnique)
    keyboard.add(button_join)
    message = bot.send_message(eMessID.chat.id, str, parse_mode="HTML", reply_markup=keyboard)
    sqlStr = '''INSERT INTO eventsList (eID, eCreator, eName, cDate, rDate, chatID, messageID1, messageID2) VALUES ('{0}', '{1}', '{2}', '{3}', '0', {4}, {5}, {6})'''.format(postObject['eID'], postObject['eCreator'], eName, postObject['cDate'], message.chat.id, message.message_id, messagec.message_id)
    cur.execute(sqlStr)
    dbHandle.commit()

bot.polling(none_stop=True, interval=0)
dbHandle.close()