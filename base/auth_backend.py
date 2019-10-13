from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist

from userena.backends import UserenaAuthenticationBackend


class SiteBackend(UserenaAuthenticationBackend):
    def authenticate(self, request, **credentials):
        if 'username' in credentials and 'password' in credentials:
            # auth request from admin login form
            user_or_none = super().authenticate(
                    request,
                    identification=credentials['username'],
                    password=credentials['password'])
        else:
            user_or_none = super().authenticate(request, **credentials)
        if (user_or_none and
                Site.objects.get_current()
                not in user_or_none.userprofile.sites.all()):
            return
        return user_or_none

    def get_user(self, user_id):
        try:
            return get_user_model().objects.get(
                pk=user_id, userprofile__sites=Site.objects.get_current())
        except ObjectDoesNotExist:
            return None
