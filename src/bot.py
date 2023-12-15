import telebot
import enum

import texts
import data

class Status(enum.Enum):
    START=0
    LIST_NEWS=1
    LIST_NOTIFICATION=2
    CREATE_NOTIFICATION=3

####################################################

bot = telebot.TeleBot(texts.TOKEN)
database = None
status = Status.START

def run():
    global database
    with open("database.txt", 'r') as file:
        database = file.read().splitlines()
    bot.infinity_polling()

####################################################

def get_main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for button in texts.BUTTON_MAIN_LIST:
        markup.add(telebot.types.KeyboardButton(button))
    return markup

def get_return_to_main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(telebot.types.KeyboardButton(texts.BUTTON_MAIN))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    status = Status.START
    bot.send_message(message.from_user.id, texts.INTRO, reply_markup=get_main_menu())
    print(status)

@bot.message_handler()
def get_text_messages(message):
    global status
    global database
    print(status)

    if message.text == texts.BUTTON_MAIN:
        bot.send_message(message.from_user.id, texts.INTRO, reply_markup=get_main_menu())
        return

    if (status == Status.START) or (status != Status.START and message.text in texts.BUTTON_MAIN_LIST):
        if (message.text == texts.BUTTON_LIST_NEWS):
            status = Status.LIST_NEWS
            bot.send_message(message.chat.id, texts.ENTER_TYPE, reply_markup=get_return_to_main_menu())

        elif (message.text == texts.BUTTON_LIST_NOTIFICATION):
            status = Status.LIST_NOTIFICATION
            bot.send_message(message.chat.id, texts.LIST_NOTIFICATIONS, reply_markup=get_return_to_main_menu())

        elif (message.text == texts.BUTTON_CREATE_NOTIFICATION):
            status = Status.CREATE_NOTIFICATION
            bot.send_message(message.chat.id, texts.CREATE_NOTIFICATION, reply_markup=get_return_to_main_menu())

        else:
            status = Status.START
            bot.send_message(message.chat.id, texts.ERROR)
        return

    if status == Status.LIST_NEWS:

        # Предобработка входного текста
        tag = data.filter_text(message.text)[0]
        bot.send_message(message.chat.id, texts.SEARCH)

        if tag not in database:
            bot.send_message(message.chat.id, texts.ENTER_ERROR, reply_markup=get_return_to_main_menu())
            return
        
        # Получаем новости
        print("Получение новостей...")
        news_list = data.get_news(data.URL, 100)
        news_list = [(title, url, data.get_tags(url)) for title, url in news_list]

        # Фильтрация новостей на основе запрошенной темы
        print("Фильтрация новостей...")
        filtered_news = list(filter(lambda news: tag in news[2], news_list))
        filtered_news = filtered_news[:min(len(filtered_news), 10)]

        # Собираем финальный текст
        if (len(filtered_news) == 0):
            bot.send_message(message.chat.id, texts.ENTER_NOT_FOUND, reply_markup=get_return_to_main_menu())
            return
        else:
            text = "✔️ Новости по теме " + message.text.capitalize() + ":\n\n"
            for news in filtered_news:
                text += f"{news[0]}\n{news[1]}\n\n"
            bot.send_message(message.chat.id, text, reply_markup=get_return_to_main_menu())
            return
