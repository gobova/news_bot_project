import telebot
from telebot import types

import csv

TOKEN = "6696985238:AAELvfYH6MLKw6SBv8f9ZICTaF2f0Q-qmSE"
bot = telebot.TeleBot(TOKEN)

dataset = None
with open("dataset.tsv", 'r') as file:
    dataset = list(csv.DictReader(file, delimiter='\t'))

@bot.message_handler(commands=['start'])
def start(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Наука')
    btn2 = types.KeyboardButton('Здоровье')
    btn3 = types.KeyboardButton('Общество')
    markup.add(btn1, btn2, btn3)

    text = "👋 Привет! Я помогу тебе быть в курсе всех сообытий! " + \
            "Просто выбери интересующую тебя тему или напиши свою 👋"
    bot.send_message(message.from_user.id, text, reply_markup=markup)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):

    # Предобработка входного текста
    theme = message.text.lower()

    # Фильтрация новостей на основе запрошенной темы
    theme_news = list(filter(lambda x: theme in x['tags'], dataset))
    theme_news = theme_news[:min(len(theme_news), 5)]

    # Собираем финальный текст
    text = f"Новости на тему \"{theme}\":\n\n" 
    for current_theme_news in theme_news:
        text += f"{current_theme_news['title']}\n{current_theme_news['url']}\n\n"

    bot.send_message(message.from_user.id, text)


bot.infinity_polling()