import asyncio
from typing import Union

from aiohttp.web import Application, run_app

from browser_manager.manager import BrowserManager
from server.requests import add_request_routes
from server.session import add_session_routes


class WebApp:

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.browsers: Union[BrowserManager, None] = None

    async def create_app(self, browsers, max_cap):
        browsers = BrowserManager(browsers=browsers, max_capacity=max_cap)
        await browsers.create_browsers()
        app = Application()
        app['browsers'] = browsers
        app = add_request_routes(app)
        app = add_session_routes(app)
        return app

    def run_server(self, browsers=1, max_cap=10):
        loop = asyncio.get_event_loop()
        app = loop.run_until_complete(self.create_app(browsers, max_cap))
        run_app(app, host=self.host, port=self.port)


def run_server(host='0.0.0.0', port=8000, browsers=1, max_cap=10):
    w = WebApp(host, port)
    w.run_server(browsers=browsers, max_cap=max_cap)
