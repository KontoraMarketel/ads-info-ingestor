import asyncio
import logging

import aiohttp

from utils import chunked

GET_ALL_ADS_URL = "https://advert-api.wildberries.ru/adv/v1/promotion/count"
GET_ADS_STATS_URL = "https://advert-api.wildberries.ru/adv/v2/fullstats"
GET_ADS_INFO_URL = "https://advert-api.wildberries.ru/adv/v1/promotion/adverts"


async def fetch_data(api_token: str, campaigns: list) -> list:
    headers = {"Authorization": api_token}
    result = []
    campaigns_list = campaigns['data']

    # TODO: пока что норм, но в будущем переделать. Тк сейчас мы обрабатываем только те компании, которые активны на момент получения данных. Но мы в системе обрабатываем данные за прошлые сутки, а компания вчера могла быть активной, а сегодня до получения данных ее остановили, и она не учитывается. Надо как то шарить данные по активным кампаниям за вчера
    campaigns_with_correct_status = []
    for i in campaigns_list:
        if i['status'] == 9:
            campaigns_with_correct_status.extend([i['advertId'] for i in i['advert_list']])

    async with aiohttp.ClientSession(headers=headers) as session:
        for batch in chunked(campaigns_with_correct_status, 50):
            data = await fetch_page_with_retry(session, GET_ADS_INFO_URL, batch)
            result.extend(data)
        await asyncio.sleep(0.2)
        return result


async def fetch_page_with_retry(session, url, payload):
    while True:
        async with session.post(url, json=payload) as response:
            if response.status == 429:
                retry_after = int(response.headers.get('X-Ratelimit-Retry', 10))
                logging.warning(f"Rate limited (429). Retrying after {retry_after} seconds...")
                await asyncio.sleep(retry_after)
                continue

            response.raise_for_status()
            return await response.json()
