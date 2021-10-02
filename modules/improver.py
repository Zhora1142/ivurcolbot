import requests
import json


class Improver:
    def __init__(self, api):
        photo_url = 'http://www.ivurcol.net/raspisanie/22.jpg'
        self.url = 'https://bigjpg.com/api/task/'
        self.api = api
        self.data = {
            'style': 'photo',
            'noise': '0',
            'x2': '1',
            'input': photo_url
        }

    def improve(self):
        r = requests.post(
            url=self.url,
            headers={'X-API-KEY': self.api},
            data={'conf': json.dumps(self.data)}
        )

        if 'status' in r.json() and r.json()['status'] == 'exceed_limit':
            raise Exception('exceed_limit')

        task_id = r.json()['tid']

        amps = 0
        while 1:
            r = requests.get(self.url + task_id)

            status = r.json()[task_id]['status']
            if status == 'processing':
                continue
            elif status == 'success':
                photo = requests.get(r.json()[task_id]['url'])
                with open('files/file.jpg', 'wb') as file:
                    file.write(photo.content)
                    file.close()
                    break
            elif status == 'error':
                if amps >= 5:
                    raise Exception('Too many errors')
                requests.post(self.url + task_id)
                amps += 1
