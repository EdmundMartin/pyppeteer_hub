from browser_manager.manager import BrowserManager
from browser.page_methods import get


from aiohttp.web import Request, json_response


async def new_session(request: Request):
    data = await request.json()
    session_id = data.get('sess_id')
    browser_manager: BrowserManager = request.app['browsers']
    renderer = await browser_manager.acquire()
    await renderer.check_browser_created()
    page = await renderer._browser.newPage()
    browser_manager.register_session(session_id, page)
    return json_response({'data': 'session created'}, status=200)


async def get_page(request: Request):
    data = await request.json()
    session_id = request.match_info['session_id']
    browser_manager: BrowserManager = request.app['browsers']
    page = browser_manager.sessions.get(session_id)
    if not page:
        return json_response({'data': 'Session {} does not exist'.format(session_id)}, status=400)
    result = await get(page, data.get('url'), data.get('timeout'), data.get('post_load'))
    return json_response(result.resp_to_json(), status=200)


async def close_session(request: Request):
    session_id = request.match_info['session_id']
    browser_manager: BrowserManager = request.app['browsers']
    page = browser_manager.sessions.get(session_id)
    if not page:
        return json_response({'data': 'Session {} does not exist'.format(session_id)}, status=400)
    await page.close()
    browser_manager.sessions.pop(session_id)
    return json_response({'data': 'Closed session'}, status=200)


def add_session_routes(app):
    app.router.add_post('/get-session', new_session)
    app.router.add_post('/{session_id}/get', get_page)
    app.router.add_post('/{session_id}/close', close_session)
    return app
