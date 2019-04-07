import asyncio
from typing import Union

import async_timeout
from pyppeteer import launch
from pyppeteer.browser import Browser
from pyppeteer.errors import PageError


class PageException(Exception):
    pass


class TimeoutException(Exception):
    pass


class RequestException(Exception):
    pass


class Response:

    __slots__ = ['url', 'requested_url', 'html', 'status', 'headers']

    def __init__(self, requested_url: str, url: str, html: str, status_code: int, headers: dict):
        self.url = url
        self.requested_url = requested_url
        self.html = html
        self.status = status_code
        self.headers = headers

    @property
    def status_ok(self) -> bool:
        return self.status < 300

    @property
    def is_redirect(self) -> bool:
        return self.requested_url != self.url

    def raise_for_status(self) -> None:
        if self.status >= 400:
            raise RequestException("Did not receive a 2XX Code")

    def resp_to_json(self):
        return {'url': self.url, 'requested_url': self.requested_url, 'html': self.html, 'status_code': self.status}

    def __repr__(self):
        return 'Response(url={}, status_code={})'.format(self.url, self.status)


class BrowserRender:

    def __init__(self, headless=False, loop=None, proxy=None, auth=None):
        self.loop = loop if loop else asyncio.get_event_loop()
        self._headless = headless
        self._proxy = proxy
        self._auth = auth
        self._browser: Union[None, Browser] = None
        self._page_queue = asyncio.Queue()
        self._semaphore = asyncio.BoundedSemaphore(1)
        self.active_pages = 0

    async def _create_browser(self) -> None:
        if self._proxy:
            self._browser = await launch(headless=self._headless,  args=['--proxy-server={}'.format(self._proxy)])
        else:
            self._browser = await launch(headless=self._headless)

    async def check_browser_created(self):
        async with self._semaphore:
            if self._browser is None:
                await self._create_browser()

    async def inject_script(self, url: str, script: str, **kwargs):
        await self.check_browser_created()
        page_retrieved = False
        page = await self._browser.newPage()
        async with async_timeout.timeout(kwargs.get('timeout', 15)):
            try:
                page_retrieved = True
                self.active_pages += 1
                await page.goto(url)
                post_load = kwargs.get('post_load_wait', None)
                if post_load:
                    await asyncio.sleep(post_load)
                value = await page.evaluate(script, force_expr=kwargs.get('force', False))
            except PageError:
                raise PageException('Page threw an exception when navigating to URL')
            except Exception as e:
                raise e
            else:
                return value
            finally:
                if page_retrieved:
                    self.active_pages -= 1
                    await page.close()

    async def render_elements(self, url: str, selector: str, method: str = 'outerHTML', **kwargs):
        await self.check_browser_created()
        page_retrieved = False
        found_elements = []
        page = await self._browser.newPage()
        async with async_timeout.timeout(kwargs.get('timeout', 15)):
            try:
                page_retrieved = True
                self.active_pages += 1
                await page.goto(url)
                post_load = kwargs.get('post_load_wait', None)
                if post_load:
                    await asyncio.sleep(post_load)
                elements = await page.querySelectorAll(selector)
                for el in elements:
                    element = await page.evaluate('(el) => el.{}'.format(method), el)
                    found_elements.append(element)
            except PageError:
                raise PageException('Page threw an exception when navigating to URL')
            except Exception as e:
                raise e
            else:
                return found_elements
            finally:
                if page_retrieved:
                    self.active_pages -= 1
                    await page.close()

    async def get_request(self, url: str, timeout: int = 15, post_load_wait: int = 0) -> Response:
        await self.check_browser_created()
        page_retrieved = False
        page = await self._browser.newPage()
        async with async_timeout.timeout(timeout):
            try:
                page_retrieved = True
                self.active_pages += 1
                response = await page.goto(url)
                if post_load_wait > 0:
                    await asyncio.sleep(post_load_wait)
                page_content = await page.content()
            except TimeoutError:
                raise TimeoutException("Request took longer than timeout: {}".format(timeout))
            except PageError:
                raise PageException('Page threw an exception when navigating to URL')
            except Exception:
                raise PageException('Page threw an exception when navigating to URL')
            else:
                return Response(url, response.url, page_content, response.status, response.headers)
            finally:
                if page_retrieved:
                    self.active_pages -= 1
                    await page.close()

    async def close(self):
        if self._browser:
            await self._browser.close()