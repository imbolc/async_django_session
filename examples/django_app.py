from django.conf import settings
from django.http import JsonResponse
from django.urls import path

import cfg

settings.configure(
    DEBUG=cfg.DEBUG,
    SECRET_KEY=cfg.SECRET_KEY,
    DATABASES={
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": cfg.DB_NAME,
        }
    },
    ROOT_URLCONF=__name__,
    MIDDLEWARE=["django.contrib.sessions.middleware.SessionMiddleware"],
    INSTALLED_APPS=["django.contrib.sessions"],
)


def index(request):
    session = request.session
    framework = "django"
    session[framework] = request.session.get(framework, 0) + 1
    return JsonResponse(
        {"framework": framework, "session": dict(request.session)}
    )


urlpatterns = [path("", index)]


if __name__ == "__main__":
    import sys
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
