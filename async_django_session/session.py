import hmac
import json
import logging
from base64 import b64decode, b64encode
from hashlib import sha1

from .utils import json_dumps, now_utc

log = logging.getLogger(__name__)


class Session(dict):
    def __init__(self, storage, key, secret, max_age):
        self.storage = storage
        self.key = key
        self.secret = secret
        self.max_age = max_age
        self.expire_date = None
        self._loaded = False
        self._value = None

    async def load(self):
        if not self._loaded:
            await self.reload()
        return self

    async def reload(self):
        log.debug("Load session from DB")
        self.clear()
        self._loaded = True
        self._value = None
        if not self.key:
            log.debug("It's a new session")
            return
        row = await self.storage.load(self.key)
        if not row:
            log.debug("Session not found in DB")
            return
        if row["expire_date"] < now_utc():
            log.debug("Session is expired")
            self.key = None
            return
        self._value = row["session_data"]
        self.expire_date = row["expire_date"]
        self._decode()
        return self

    async def save(self):
        if not self._loaded:
            log.debug("Skip saving of not loaded session")
            return False
        if not self.key and not self:
            log.debug("Skip saving of a new empty session")
            return False
        value = self._encode()
        if value == self._value:
            log.debug("Skip saving of unchanged session")
            return False
        log.debug("Saving session")
        self.expire_date = now_utc() + self.max_age
        self.key = await self.storage.save(self.key, value, self.expire_date)
        self._value = value
        return True

    def _decode(self):
        text = b64decode(self._value).decode("ascii")
        data = json.loads(text.split(":", 1)[1])
        self.update(**data)

    def _encode(self):
        dump = json_dumps(self)
        hash = (
            hmac.new(self.secret, msg=dump, digestmod=sha1)
            .hexdigest()
            .encode("ascii")
        )
        return b64encode(hash + b":" + dump).decode("ascii")
