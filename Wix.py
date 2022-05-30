import requests


class Wix:
    def __init__(self):
        self.url = 'https://liaveliyahou2.wixsite.com/website-1/_functions'

    def send_to_db(self, data, path='event'):
        # send event to wix
        post_result = requests.post(f'{self.url}/{path}', json=data)
        return post_result

