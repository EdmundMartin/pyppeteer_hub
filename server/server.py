import asyncio
from typing import Any, List, Union, Dict

from aiohttp.web import Request
from aiohttp.web import json_response, Application, run_app

from browser import Response
from browser_manager.manager import BrowserManager


class WebApp:

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.browsers: Union[BrowserManager, None] = None

    async def get_page(self, request: Request):
        payload: Dict[str, Any] = await request.json()
        target: str = payload.pop('url')
        try:
            browser = await self.browsers.acquire()
            resp: Response = await browser.get_request(target, **payload)
        except Exception as e:
            return json_response({'message': str(e)}, status=400)
        else:
            return json_response(resp.resp_to_json())

    async def render_elements(self, request: Request):
        payload: Dict[str, Any] = await request.json()
        target, selector = payload.pop('url'), payload.pop('selector')
        try:
            browser = await self.browsers.acquire()
            resp: List[str] = await browser.render_elements(target, selector, **payload)
        except Exception as e:
            return json_response({'message': str(e)}, status=400)
        else:
            return json_response({'elements': resp})

    async def inject_script(self, request: Request):
        payload: Dict[str, Any] = await request.json()
        target, script = payload.pop('url'), payload.pop('script')
        try:
            browser = await self.browsers.acquire()
            resp = await browser.inject_script(target, script, **payload)
        except Exception as e:
            return json_response({'message': str(e)}, status=400)
        else:
            return json_response({'value': resp})

    async def create_app(self, browsers, max_cap):
        self.browsers = BrowserManager(browsers=browsers, max_capacity=max_cap)
        await self.browsers.create_browsers()
        app = Application()
        app.router.add_post('/get-request', self.get_page)
        app.router.add_post('/get-elements', self.render_elements)
        app.router.add_post('/inject-script', self.inject_script)
        return app

    def run_server(self, browsers=1, max_cap=10):
        loop = asyncio.get_event_loop()
        app = loop.run_until_complete(self.create_app(browsers, max_cap))
        run_app(app, host=self.host, port=self.port)


def run_server(host='0.0.0.0', port=800, browsers=1, max_cap=10):
    w = WebApp(host, port)
    w.run_server(browsers=browsers, max_cap=max_cap)
