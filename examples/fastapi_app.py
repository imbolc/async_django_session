import sys

sys.path.insert(0, "..")  # noqa

from async_django_session.fastapi import get_session
from async_django_session.session import Session
from fastapi import Depends, FastAPI
import async_django_session.asyncpg
import async_django_session.starlette
import asyncpg
import uvicorn

import cfg


app = FastAPI()
app.debug = True


class DB:
    async def connect(self):
        global acquire
        self.pool = await asyncpg.create_pool(cfg.DB_URI)
        self.acquire = self.pool.acquire


db = DB()


@app.on_event("startup")
async def startup():
    await db.connect()


@app.on_event("shutdown")
async def shutdown():
    await db.pool.release()


async_django_session.starlette.middleware(
    app, async_django_session.asyncpg.Backend(db, cfg.SECRET_KEY)
)


@app.get("/")
async def index(session: Session = Depends(get_session)):
    framework = "fastapi"
    session[framework] = session.get(framework, 0) + 1
    return {"framework": framework, "session": session}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=cfg.PORT, debug=cfg.DEBUG)
