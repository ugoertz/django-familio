from django.contrib.sites.models import Site
from django.core.exceptions import PermissionDenied

from accounts.models import UserSite


class CheckUserSiteMiddleware(object):

    def process_request(self, request):
        if (request.path_info.startswith('/admin/') and
                request.user.is_authenticated() and
                not request.user.is_superuser and
                Site.objects.get_current() not in
                request.user.userprofile.sites.filter(
                    usersite__role__in=[UserSite.STAFF, UserSite.SUPERUSER])):
            raise PermissionDenied
