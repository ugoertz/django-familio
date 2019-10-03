from django.conf import settings
from django.http import Http404
from .views import NoteDetailVerboseLink


class NotaroMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code != 404 or not request.user.is_authenticated:
            return response

        try:
            # Try the page view.
            return NoteDetailVerboseLink.as_view()(request).render()
        except Http404:
            # If the page view 404s, return the ORIGINAL 404 response.
            return response
        except:
            # If anything else happened, something is wrong with the page view.
            # Return the original (404) response, unless we're in DEBUG.
            if settings.DEBUG:
                raise
            return response
