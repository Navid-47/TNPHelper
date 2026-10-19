"""
Views for the core app — serves the landing page and error handlers.
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import connection, OperationalError


def home(request):
    """Render the landing page."""
    return render(request, 'home.html')


def custom_404(request, exception):
    """Custom 404 error page."""
    return render(request, '404.html', status=404)


def custom_500(request):
    """Custom 500 error page."""
    return render(request, '500.html', status=500)


@csrf_exempt
@require_http_methods(["GET", "HEAD"])
def healthz(request):
    """
    Unauthenticated health-check endpoint.

    Shallow check (default): returns 200 {"status": "ok"} immediately.
    Deep check (?deep=1):    performs a trivial DB query (SELECT 1).
                              Returns 503 {"status": "error"} on DB failure.

    This endpoint intentionally reveals NO secrets, settings, versions,
    stack traces, or database details. It is exempt from CSRF and login
    requirements. SECURE_SSL_REDIRECT does not affect it because the
    proxy sets HTTP_X_FORWARDED_PROTO=https, which satisfies Django.
    """
    if request.GET.get("deep") == "1":
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        except OperationalError:
            return JsonResponse({"status": "error"}, status=503)

    return JsonResponse({"status": "ok"})
