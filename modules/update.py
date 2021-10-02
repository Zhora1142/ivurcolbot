from modules.handler import Handler
from modules.improver import Improver
from modules.scanner import Scanner
from modules.final_handler import FinalHandler
import logging

logging.basicConfig(filename='bot.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def upd(bot, config, auto=True, call=None):
    if auto:
        bot.edit_message_text(text='Улучшение скана расписания...', chat_id=call.message.chat.id,
                              message_id=call.message.id)
        try:
            i = Improver(**config['bigjpg'])
            i.improve()
        except Exception as e:
            logging.error(msg=f'Improver error: {e}')
            bot.edit_message_text(text=f'Ошибка улучшения скана: {e}', chat_id=call.message.chat.id,
                                  message_id=call.message.id)
        else:
            bot.edit_message_text(text='Сканирование расписания...', chat_id=call.message.chat.id,
                                  message_id=call.message.id)
            try:
                s = Scanner(**config['OCR'])
                s.scan()
            except Exception as e:
                logging.error(msg=f'Scanner error: {e}')
                bot.edit_message_text(text=f'Ошибка сканирования: {e}', chat_id=call.message.chat.id,
                                      message_id=call.message.id)
            else:
                bot.edit_message_text(text='Обработка расписания...', chat_id=call.message.chat.id,
                                      message_id=call.message.id)
                try:
                    h = Handler()
                    h.move_table()
                except Exception as e:
                    logging.error(msg=f'Handler error: {e}')
                    bot.edit_message_text(text=f'Ошибка обработки: {e}', chat_id=call.message.chat.id,
                                          message_id=call.message.id)
                else:
                    bot.edit_message_text(text=f'Сохранение...', chat_id=call.message.chat.id,
                                          message_id=call.message.id)
                    try:
                        f = FinalHandler()
                        f.handle()
                    except Exception as e:
                        logging.error(msg=f'FinalHandler error: {e}')
                        bot.edit_message_text(text=f'Ошибка сохранения: {e}', chat_id=call.message.chat.id,
                                              message_id=call.message.id)
                    else:
                        bot.edit_message_text(text='Расписание обновлено!', chat_id=call.message.chat.id,
                                              message_id=call.message.id)
    else:
        msg = bot.send_message(chat_id=call.chat.id, text='Сохранение расписания...')
        try:
            f = FinalHandler()
            f.handle()
        except Exception as e:
            logging.error(msg=f'FinalHandler error: {e}')
            bot.edit_message_text(text=f'Ошибка сохранения: {e}', chat_id=msg.chat.id,
                                  message_id=msg.id)
        else:
            bot.edit_message_text(text=f'Расписание обновлено!', chat_id=msg.chat.id,
                                  message_id=msg.id)
