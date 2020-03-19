import telebot
from telebot import types
import mysql.connector
import datetime

bot = telebot.TeleBot('API_KEY')

@bot.message_handler(commands=['start'])
def start(message):
    user_markup=telebot.types.ReplyKeyboardMarkup(True,False)
    user_markup.row('/start','/stop')
    user_markup.row('location','about')
    user_markup.row('search')
    bot.send_message(message.from_user.id,"Hi,{0}! Welcome to the official Bot Creative Web".format(message.from_user.first_name),reply_markup=user_markup)

@bot.message_handler(commands=['stop'])
def start(message):
    hide_markup=telebot.types.ReplyKeyboardRemove()
    bot.send_message(message.from_user.id,"Bye :)",reply_markup=hide_markup)

@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text == 'location':
        bot.send_chat_action(message.from_user.id,'find_location')
        bot.send_location(message.from_user.id,40.178671, 44.518931)
    elif message.text == 'search':
        bot.send_message(message.from_user.id,"Write the profession You want")
        bot.register_next_step_handler(message,profession)
    elif message.text == 'about':
        bot.send_message(message.from_user.id,"BOT")

def profession(message):
    global msg
    msg = message.text[0:2]
    user_markup=telebot.types.ReplyKeyboardMarkup(True,False)
    db = mysql.connector.connect(host= "host",     \
                                    user= "user",\
                                    password= "password", \
                                    db= "db"   ) 
    cur=db.cursor() 
    cur.execute(f"SELECT cvs.filename, cvs.id, cvs.name, cvs.surname \
                FROM cvs                             \
                INNER JOIN cv_professions as cvp     \
                    ON cvs.id = cvp.cv_id            \
                INNER JOIN professions as pro        \
                    ON cvp.profession_id = pro.id    \
                JOIN profession_translations as lang \
                    ON lang.profession_id = pro.id and lang.title LIKE '{msg}%'  \
                GROUP BY cvs.id LIMIT 10")
    result= cur.fetchall()
    bot.send_message(message.from_user.id,"suitable employees")
    for res in result:
        bot.send_message(message.from_user.id,f"{res[2]} {res[3]}")
        bot.send_message(message.from_user.id,f"Your_Link")
    quest = 'Do You want to continue filtering?'  
    user_markup.row('Yes')
    user_markup.row('No')
    bot.send_message(message.from_user.id, text=quest, reply_markup=user_markup)
    bot.register_next_step_handler(message,yes_or_no)


def yes_or_no(message):
    if message.text == 'Yes':
        bot.send_message(message.from_user.id, 'minimum work experience (year)?')
        bot.register_next_step_handler(message,experience)       
    elif message.text == 'No':
        user_markup=telebot.types.ReplyKeyboardMarkup(True,False)
        user_markup.row('/start','/stop')
        user_markup.row('location','about')
        user_markup.row('search')
        bot.send_message(message.from_user.id,'Thanks for using our BOT :)',reply_markup=user_markup)
    else: 
        bot.send_message(message.from_user.id, 'Please click button above Yes or No')
        bot.register_next_step_handler(message,yes_or_no)
    
def experience(message):
    global msg
    user_markup=telebot.types.ReplyKeyboardMarkup(True,False)
    user_markup.row('/start','/stop')
    user_markup.row('location','about')
    user_markup.row('search')
    db = mysql.connector.connect(host= "host",     \
                                    user= "user",\
                                    password= "password", \
                                    db= "db"   ) 
    cur=db.cursor()
    cur.execute(f"SELECT cvs.filename,  cvs.id, cvp.profession_id, pro.id,cvs.name, cvs.surname, cv_exp.start, \
                            cv_exp.end, TIMESTAMPDIFF(year,cv_exp.start,IF(cv_exp.end is NULL,CURDATE(),cv_exp.end)) \
                FROM cvs                             \
                INNER JOIN cv_professions as cvp     \
                    ON cvs.id = cvp.cv_id            \
                INNER JOIN professions as pro        \
                    ON cvp.profession_id = pro.id    \
                JOIN profession_translations as lang \
                    ON lang.profession_id = pro.id   \
                INNER JOIN cv_experiances as cv_exp  \
                    ON cv_exp.profession_id = lang.profession_id and cv_exp.cv_id = cvs.id \
                WHERE   lang.title LIKE  '{msg}%' GROUP BY cvs.id,cvp.profession_id,cv_exp.start,cv_exp.end")
    result= cur.fetchall()
    for res in result:
        if  res[8] >= int(message.text):
            bot.send_message(message.from_user.id,f"{res[4]} {res[5]}")
            bot.send_message(message.from_user.id,f"Your_Link")
    bot.send_message(message.from_user.id,'Thanks for using our BOT :)',reply_markup=user_markup)
bot_name=bot.get_me()
print(bot_name.first_name +' at your service....')
bot.polling(none_stop=True, interval=0)
