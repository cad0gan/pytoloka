import re
import uuid
import asyncio
import aiohttp
from pytoloka.exceptions import HttpError


class Yandex:
    def __init__(self) -> None:
        self._timeout: aiohttp.ClientTimeout = aiohttp.ClientTimeout(total=5)
        self._headers: dict = {
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:81.0) Gecko/20100101 Firefox/81.0'
        }
        self._cookie: aiohttp.CookieJar = aiohttp.CookieJar()

    async def login(self, username: str, password: str) -> bool:
        async with aiohttp.ClientSession(
                timeout=self._timeout, headers=self._headers, cookie_jar=self._cookie
        ) as session:
            try:
                # get initial cookies
                response = await session.get(
                    'https://passport.yandex.ru/passport?origin=toloka&mode=auth&retpath=https://toloka.yandex.ru/',
                )
                body: str = await response.text()
                match = re.search(r'csrf_token.+value="([\w|:]+)"', body)
                if not match:
                    return False
                csrf_token: str = match.group(1)

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
                json: dict = await response.json()
                if json['status'] != 'ok':
                    return False
                track_id: str = json['track_id']

                response = await session.post(
                    'https://passport.yandex.ru/registration-validations/auth/multi_step/commit_password',
                    data={
                        'csrf_token': csrf_token,
                        'track_id': track_id,
                        'password': password,
                        'retpath': 'https://toloka.yandex.ru/',
                    }
                )
                json: dict = await response.json()
                if json['status'] != 'ok':
                    return False
                self._cookie = session.cookie_jar
                return True

            except (
                    asyncio.TimeoutError,
                    aiohttp.ClientConnectionError, aiohttp.ClientPayloadError, aiohttp.ContentTypeError
            ):
                raise HttpError
            except KeyError:
                return False
