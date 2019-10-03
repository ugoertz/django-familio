from django.contrib.sites.models import Site
from django.core.exceptions import PermissionDenied

from accounts.models import UserSite


class CheckUserSiteMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (request.path_info.startswith('/admin/') and
                request.user.is_authenticated and  # allow non-authenticated
                                                   # users: might be trying
                                                   # to log in right now
                not request.user.is_superuser and
                Site.objects.get_current() not in
                request.user.userprofile.sites.filter(
                    usersite__role__in=[UserSite.STAFF, UserSite.SUPERUSER])):
            raise PermissionDenied

        response = self.get_response(request)
        return response
