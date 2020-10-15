import asyncio
import aiohttp
from datetime import datetime
from pytoloka.yandex import Yandex
from pytoloka.exceptions import HttpError


class Toloka(Yandex):
    __max_errors = 3

    async def get_tasks(self) -> list:
        result: list = list()
        try:
            async with aiohttp.ClientSession(
                    timeout=self._timeout, headers=self._headers, cookie_jar=self._cookie
            ) as session:
                response = await session.get('https://toloka.yandex.ru/api/i-v2/task-suite-pool-groups')
                result = await response.json()
        except (asyncio.TimeoutError, aiohttp.ClientConnectionError, aiohttp.ClientPayloadError):
            raise HttpError
        return result

    async def get_skills(self) -> list:
        result: list = list()
        try:
            async with aiohttp.ClientSession(
                timeout=self._timeout, headers=self._headers, cookie_jar=self._cookie
            ) as session:
                response = await session.get('https://toloka.yandex.ru/api/users/current/worker/skills')
                json = await response.json()
                result = json.get('content', [])
        except (asyncio.TimeoutError, aiohttp.ClientConnectionError, aiohttp.ClientPayloadError):
            raise HttpError
        return result

    async def get_transactions(self) -> list:
        result: list = list()
        url: str = 'https://toloka.yandex.ru/api/users/current/worker/transactions?properties=startDate&direction=DESC'
        page: int = 0
        errors: int = 0
        while True:
            try:
                async with aiohttp.ClientSession(
                    timeout=self._timeout, headers=self._headers, cookie_jar=self._cookie
                ) as session:
                    response = await session.get(
                        url + f'&page={page}&size=20'
                    )
                    json = await response.json()
                    content = json.get('content', [])
                    for value in content:
                        value['startDate'] = datetime.strptime(value['startDate'], '%Y-%m-%dT%H:%M:%S.%f')
                        if 'endDate' in value:
                            value['endDate'] = datetime.strptime(value['endDate'], '%Y-%m-%dT%H:%M:%S.%f')
                    result += content
                    if json['last']:
                        break
                    else:
                        page += 1
                        errors = 0
            except (asyncio.TimeoutError, aiohttp.ClientConnectionError, aiohttp.ClientPayloadError):
                errors += 1
                if errors >= self.__max_errors:
                    raise HttpError
        return result

    async def assign_task(self, pool_id, ref_uuid) -> dict:
        result = dict()
        try:
            async with aiohttp.ClientSession(
                    timeout=self._timeout, headers=self._headers, cookie_jar=self._cookie
            ) as session:
                response = await session.get('https://toloka.yandex.ru/task/{}?refUuid={}'.format(pool_id, ref_uuid))
                await response.text()

                response = await session.post(
                    'https://toloka.yandex.ru/api/assignments',
                    json={
                        'refUuid': ref_uuid,
                        'poolId': pool_id,
                    }
                )
                result = await response.json()
                cookie = self._cookie.filter_cookies('https://toloka.yandex.ru')
                toloka_csrftoken = cookie.get('toloka-csrftoken')
                if toloka_csrftoken:
                    self._headers['X-CSRF-Token'] = toloka_csrftoken.value
        except (asyncio.TimeoutError, aiohttp.ClientConnectionError, aiohttp.ClientPayloadError):
            raise HttpError
        return result
