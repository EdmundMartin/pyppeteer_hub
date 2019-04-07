from browser_manager.manager import BrowserManager

from aiohttp.web import Request, json_response


async def new_session(request: Request):
    data = await request.json()
    session_id = data.get('sess_id')
    browser_manager: BrowserManager = request.app['browsers']
    renderer = await browser_manager.acquire()
    await renderer.check_browser_created()
    page = await renderer._browser.newPage()
    browser_manager.register_session(session_id, page)
    return json_response({'data': 'session created'},status=200)


def add_session_routes(app):
    app.router.add_post('/get-session', new_session)
    return app
