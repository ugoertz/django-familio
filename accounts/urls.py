from django.urls import re_path

from userena.views import profile_edit

from .forms import EditProfileFormExtra
from .views import InviteView, AcceptInvitationView


urlpatterns = (
        re_path(r'^invite/', InviteView.as_view(),
            name="send-invitation"),
        re_path(r'^register/(?P<key>\w+)/$',
            AcceptInvitationView.as_view(),
            name="accept-invitation"),
        re_path(r'^(?P<username>[\@ \.\w-]+)/edit/$',
            profile_edit,
            {'edit_profile_form': EditProfileFormExtra},
            name='edit-profile')
        )
