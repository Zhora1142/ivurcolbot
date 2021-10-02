from modules.msql_collector import MysqlCollector
import yaml
from json import loads
from datetime import datetime, time

with open('config.yml') as stream:
    config = yaml.safe_load(stream)['sql']


class Timetable:
    def __init__(self):
        self.collector = MysqlCollector(**config, db='ivurcol')
        self.errorMessage = None
        self.now = datetime.now().time()
        self.time = {1: {'begin': time(hour=9, minute=00), 'end': time(hour=10, minute=20)},
                     2: {'begin': time(hour=10, minute=30), 'end': time(hour=11, minute=50)},
                     3: {'begin': time(hour=12, minute=20), 'end': time(hour=13, minute=40)},
                     4: {'begin': time(hour=13, minute=50), 'end': time(hour=15, minute=10)},
                     5: {'begin': time(hour=15, minute=20), 'end': time(hour=16, minute=40)},
                     6: {'begin': time(hour=17, minute=50), 'end': time(hour=18, minute=10)}}
        self.smiles = {1: '1️⃣', 2: '2️⃣', 3: '3️⃣', 4: '4️⃣', 5: '5️⃣', 6: '6️⃣'}

    def get_day(self, day):
        if 0 < day < 6:
            result = self.collector.select(table='timetable',
                                           cols=['couple_1', 'couple_2', 'couple_3',
                                                 'couple_4', 'couple_5', 'couple_6'],
                                           where=f'day={day}')

            data = result['data']

            if not result['status']:
                raise Exception(data)

            flag = False
            remove = []
            for k, v in data.items():
                data[k] = loads(v)
                if data[k]['name'] and not flag:
                    flag = True
                if data[k]['name'] is None and flag:
                    remove.append(k)

            for key in remove:
                data.pop(key)

            result = list(data.values())
            weekend = True
            for v in result:
                if v['name']:
                    weekend = False
                    break

            if weekend:
                return None

            return list(data.values())
        else:
            return None

    def get_next_couple(self, first, last):
        couple = None
        for k, v in self.time.items():
            if k > first and v['begin'] > self.now:
                couple = k
                break
            if k == last:
                break

        return couple

    def get_couple_status(self, couple):
        info = self.time[couple]

        if info['begin'] <= self.now < info['end']:
            status = 'now'
        elif self.now >= info['end']:
            status = 'end'
        else:
            status = 'next'

        return status

    def get_time_string(self, couple):
        begin = f'{self.time[couple]["begin"].strftime("%H:%M")}'
        end = f'{self.time[couple]["end"].strftime("%H:%M")}'
        return {'begin': begin, 'end': end}

    def get_day_limits(self, day):
        d = self.get_day(day)

        first = None
        last = len(d)
        couple = 1
        for i in d:
            if i['name']:
                first = couple
                break
            couple += 1

        return first, last

    def get_current_status(self, day):
        response = {'status': None, 'couple': None}
        first, last = self.get_day_limits(day)

        if self.now < self.time[first]['begin']:
            response['status'] = 'not_started'
        elif self.now >= self.time[last]['end']:
            response['status'] = 'finished'
        else:
            current = None
            next_couple = None
            for couple in range(first, last + 1):
                status = self.get_couple_status(couple)
                if status == 'now':
                    current = couple
                elif status == 'next':
                    next_couple = couple

            if current:
                response['status'] = 'couple'
                response['couple'] = current
            elif next_couple:
                response['status'] = 'break'
                response['couple'] = next_couple

        return response

    def get_info_block(self, day, today=True):
        first, last = self.get_day_limits(day)

        data = self.get_current_status(day)
        string = ''
        if today:
            if data['status'] == 'not_started':
                string += '\n🕘Пары ещё не начались\n'
            elif data['status'] == 'finished':
                string += '\n🤤На сегодня пары закончились\n/tomorrow\n'
            elif data['status'] == 'couple':
                string += f'\n📖Текущая пара закончится в <b>{self.get_time_string(data["couple"])["end"]}</b>\n'
            elif data['status'] == 'break':
                string += f'\n🚬Следующая пара начнётся в <b>{self.get_time_string(data["couple"])["begin"]}</b>\n'

        string += f'\n<b>{self.get_time_string(first)["begin"]}</b> - <b>{self.get_time_string(last)["end"]}</b>'

        return string

    def day_to_string(self, day, today=True):
        data = self.get_day(day)

        if data:
            string = ''

            n = 1
            for couple in data:
                if couple['name']:
                    s = f'{self.smiles[n]} {couple["name"]} - {couple["type"]} - {couple["room"]} - {couple["tutor"]}'
                else:
                    s = f'{self.smiles[n]} Нет пары'
                if today:
                    status = self.get_couple_status(n)
                    if status == 'now':
                        s = f'<b>{s}</b>\n'
                    elif status == 'end':
                        s = f'<s>{s}</s>\n'
                    else:
                        s += '\n'
                else:
                    s += '\n'
                n += 1
                string += s

            string += self.get_info_block(day, today)

            return string

        else:
            return 'В этот день выходной, отдыхай и набирайся сил 🤤'
