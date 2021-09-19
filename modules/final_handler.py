from openpyxl import load_workbook
from modules.msql_collector import MysqlCollector
import yaml
from json import dumps
from os import remove

with open('config.yml') as stream:
    config = yaml.safe_load(stream)['sql']


class FinalHandler:
    def __init__(self):
        self.wb = load_workbook('files/result.xlsx')
        self.collector = MysqlCollector(**config, db='ivurcol')
        self.errorMessage = None

    def handle(self):
        try:
            sheet = self.wb.active
            self.collector.update(table='timetable', values={'name': None, 'room': None, 'tutor': None}, where='day=1')

            day, couple = 1, 1
            for row in range(1, sheet.max_row + 1):
                if sheet.cell(row=row, column=1).value:
                    if sheet.cell(row=row, column=2):
                        data = {
                            'name': sheet.cell(row=row, column=2).value,
                            'type': sheet.cell(row=row, column=3).value,
                            'room': sheet.cell(row=row, column=4).value,
                            'tutor': sheet.cell(row=row, column=5).value
                        }

                        result = self.collector.update(table='timetable',
                                                       values={f'couple_{couple}': dumps(data, ensure_ascii=False)},
                                                       where=f'day={day}')
                        if not result['status']:
                            self.errorMessage = result['data']
                            break
                        couple += 1
                else:
                    couple = 1
                    day += 1
        except Exception as e:
            self.errorMessage = e

        remove('files/result.xlsx')
