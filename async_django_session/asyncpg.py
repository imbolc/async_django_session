from asyncpg.exceptions import UniqueViolationError

from .utils import new_session_key
from .base_backend import BaseBackend


class Backend(BaseBackend):
    def __init__(self, pool, *args, **kwargs):
        self.pool = pool
        super().__init__(*args, **kwargs)

    async def load(self, key):
        async with self.pool.acquire() as con:
            sql = "SELECT * FROM django_session WHERE session_key = $1"
            return await con.fetchrow(sql, key)

    async def save(self, key, value, expire_date):
        async with self.pool.acquire() as con:
            if key:
                return await self._update(con, key, value, expire_date)
            return await self._insert_new(con, value, expire_date)

    async def _insert_new(self, con, value, expire_date):
        sql = """
            INSERT INTO django_session (
                session_key,
                session_data,
                expire_date
            ) VALUES ($1, $2, $3)
        """
        while True:
            key = new_session_key()
            try:
                await con.execute(sql, key, value, expire_date)
            except UniqueViolationError:
                continue
            break
        return key

    async def _update(self, con, key, value, expire_date):
        sql = """
            UPDATE django_session
            SET session_data = $1, expire_date = $2
            WHERE session_key = $3
        """
        await con.execute(sql, value, expire_date, key)
        return key
