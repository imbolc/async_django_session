def middleware(app, backend, cookie_name="sessionid"):
    @app.middleware("http")
    async def django_session(request, call_next):
        key = request.cookies.get(cookie_name)
        session = backend.get_session(key)
        request.state.get_session = session.load
        response = await call_next(request)
        if await session.save():
            response.set_cookie(
                cookie_name, session.key, expires=session.expire_date
            )
        return response
