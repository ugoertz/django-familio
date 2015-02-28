from django.conf.urls import patterns, url

from .forms import EditProfileFormExtra
from .views import InviteView, AcceptInvitationView


urlpatterns = patterns('',
                       url(r'^invite/', InviteView.as_view(),
                           name="send-invitation"),
                       url(r'^register/(?P<key>[a-f0-9]+)/$',
                           AcceptInvitationView.as_view(),
                           name="accept-invitation"),
                       url(r'^(?P<username>[\.\w-]+)/edit/$',
                           'userena.views.profile_edit',
                           {'edit_profile_form': EditProfileFormExtra},
                           name='edit-profile'))
