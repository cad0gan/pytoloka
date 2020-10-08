import aiohttp
from yandex import Yandex


class Toloka(Yandex):
    async def request_tasks(self):
        async with aiohttp.ClientSession(headers=self._headers, cookie_jar=self._cookies) as session:
            response = await session.get('https://toloka.yandex.ru/api/i-v2/task-suite-pool-groups')
            json = await response.json()
            return json
