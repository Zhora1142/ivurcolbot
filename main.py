from modules.timetable import Timetable
from datetime import datetime
import yaml
import os
import telebot
from modules.update import upd
import requests
import logging

logging.basicConfig(filename='bot.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

if not os.path.exists('files'):
    os.mkdir('files')

with open('config.yml') as stream:
    config = yaml.safe_load(stream)

bot = telebot.AsyncTeleBot(**config['bot'])

wait = False


@bot.message_handler(commands=['start'])
def start(message):
    text = 'Этот бот поможет тебе всегда быть в курсе своего расписания :)'
    bot.send_message(chat_id=message.chat.id, text=text)


@bot.message_handler(commands=['today'])
def today(message):
    try:
        t = Timetable()
        text = t.day_to_string(datetime.now().weekday() + 1)
    except Exception as e:
        logging.error(msg=f'Timetable getting error: {e}')
        text = 'Произошла ошибка. Попробуй ещё раз через некоторое время.'
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(telebot.types.InlineKeyboardButton(text='🔄Обновить', callback_data='update'))
    keyboard.add(telebot.types.InlineKeyboardButton(text='❌Закрыть', callback_data='delete'))
    bot.send_message(chat_id=message.chat.id, text=text, reply_markup=keyboard, parse_mode='HTML')


@bot.message_handler(content_types=['document'])
def doc(message):
    global wait
    if wait and message.from_user.id == 326911795:
        if message.document.mime_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
            url = bot.get_file_url(file_id=message.document.file_id)
            with open(file='files/result.xlsx', mode='wb') as file:
                data = requests.get(url=url).content
                file.write(data)
                file.close()
            upd(call=message, auto=False, bot=bot, config=config)
            wait = False
        else:
            bot.send_message(chat_id=message.chat.id, text='Расписание должно быть в формате xlsx')


@bot.message_handler(commands=['picture'])
def picture(message):
    try:
        file = requests.get('http://www.ivurcol.net/raspisanie/22.jpg')
    except Exception as e:
        logging.error(f'Timetable picture getting error: {e}')
        bot.send_message(chat_id=message.chat.id, text='Произошла ошибка, попробуйте позже')
    else:
        if file.status_code != 200:
            bot.send_message(chat_id=message.chat.id, text='Произошла ошибка, попробуйте позже')
        else:
            bot.send_photo(photo=file.content, chat_id=message.chat.id)


@bot.message_handler(commands=['day'])
def day(message):
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(telebot.types.InlineKeyboardButton(text='Понедельник', callback_data='day_1'),
                 telebot.types.InlineKeyboardButton(text='Вторник', callback_data='day_2'),
                 telebot.types.InlineKeyboardButton(text='Среда', callback_data='day_3'),
                 telebot.types.InlineKeyboardButton(text='Четверг', callback_data='day_4'),
                 telebot.types.InlineKeyboardButton(text='Пятница', callback_data='day_5'),
                 telebot.types.InlineKeyboardButton(text='❌Закрыть', callback_data='delete'))
    bot.send_message(chat_id=message.chat.id, text='Выбери день', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == 'update':
        try:
            t = Timetable()
            text = t.day_to_string(day=datetime.now().weekday() + 1)
        except Exception as e:
            logging.error(msg=f'Timetable getting error: {e}')
            text = 'Произошла ошибка. Попробуй ещё раз через некоторое время.'
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(telebot.types.InlineKeyboardButton(text='🔄Обновить', callback_data='update'))
        keyboard.add(telebot.types.InlineKeyboardButton(text='❌Закрыть', callback_data='delete'))
        try:
            bot.edit_message_text(text=text, chat_id=call.message.chat.id, reply_markup=keyboard,
                                  message_id=call.message.id, parse_mode='HTML')
        except Exception as e:
            logging.warning(msg=f'Editing message error. It\'s ok: {e}')
        bot.answer_callback_query(callback_query_id=call.id)
    elif call.data == 'delete':
        bot.answer_callback_query(callback_query_id=call.id)
        bot.delete_message(call.message.chat.id, call.message.id)
    elif call.data == 'update_auto':
        if call.from_user.id == 326911795:
            upd(call=call, bot=bot, config=config)
        else:
            bot.answer_callback_query(callback_query_id=call.id, text='Ты не администратор')
    elif call.data == 'update_manual':
        if call.from_user.id == 326911795:
            global wait
            wait = True
            keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(telebot.types.InlineKeyboardButton(text='Отмена', callback_data='cancel_update'))
            bot.edit_message_text(text='Пришли файл xlsx файл с расписанием', chat_id=call.message.chat.id,
                                  message_id=call.message.id, reply_markup=keyboard)
        else:
            bot.answer_callback_query(callback_query_id=call.id, text='Ты не администратор')
    elif call.data == 'cancel_update':
        bot.edit_message_text(text='Отменено', chat_id=call.message.chat.id, message_id=call.message.id)
        wait = False
    elif call.data == 'back':
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(telebot.types.InlineKeyboardButton(text='Понедельник', callback_data='day_1'),
                     telebot.types.InlineKeyboardButton(text='Вторник', callback_data='day_2'),
                     telebot.types.InlineKeyboardButton(text='Среда', callback_data='day_3'),
                     telebot.types.InlineKeyboardButton(text='Четверг', callback_data='day_4'),
                     telebot.types.InlineKeyboardButton(text='Пятница', callback_data='day_5'),
                     telebot.types.InlineKeyboardButton(text='❌Закрыть', callback_data='delete'))
        bot.answer_callback_query(callback_query_id=call.id)
        bot.edit_message_text(chat_id=call.message.chat.id, text='Выбери день', reply_markup=keyboard,
                              message_id=call.message.id)
    elif 'day' in call.data:
        d = int(call.data[-1])
        try:
            t = Timetable()
            text = t.day_to_string(day=d, today=False)
        except Exception as e:
            logging.error(msg=f'Getting timetable error: {e}')
            text = 'Произошла ошибка. Попробуй ещё раз через некоторое время.'
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(telebot.types.InlineKeyboardButton(text='❌Закрыть', callback_data='delete'),
                     telebot.types.InlineKeyboardButton(text='↩Назад', callback_data='back'))
        bot.answer_callback_query(callback_query_id=call.id)
        bot.edit_message_text(chat_id=call.message.chat.id, text=text, reply_markup=keyboard, parse_mode='HTML',
                              message_id=call.message.id)


@bot.message_handler(commands=['tomorrow'])
def tomorrow(message):
    try:
        t = Timetable()
        text = t.day_to_string(day=(datetime.now().weekday() + 2) % 7, today=False)
    except Exception as e:
        logging.error(msg=f'Timetable getting error: {e}')
        text = 'Произошла ошибка. Попробуй ещё раз через некоторое время.'
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(telebot.types.InlineKeyboardButton(text='❌Закрыть', callback_data='delete'))
    bot.send_message(chat_id=message.chat.id, text=text, reply_markup=keyboard, parse_mode='HTML')


@bot.message_handler(commands=['update'])
def update(message):
    if message.from_user.id == 326911795:
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(telebot.types.InlineKeyboardButton(text='Автоматически', callback_data='update_auto'),
                     telebot.types.InlineKeyboardButton(text='Вручную', callback_data='update_manual'))
        bot.send_message(chat_id=message.chat.id, text='Выбери способ обновления', reply_markup=keyboard)
    else:
        bot.send_message(chat_id=message.chat.id, text='Обновлять расписание может только администратор')


if __name__ == '__main__':
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
