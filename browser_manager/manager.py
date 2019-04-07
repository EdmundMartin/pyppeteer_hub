import asyncio
from typing import List, Union, Dict

import async_timeout
from pyppeteer.page import Page

from browser import BrowserRender


class BrowserManager:

    def __init__(self, browsers: int = 1, max_capacity: int = 1):
        self._max_browsers = browsers
        self._max_capacity = max_capacity
        self._browsers: Union[List[BrowserRender], None] = None
        self._sessions: Dict[str, Page] = {}

    def register_session(self, uuid: str, browser_page: Page):
        if uuid in self._sessions:
            raise ValueError('A session with this UUID already exists')
        self._sessions[uuid] = browser_page

    async def create_browsers(self):
        browsers = []
        if self._browsers is None or len(self._browsers) == 0:
            for i in range(self._max_browsers):
                b = BrowserRender()
                browsers.append(b)
        self._browsers = browsers

    async def acquire(self, timeout=60):
        async with async_timeout.timeout(timeout):
            while True:
                for b in self._browsers:
                    if b.active_pages < self._max_capacity:
                        return b
                else:
                    await asyncio.sleep(0.15)

    def clean_browser(self, browser: BrowserRender):
        self._browsers.remove(browser)
        self._browsers.append(BrowserRender())
