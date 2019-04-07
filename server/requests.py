from typing import Any, Dict, List

from aiohttp.web import Request, json_response

from browser.browser import Response


async def get_page(request: Request):
    payload: Dict[str, Any] = await request.json()
    target: str = payload.pop('url')
    try:
        browser = await request.app['browsers'].acquire()
        resp: Response = await browser.get_request(target, **payload)
    except Exception as e:
        return json_response({'message': str(e)}, status=400)
    else:
        return json_response(resp.resp_to_json())


async def render_elements(request: Request):
    payload: Dict[str, Any] = await request.json()
    target, selector = payload.pop('url'), payload.pop('selector')
    try:
        browser = await request.app['browsers'].acquire()
        resp: List[str] = await browser.render_elements(target, selector, **payload)
    except Exception as e:
        return json_response({'message': str(e)}, status=400)
    else:
        return json_response({'elements': resp})


async def inject_script(request: Request):
    payload: Dict[str, Any] = await request.json()
    target, script = payload.pop('url'), payload.pop('script')
    try:
        browser = await request.app['browsers'].acquire()
        resp = await browser.inject_script(target, script, **payload)
    except Exception as e:
        return json_response({'message': str(e)}, status=400)
    else:
        return json_response({'value': resp})


def add_request_routes(app):
    app.router.add_post('/get-request', get_page)
    app.router.add_post('/get-elements', render_elements)
    app.router.add_post('/inject-script', inject_script)
    return app