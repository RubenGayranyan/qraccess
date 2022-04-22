import qrcode
import random
from datetime import datetime
import telebot
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
import threading
import mysql.connector as MySQL
import re
import time

MySQL_HOST = "https://cp.sprinthost.ru";
MySQL_USER = "f0663527_qr_access";
MySQL_PASSWORD = "gazan444";
MySQL_DB = "f0663527_qr_access";

lock = threading.Lock()
bot = telebot.TeleBot("5239236978:AAFYs8tCXGI9sGh5UhIjNCh9uOqANi1Yp8Y")
eCreate = 0
eMessID = 0
isEditing = "0"
eventName = ""
isOpenedManageMenu = 0

def setCreate(arg):
    global eCreate
    eCreate = arg

def setMessID(arg):
    global eMessID
    eMessID = arg

def setEvName(arg):
    global eventName
    eventName = arg

def setManageMenuState(arg):
    global isOpenedManageMenu
    isOpenedManageMenu = arg

cLetters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U",
            "V", "W", "X", "Y", "Z"]
sLetters = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u",
            "v", "w", "x", "y", "z"]
numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

idCharacters = cLetters + sLetters + numbers

qr = qrcode.QRCode(
    version=1,
    box_size=10,
    border=5)

def runBot():
    dbHandle = MySQL.connect(host=MySQL_HOST, user=MySQL_USER, password=MySQL_PASSWORD, database=MySQL_DB)
    cur = dbHandle.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS eventsList (
        `eID` varchar(64) NOT NULL,
        `eName` varchar(64) NOT NULL,
        `eCreator` varchar(64) NOT NULL,
        `cDate` datetime DEFAULT CURRENT_TIMESTAMP,
        `rDate` datetime,
        `chatID` bigint(32) NOT NULL,
        `messageID1` bigint(32) NOT NULL,
        `messageID2` bigint(32) NOT NULL,
        `eDescription` longtext NOT NULL,
        `eCreatorID` bigint(32) NOT NULL
    )''')
    dbHandle.commit()

    @bot.message_handler(commands=["start", "help"])
    def send_welcome(message):
        fName = message.from_user.first_name
        bot.send_message(message.chat.id, "Hi " + fName + "! I'll help you to create an event.\n\n\
    /newevent - Add a new event (only for chats).\n\
    /myevents - Check your events list.", parse_mode="HTML")

    @bot.message_handler(commands=["myevents"])
    def sendParticipantsList(message):
        keyboard = telebot.types.InlineKeyboardMarkup()
        with lock:
            cur.execute(f"SELECT * FROM `eventsList` WHERE `eCreatorID` = {message.from_user.id}")
            eventsList = list(cur)
        if len(eventsList) != 0:
            for row in eventsList:
                button_join = telebot.types.InlineKeyboardButton(text=str(row[1]), callback_data='info_' + str(row[0]))
                keyboard.add(button_join)
                print(row[0])
            bot.send_message(message.from_user.id, f"You have created {len(eventsList)} events:", reply_markup=keyboard)
        else:
            bot.send_message(message.from_user.id, "You haven't created events yet.")

    @bot.callback_query_handler(func=DetailedTelegramCalendar.func())
    def cal(c):
        result, key, step = DetailedTelegramCalendar().process(c.data)
        if not result and key:
            if isEditing == "0":
                bot.edit_message_text(f"Please select the {LSTEP[step]}", c.message.chat.id, c.message.message_id,
                                      reply_markup=key)
            else:
                bot.edit_message_text(f"Please new select the {LSTEP[step]}", c.message.chat.id, c.message.message_id,
                                      reply_markup=key)

        elif result:
            if isEditing == "0":
                bot.edit_message_text(f"The date has been selected: {result}", c.message.chat.id, c.message.message_id)
            else:
                bot.edit_message_text(f"The new date has been selected: {result}", c.message.chat.id,
                                      c.message.message_id)

            global eventDate
            eventDate = result
            setCreate(3)
            bot.send_message(c.from_user.id, f"Please enter the time (HH:MM):")

    @bot.callback_query_handler(func=lambda call: True)
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
                    bot.send_message(call.from_user.id, "You've already joined that event. (<b>{0}</b>)".format(row[1]),
                                     parse_mode="HTML")
                break
            if call.data == "un_" + str(row[0]):
                with lock:
                    cur.execute(
                        "SELECT messageID1, messageID2 FROM {0} WHERE userID = '{1}'".format(row[0], call.from_user.id))
                    userData = list(cur)
                if len(userData) != 0:
                    bot.edit_message_text(
                        "You leaved the event [ <b>{0}</b> ]! Your QR was removed from database.".format(row[1]),
                        call.from_user.id, userData[0][1], parse_mode="html")
                    cur.execute("DELETE FROM {0} WHERE userID = {1}".format(str(row[0]), call.from_user.id))
                    dbHandle.commit()
                else:
                    bot.send_message(call.from_user.id, "You've not joined the event yet. (<b>{0}</b>)".format(row[1]),
                                     parse_mode="HTML")
                break
            if call.data == "delete_" + str(row[0]):
                with lock:
                    cur.execute(
                        "SELECT chatID, messageID1, messageID2, eName FROM eventsList WHERE eID = '{0}'".format(row[0]))
                    eventInfo = list(cur)
                bot.edit_message_text("<i>Event <b>{0}</b> has been removed!</i>".format(eventInfo[0][3]),
                                      eventInfo[0][0], eventInfo[0][1], parse_mode="html")
                bot.edit_message_text(
                    "<i>Your event was removed from database! (<b>{0}</b>)</i>".format(eventInfo[0][3]),
                    call.from_user.id, eventInfo[0][2], parse_mode="html")
                cur.execute("DROP TABLE IF EXISTS {0}".format(str(row[0])))
                dbHandle.commit()
                cur.execute("DELETE FROM `eventsList` WHERE `eID` = '{0}'".format(str(row[0])))
                dbHandle.commit()
                if isOpenedManageMenu == 1:
                    bot.send_message(call.from_user.id,
                                     "Your event was removed the event from database! (<b>{0}</b>)".format(
                                         eventInfo[0][3]), parse_mode="html")
            if call.data == "edit_" + str(row[0]):
                bot.send_message(call.from_user.id, "Please enter event's new name:")
                setCreate(1)
                setMessID(call)
                global isEditing
                isEditing = str(row[0])
            if call.data == "info_" + str(row[0]):
                setManageMenuState(1)
                print(str(row[0]))
                keyboard = telebot.types.InlineKeyboardMarkup()
                with lock:
                    cur.execute(f"SELECT * FROM {row[0]}")
                    eventInfo = list(cur)
                button_join = telebot.types.InlineKeyboardButton(text='Participants list',
                                                                 callback_data='partList_' + str(row[0]))
                keyboard.add(button_join)
                button_join = telebot.types.InlineKeyboardButton(text='Edit this event',
                                                                 callback_data='edit_' + str(row[0]))
                keyboard.add(button_join)
                button_join = telebot.types.InlineKeyboardButton(text='Delete this event',
                                                                 callback_data='delete_' + str(row[0]))
                keyboard.add(button_join)
                bot.edit_message_text(f"{len(eventInfo)} people have joined this event [{row[1]}]:", call.from_user.id,
                                      call.message.message_id, parse_mode="html", reply_markup=keyboard)
            if call.data == "partList_" + str(row[0]):
                keyboard = telebot.types.InlineKeyboardMarkup()
                with lock:
                    cur.execute("SELECT * FROM {0}".format(row[0]))
                    eventInfo = list(cur)
                if len(eventInfo) != 0:
                    integer = 1
                    string = "<b>[First Name] - [Username] - [Date of joining]</b>\n"
                    for sRow in eventInfo:
                        string += str(integer) + ". " + str(sRow[3]) + " - @" + str(sRow[2]) + " - " + str(
                            sRow[5]) + "\n"
                        integer += 1
                    bot.send_message(call.from_user.id, string, parse_mode="html")
                else:
                    bot.send_message(call.from_user.id, "Nobody joined this event yet.")

    @bot.message_handler(commands=["newevent"])
    def new_event(message):
        if bot.get_chat_member(message.chat.id, message.from_user.id).status == "creator" or bot.get_chat_member(
                message.chat.id, message.from_user.id).status == "administrator":
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
        elif eCreate == 3:
            if re.match("^(2[0-3]|[01]?[0-9]):([0-5]?[0-9])$", message.text) == None:
                bot.send_message(message.from_user.id, f"Please enter the time (HH:MM):")
            else:
                global eventDate
                eventDate = str(eventDate) + " " + message.text + ":00"
                setCreate(4)
                bot.send_message(message.from_user.id, f"Please enter the event description:")
        elif eCreate == 4:
            global eDescription
            eDescription = message.text
            create_new_event(eMessID, eventName, eventDate, eDescription)

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
        print(img.save('/home/pi/qraccess/database/' + unicalID + '.jpg'))
        time.sleep(2)
        message = bot.send_photo(user.id, open('/home/pi/qraccess/database/' + unicalID + '.jpg', 'rb'))

        string = "You've joined the event [ <b>{0}</b> ]! Here's your unique QR.".format(evName)
        keyboard = telebot.types.InlineKeyboardMarkup()
        button_join = telebot.types.InlineKeyboardButton(text='Cancel', callback_data='un_' + evID)
        keyboard.add(button_join)
        message1 = bot.send_message(user.id, string, parse_mode="HTML", reply_markup=keyboard)

        sqlStr = '''INSERT INTO {0} (unicalID, userID, userName, fName, lName, rDate, messageID1, messageID2) VALUES ('{1}', '{2}', '{3}', '{4}', '{5}', '0', {6}, {7})'''.format(
            input_data['eventID'], input_data['unicalID'], input_data['userID'], input_data['userName'],
            input_data['fName'], input_data['lName'], message.message_id, message1.message_id)
        cur.execute(sqlStr)
        dbHandle.commit()

    def create_new_event(eMessID, eName, eDate, eDesc):
        setCreate(0)
        if isEditing == "0":
            tempID = random.sample(idCharacters, 6)
            tempUnique = "".join(tempID)
            eventUnique = "Event_" + tempUnique
            now = datetime.now()
            postObject = {
                "eID": eventUnique,
                "eCreator": eMessID.from_user.first_name,
                "cDate": now.strftime("%Y-%m-%d %H:%M:%S"),
                "rDate": eDate
            }
            cur.execute('''CREATE TABLE {0} (
                `unicalID` varchar(64) UNIQUE NOT NULL,
                `userID` int(11) NOT NULL,
                `userName` varchar(64) NOT NULL,
                `fName` varchar(64) NOT NULL,
                `lName` varchar(64) NOT NULL,
                `cDate` datetime DEFAULT CURRENT_TIMESTAMP,
                `rDate` datetime DEFAULT CURRENT_TIMESTAMP,
                `messageID1` bigint(32) NOT NULL,
                `messageID2` bigint(32) NOT NULL
            )'''.format(eventUnique))
            dbHandle.commit()

            keyboard1 = telebot.types.InlineKeyboardMarkup()
            button_join1 = telebot.types.InlineKeyboardButton(text='Edit', callback_data='edit_' + eventUnique)
            keyboard1.add(button_join1)
            button_join2 = telebot.types.InlineKeyboardButton(text='Delete', callback_data='delete_' + eventUnique)
            keyboard1.add(button_join2)
            messagec = bot.send_message(eMessID.from_user.id, "You've created an event <b>{0}</b>!".format(eName),
                                        parse_mode="HTML", reply_markup=keyboard1)
            str = "<b>{0}</b> created an event [ <b>{1}</b> - <b>{2}</b> ].\n\n<i>{3}</i>\n\n<b>Would you like to join?</b>".format(
                eMessID.from_user.first_name, eName, eDate, eDesc)
            keyboard = telebot.types.InlineKeyboardMarkup()
            button_join = telebot.types.InlineKeyboardButton(text='Join the event!',
                                                             callback_data='join_' + eventUnique)
            keyboard.add(button_join)
            message = bot.send_message(eMessID.chat.id, str, parse_mode="HTML", reply_markup=keyboard)
            sqlStr = "INSERT INTO `eventsList`(`eID`, `eName`, `eCreator`, `rDate`, `chatID`, `messageID1`, `messageID2`, `eDescription`, `eCreatorID`) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', \"{7}\", '{8}')".format(
                postObject['eID'], eName, postObject['eCreator'], eventDate, eMessID.chat.id, message.message_id,
                messagec.message_id, eDesc, eMessID.from_user.id)
            cur.execute(sqlStr)
            dbHandle.commit()
        else:
            with lock:
                cur.execute("SELECT * FROM `eventsList` WHERE eID = '{0}'".format(isEditing))
                eventInfo = list(cur)

            str = "<b>{0}</b> created an event [ <b>{1}</b> - <b>{2}</b> ].\n\n<i>{3}</i>\n\n<b>Would you like to join?</b> <i>(Edited)</i>".format(
                eMessID.from_user.first_name, eName, eDate, eDesc)
            keyboard = telebot.types.InlineKeyboardMarkup()
            button_join = telebot.types.InlineKeyboardButton(text='Join the event!',
                                                             callback_data='join_' + eventInfo[0][0])
            keyboard.add(button_join)
            bot.edit_message_text(str, eventInfo[0][5], eventInfo[0][6], reply_markup=keyboard, parse_mode="HTML")
            bot.send_message(eventInfo[0][5],
                             "{0} edited the event! (<i>{1}</i>)".format(eventInfo[0][2], eventInfo[0][1]),
                             parse_mode="HTML", reply_to_message_id=eventInfo[0][6])
            if isOpenedManageMenu == 1:
                bot.send_message(eMessID.from_user.id,
                                 "Your event was edited successfully! (<b>{0}</b>)".format(eventInfo[0][2]),
                                 parse_mode="html")
            sqlStr = '''UPDATE `eventsList` SET `eName`="{0}", `rDate`="{1}", `eDescription`="{2}" WHERE `eID` = "{3}"'''.format(
                eName, eventDate, eDesc, isEditing)
            cur.execute(sqlStr)
            dbHandle.commit()

    bot.polling(none_stop=True, interval=0)
    dbHandle.close()

while True:
    try:
        runBot()
    except Exception as e:
        bot.send_message(838233402, e)