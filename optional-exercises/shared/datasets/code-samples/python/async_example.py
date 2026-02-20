"""
Asynchronous programming examples using async/await.
Demonstrates concurrent operations and async patterns.
"""

import asyncio
import aiohttp
from typing import List, Dict


async def fetch_url(session, url):
    """Fetch a single URL asynchronously."""
    async with session.get(url) as response:
        return await response.text()


async def fetch_multiple_urls(urls: List[str]) -> List[str]:
    """Fetch multiple URLs concurrently."""
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
        return results


async def process_data_with_delay(data: Dict, delay: float):
    """Process data with simulated delay."""
    await asyncio.sleep(delay)
    return {k: v * 2 for k, v in data.items()}


async def main():
    """Main async function demonstrating concurrent operations."""
    # Simulate concurrent data processing
    tasks = [
        process_data_with_delay({"value": 10}, 1.0),
        process_data_with_delay({"value": 20}, 0.5),
        process_data_with_delay({"value": 30}, 0.2)
    ]

    results = await asyncio.gather(*tasks)
    return results


if __name__ == "__main__":
    asyncio.run(main())
