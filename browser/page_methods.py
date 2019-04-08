from typing import Any
import asyncio

import async_timeout
from pyppeteer.page import Page

from browser.browser import Response


async def get(page: Page, url: str, timeout: int, post_load_wait: int = 0) -> Response:
    async with async_timeout.timeout(timeout):
        try:
            resp = await page.goto(url)
            if post_load_wait > 0:
                await asyncio.sleep(post_load_wait)
            page_content = await page.content()
        except Exception as e:
            raise e
        else:
            return Response(url, resp.url, page_content, resp.status, resp.headers)


async def inject(page: Page, script: str, timeout: int, force: bool=False) -> Any:
    async with async_timeout.timeout(timeout):
        try:
            result = await page.evaluate(script, force_expr=force)
        except Exception as e:
            raise e
        else:
            return result


async def page_source(page: Page, timeout: int) -> str:
    async with async_timeout.timeout(timeout):
        try:
            source = await page.content()
        except Exception as e:
            raise e
        else:
            return source