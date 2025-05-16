from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_str
from django.conf import settings
from django import forms
from .models import Comment


class CommentForm(forms.ModelForm):
    parent = forms.CharField(widget=forms.HiddenInput(
                 attrs={'class': 'parent'}), required=False)
    content_type = forms.CharField(widget=forms.HiddenInput)
    object_pk = forms.CharField(widget=forms.HiddenInput)

    def __init__(self, target_object, data=None, initial=None):
        self.target_object = target_object
        if initial is None:
            initial = {}
        initial.update({
            'content_type': str(self.target_object._meta),
            'object_pk': str(self.target_object._get_pk_val()),
            })
        auto_id = 'id_' + str(target_object.id) + '_%s'
        super(CommentForm, self).__init__(
            data=data, initial=initial, auto_id=auto_id)

    def get_comment_create_data(self):
        """
        Returns the dict of data to be used to create a comment.
        """
        return dict(
            content_type=ContentType.objects.get_for_model(self.target_object),
            object_pk=force_str(self.target_object._get_pk_val()),
            content=self.cleaned_data["content"],
            site_id=settings.SITE_ID,
            )

    class Meta:
        model = Comment
        fields = ('content',)
        widgets = {
                'content': forms.Textarea(attrs={'cols': 40, 'rows': 8}),
                }
