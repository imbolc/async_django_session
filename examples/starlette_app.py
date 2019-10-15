import sys

sys.path.insert(0, "..")  # noqa

from starlette.applications import Starlette
from starlette.responses import JSONResponse
import async_django_session.asyncpg
import async_django_session.starlette
import asyncpg
import uvicorn

import cfg


app = Starlette()
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


@app.route("/")
async def index(request):
    session = await request.state.get_session()
    framework = "starlette"
    session[framework] = session.get(framework, 0) + 1
    return JSONResponse({"framework": framework, "session": session})


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=cfg.PORT, debug=cfg.DEBUG)
