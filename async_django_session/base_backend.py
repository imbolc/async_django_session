from datetime import timedelta
from hashlib import sha1

from .session import Session


class BaseBackend:
    def __init__(
        self,
        secret,
        *,
        max_age=timedelta(days=14),
        salt="django.contrib.sessionsSessionStore"
    ):
        self.secret = sha1((salt + secret).encode("ascii")).digest()
        self.max_age = max_age

    def get_session(self, key):
        return Session(self, key, self.secret, self.max_age)
