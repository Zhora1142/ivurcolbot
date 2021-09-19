from modules.msql_collector import MysqlCollector
import yaml
from json import loads

with open('config.yml') as stream:
    config = yaml.safe_load(stream)['sql']


class Timetable:
    def __init__(self):
        self.collector = MysqlCollector(**config, db='ivurcol')
        self.errorMessage = None

    def get_day(self, day):
        try:
            result = self.collector.select(table='timetable', where=f'day={day}')

            if not result['status']:
                self.errorMessage = result['data']
                return None

            for k, v in result['data'].items():
                if type(v) == str:
                    result['data'][k] = loads(v)

            return result['data']
        except Exception as e:
            self.errorMessage = e
            return None

    def day_to_string(self, day):
        data = self.get_day(day)
        string = ''

        if not self.errorMessage:
            for couple in range(1, 7):
                if data[f'couple_{couple}']['name']:
                    string += f'{couple} - {data[f"couple_{couple}"]["name"]} - {data[f"couple_{couple}"]["type"]} - ' \
                              f'{data[f"couple_{couple}"]["room"]} - {data[f"couple_{couple}"]["tutor"]}\n'
                else:
                    string += f'{couple} - Нет пары\n'

            raw = string.splitlines()
            raw.reverse()
            remove_values = []

            for v in raw:
                if 'Нет пары' in v:
                    remove_values.append(v)
                else:
                    raw.reverse()
                    break

            for v in remove_values:
                raw.remove(v)

            response = ''.join(f'{item}\n' for item in raw)
            return response
        else:
            return None
