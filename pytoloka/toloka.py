import aiohttp
from pytoloka.yandex import Yandex


class Toloka(Yandex):
    async def get_tasks(self) -> dict:
        async with aiohttp.ClientSession(headers=self._headers, cookie_jar=self._cookies) as session:
            response = await session.get('https://toloka.yandex.ru/api/i-v2/task-suite-pool-groups')
            json = await response.json()
            return json

    async def assign_task(self, pool_id, ref_uuid) -> dict:
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
            toloka_csrftoken = cookies.get('toloka-csrftoken')
            if toloka_csrftoken:
                self._headers['X-CSRF-Token'] = toloka_csrftoken.value
            return json
