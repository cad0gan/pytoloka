import aiohttp
from pytoloka.yandex import Yandex


class Toloka(Yandex):
    async def request_tasks(self):
        async with aiohttp.ClientSession(headers=self._headers, cookie_jar=self._cookies) as session:
            response = await session.get('https://toloka.yandex.ru/api/i-v2/task-suite-pool-groups')
            json = await response.json()
            return json

    async def assign_task(self, pool_id, ref_uuid):
        async with aiohttp.ClientSession(headers=self._headers, cookie_jar=self._cookies) as session:
            response = await session.get('https://toloka.yandex.ru/task/{}?refUuid={}'.format(pool_id, ref_uuid))
            json = await response.text()

            response = await session.post(
                'https://toloka.yandex.ru/api/assignments',
                json={
                    'refUuid': ref_uuid,
                    'poolId': pool_id,
                }
            )
            json = await response.json()
            cookies = self._cookies.filter_cookies('https://toloka.yandex.ru')
            for name, value in cookies.items():
                if name == 'toloka-csrftoken':
                    self._headers['X-CSRF-Token'] = value.value
            return json
