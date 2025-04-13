import aiohttp
import logging
import backoff
from typing import Dict, Any, Optional
from aiohttp import ClientSession, ClientError, ClientTimeout

logger = logging.getLogger(__name__)

class WoolworthsClient:
    """Client for interacting with the Woolworths product API."""
    
    BASE_URL = "https://www.woolworths.com.au/apis/ui/product/detail"
    
    # Default timeout values (in seconds)
    DEFAULT_TIMEOUT = ClientTimeout(total=30, connect=10, sock_read=30)
    
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

    def __init__(self, timeout: Optional[ClientTimeout] = None):
        """Initialize the Woolworths client.
        
        Args:
            timeout: Optional custom timeout for API requests
        """
        self.timeout = timeout or self.DEFAULT_TIMEOUT

    @backoff.on_exception(
        backoff.expo, 
        (ClientError, TimeoutError),
        max_tries=3,
        giveup=lambda e: isinstance(e, aiohttp.ClientResponseError) and e.status >= 400 and e.status != 429
    )
    async def _get_session_cookies(self) -> Dict[str, str]:
        """First visit the main site to get required cookies.
        
        Returns:
            Dictionary of cookies needed for API requests
        
        Raises:
            Exception: If unable to retrieve cookies after retries
        """
        async with ClientSession(timeout=self.timeout) as session:
            try:
                async with session.get(
                    "https://www.woolworths.com.au/shop/productdetails/", 
                    headers=self.HEADERS
                ) as response:
                    response.raise_for_status()
                    cookies = response.cookies
                    return {cookie.key: cookie.value for cookie in cookies.values()}
            except ClientError as e:
                logger.error(f"Error retrieving session cookies: {str(e)}")
                raise

    @backoff.on_exception(
        backoff.expo, 
        (ClientError, TimeoutError),
        max_tries=3,
        giveup=lambda e: isinstance(e, aiohttp.ClientResponseError) and e.status >= 400 and e.status != 429
    )
    async def get_product_details(self, product_id: str) -> Dict[str, Any]:
        """Fetch product details from Woolworths API.
        
        Args:
            product_id: The ID of the product to fetch
        
        Returns:
            Dictionary containing product details
        
        Raises:
            Exception: If the API request fails after retries
        """
        url = f"{self.BASE_URL}/{product_id}/"
        logger.info(f"Fetching product details for ID: {product_id}")
        
        # First get session cookies
        try:
            cookies = await self._get_session_cookies()
        except Exception as e:
            logger.error(f"Failed to get session cookies: {str(e)}")
            raise
        
        async with ClientSession(cookies=cookies, timeout=self.timeout) as session:
            try:
                async with session.get(url, headers=self.HEADERS, ssl=True) as response:
                    if response.status == 403:
                        logger.error("Access forbidden - might need to update headers or cookies")
                        raise ValueError("Access forbidden by Woolworths API")
                    
                    if response.status == 404:
                        logger.warning(f"Product not found: {product_id}")
                        raise ValueError(f"Product ID {product_id} not found")
                    
                    response.raise_for_status()
                    
                    try:
                        data = await response.json()
                        logger.info(f"Successfully fetched data for product ID: {product_id}")
                        return data
                    except Exception as je:
                        text = await response.text()
                        logger.error(f"JSON parsing error: {str(je)}\nResponse text: {text[:200]}...")
                        raise ValueError(f"Failed to parse response as JSON: {str(je)}")
                    
            except ClientError as e:
                logger.error(f"Network error fetching product {product_id}: {str(e)}")
                raise ValueError(f"Failed to fetch product details: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error fetching product {product_id}: {str(e)}")
                raise