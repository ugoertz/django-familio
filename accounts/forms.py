from userena.forms import EditProfileForm
from userena.utils import get_profile_model


class EditProfileFormExtra(EditProfileForm):
    class Meta:
        model = get_profile_model()
        exclude = ['user', 'sites']

