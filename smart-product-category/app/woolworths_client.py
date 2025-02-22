import aiohttp
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class WoolworthsClient:
    BASE_URL = "https://www.woolworths.com.au/apis/ui/product/detail"
    
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.woolworths.com.au/shop/productdetails/",
        "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "wp-correlation-id": "default",
        "x-masked-address": "null",
        "x-user-id": "anonymous"
    }

    async def _get_session_cookies(self) -> Dict[str, str]:
        """First visit the main site to get required cookies"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://www.woolworths.com.au/shop/productdetails/", 
                headers=self.HEADERS
            ) as response:
                cookies = response.cookies
                return {cookie.key: cookie.value for cookie in cookies.values()}

    async def get_product_details(self, product_id: str) -> Dict[str, Any]:
        """Fetch product details from Woolworths API"""
        url = f"{self.BASE_URL}/{product_id}/"
        logger.info(f"Fetching product details from: {url}")
        
        # First get session cookies
        cookies = await self._get_session_cookies()
        
        async with aiohttp.ClientSession(cookies=cookies) as session:
            try:
                async with session.get(url, headers=self.HEADERS, ssl=True) as response:
                    logger.debug(f"Response status: {response.status}")
                    logger.debug(f"Response headers: {dict(response.headers)}")
                    
                    if response.status == 403:
                        logger.error("Access forbidden - might need to update headers or cookies")
                        raise Exception("Access forbidden by Woolworths API")
                    
                    if response.status != 200:
                        text = await response.text()
                        logger.error(f"Error response: {text}")
                        raise Exception(f"Woolworths API returned status {response.status}")
                    
                    try:
                        data = await response.json()
                        logger.info(f"Successfully fetched data for product ID: {product_id}")
                        return data
                    except Exception as je:
                        text = await response.text()
                        logger.error(f"JSON parsing error: {str(je)}\nResponse text: {text[:200]}...")
                        raise Exception(f"Failed to parse response as JSON: {str(je)}")
                    
            except aiohttp.ClientError as e:
                logger.error(f"Network error: {str(e)}")
                raise Exception(f"Failed to fetch product details: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                raise