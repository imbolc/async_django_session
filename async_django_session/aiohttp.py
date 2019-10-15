from aiohttp import web


def middleware(storage, cookie_name="sessionid"):
    @web.middleware
    async def django_session(request, handler):
        key = request.cookies.get(cookie_name)
        session = storage.get_session(key)
        request.get_session = session.load
        response = await handler(request)
        if await session.save():
            response.set_cookie(cookie_name, session.key)
        return response

    return django_session
