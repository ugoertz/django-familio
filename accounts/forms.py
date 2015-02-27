from userena.forms import EditProfileForm
#  from userena.utils import get_profile_model


class EditProfileFormExtra(EditProfileForm):
    class Meta(EditProfileForm.Meta):
        fields = ['privacy', 'mugshot',
                  'email_on_message', 'email_on_comment_answer']

