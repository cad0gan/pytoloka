import re
import uuid
import aiohttp


class Yandex:
    def __init__(self) -> None:
        self._headers: dict = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:81.0) Gecko/20100101 Firefox/81.0'
        }
        self._cookies: aiohttp.CookieJar = aiohttp.CookieJar()

    async def login(self, username: str, password: str) -> bool:
        async with aiohttp.ClientSession(headers=self._headers, cookie_jar=self._cookies) as session:
            try:
                # get initial cookies
                response = await session.get(
                    'https://passport.yandex.ru/passport?origin=toloka&mode=auth&retpath=https://toloka.yandex.ru/',
                )
                body = await response.text()
                match = re.search(r'csrf_token.+value="([\w|:]+)"', body)
                if not match:
                    return False
                csrf_token = match.group(1)

                # start
                response = await session.post(
                    'https://passport.yandex.ru/registration-validations/auth/multi_step/start',
                    data={
                        'csrf_token': csrf_token,
                        'login': username,
                        'process_uuid': str(uuid.uuid4()),
                        'retpath': 'https://toloka.yandex.ru/',
                        'origin': 'toloka',
                    }
                )
                json = await response.json()
                if json['status'] != 'ok':
                    return False
                track_id = json['track_id']

                response = await session.post(
                    'https://passport.yandex.ru/registration-validations/auth/multi_step/commit_password',
                    data={
                        'csrf_token': csrf_token,
                        'track_id': track_id,
                        'password': password,
                        'retpath': 'https://toloka.yandex.ru/',
                    }
                )
                json = await response.json()
                if json['status'] != 'ok':
                    return False

                self._cookies = session.cookie_jar
                cookies = self._cookies.filter_cookies('https://passport.yandex.ru')

                return True

            except (ConnectionError, KeyError):
                return False
