import asyncio

import aiohttp

from utils import chunked

GET_ALL_ADS_URL = "https://advert-api.wildberries.ru/adv/v1/promotion/count"
GET_ADS_STATS_URL = "https://advert-api.wildberries.ru/adv/v2/fullstats"
GET_ADS_INFO_URL = "https://advert-api.wildberries.ru/adv/v1/promotion/adverts"


async def fetch_data(api_token: str, campaigns: list) -> list:
    headers = {"Authorization": api_token}
    result = []

    # TODO: пока что норм, но в будущем переделать. Тк сейчас мы обрабатываем только те компании, которые активны на момент получения данных. Но мы в системе обрабатываем данные за прошлые сутки, а компания вчера могла быть активной, а сегодня до получения данных ее остановили, и она не учитывается. Надо как то шарить данные по активным кампаниям за вчера
    campaigns_with_correct_status = []
    for i in campaigns:
        if int(i['status']) == 9:
            campaigns_with_correct_status.extend([i['advertId'] for i in i['advert_list']])

    async with aiohttp.ClientSession(headers=headers) as session:
        for batch in chunked(campaigns_with_correct_status, 50):
            async with session.post(GET_ADS_INFO_URL, json=batch) as response:
                data = await response.json()
                response.raise_for_status()
                result.extend(data)
            await asyncio.sleep(0.2)
        return result
