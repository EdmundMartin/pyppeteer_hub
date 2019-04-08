from uuid import uuid4
from typing import Any, Union
from urllib.parse import urljoin

import requests


DEFAULT_AGENT = {'Linux': '', 'Windows': '', 'Apple': ''}


class SessionException(Exception):
    pass


def generate_uuid():
    return str(uuid4())


class Session:

    def __init__(self, server_path: str, user_agent: Union[str, None]=None,
                 proxy: Union[str, None]=None, timeout: int=30):
        self._server_path = server_path
        self._user_agent = user_agent
        self._proxy = proxy
        self._timeout = timeout
        self.session_id = self._dial_browser()

    def _dial_browser(self):
        sess_id = generate_uuid()
        target_url = urljoin(self._server_path, '/get-session')
        requests.post(target_url, json={'sess_id': sess_id}, timeout=self._timeout)
        return sess_id

    def get(self, url: str, post_load_wait: int = 0):
        target_url = urljoin(self._server_path, '/{}/get'.format(self.session_id))
        resp = requests.post(target_url, json={'url': url, 'timeout': self._timeout,
                                               'post_load': post_load_wait}, timeout=self._timeout)
        if resp.status_code > 200:
            raise SessionException(resp.json().get('data'))
        return resp.json()

    async def evaluate_script(self, script: str) -> Any:
        pass

    async def current_url(self) -> str:
        pass

    async def page_source(self):
        target_url = urljoin(self._server_path, '/{}/page-source')
        resp = requests.post(target_url, json={'timeout': self._timeout})
        if resp.status_code > 200:
            raise SessionException(resp.json().get('data'))
        source = resp.json()
        return source['data']

    def close(self):
        target_url = urljoin(self._server_path, '/{}/close'.format(self.session_id))
        resp = requests.post(target_url)
        if resp.status_code > 200:
            raise SessionException(resp.json().get('data'))
        return resp.json()


if __name__ == '__main__':
    sess = Session('http://localhost:8000')
    res = sess.get('http://edmundmartin.com', post_load_wait=5)
    res = sess.close()