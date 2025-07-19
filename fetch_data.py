import asyncio

import aiohttp

from utils import chunked

GET_ALL_ADS_URL = "https://advert-api.wildberries.ru/adv/v1/promotion/count"
GET_ADS_STATS_URL = "https://advert-api.wildberries.ru/adv/v2/fullstats"
GET_ADS_INFO_URL = "https://advert-api.wildberries.ru/adv/v1/promotion/adverts"


async def fetch_data(api_token: str, campaign_ids: list) -> list:
    headers = {"Authorization": api_token}
    result = []
    async with aiohttp.ClientSession(headers=headers) as session:
        for batch in chunked(campaign_ids, 50):
            async with session.post(GET_ADS_INFO_URL, json=batch) as response:
                data = await response.json()
                response.raise_for_status()
                result.extend(data)
            await asyncio.sleep(0.2)
        return result
