from modules.handler import Handler
from modules.improver import Improver
from modules.scanner import Scanner
from modules.final_handler import FinalHandler
import yaml
import os
import warnings

if not os.path.exists('files'):
    os.mkdir('files')

with open('config.yml') as stream:
    config = yaml.safe_load(stream)

print('Улучшение изображения...')
photo_url = 'http://www.ivurcol.net/raspisanie/22.jpg'
improver = Improver(photo_url=photo_url, api=config['bigjpg']['api'])
improver.improve()
if improver.errorMessage:
    print(f'Ошибка при улучшении изображения: {improver.errorMessage}')
    exit()

print('Сканирование изображения...')
scanner = Scanner(login=config['OCR']['login'], lic=config['OCR']['license'])
scanner.scan()
if scanner.errorMessage:
    print(f'Ошибка при сканировании изображения: {scanner.errorMessage}')
    exit()

print('Обработка таблицы...')
with warnings.catch_warnings(record=True):
    warnings.simplefilter("always")
    handler = Handler()
    handler.move_table()
    if handler.errorMessage:
        print(f'Ошибка при обработке таблицы: {handler.errorMessage}')
        exit()

print('Запись таблицы...')
final_handler = FinalHandler()
final_handler.handle()
if final_handler.errorMessage:
    print(f'Ошибка при загрузке таблицы: {final_handler.errorMessage}')

print('Done!')
