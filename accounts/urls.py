from django.conf.urls import url

from userena.views import profile_edit

from .forms import EditProfileFormExtra
from .views import InviteView, AcceptInvitationView


urlpatterns = (
        url(r'^invite/', InviteView.as_view(),
            name="send-invitation"),
        url(r'^register/(?P<key>\w+)/$',
            AcceptInvitationView.as_view(),
            name="accept-invitation"),
        url(r'^(?P<username>[\@ \.\w-]+)/edit/$',
            profile_edit,
            {'edit_profile_form': EditProfileFormExtra},
            name='edit-profile')
        )
