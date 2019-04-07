from uuid import uuid4
from typing import Union


def generate_uuid():
    return str(uuid4())


class Session:

    def __init__(self, server_path: str, user_agent: Union[str, None] = None, proxy: Union[str, None] = None):
        self._server_path = server_path
        self._user_agent = user_agent
        self._proxy = proxy
        self.session_id = self._dial_browser()

    def _dial_browser(self):
        sess_id = generate_uuid()