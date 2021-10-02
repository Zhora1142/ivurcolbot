from modules.improver import Improver
from modules.scanner import Scanner
from modules.handler import Handler
from modules.final_handler import FinalHandler
import yaml

with open('config.yml') as file:
    config = yaml.safe_load(file)

'''i = Improver(photo_url='http://www.ivurcol.net/raspisanie/22.jpg', **config['bigjpg'])
i.improve()
print('Improved')

s = Scanner(**config['OCR'])
s.scan()
print('scanned')'''

h = Handler()
h.move_table()
print('moved')

f = FinalHandler()
f.handle()
print('done')