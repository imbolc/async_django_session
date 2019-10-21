from starlette.requests import Request


async def get_session(request: Request):
    return await request.state.get_session()
