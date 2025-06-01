from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, HTML, Layout, Submit

from .models import FamilyTree


class FTForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        helper = FormHelper()
        helper.form_class = 'form-horizontal'
        helper.label_class = 'col-md-2'
        helper.field_class = 'col-md-9'
        helper.layout = Layout(
            'title',
            'levels_up',
            'levels_down',
            Div('public', css_class="col-md-offset-1"),
            HTML('<h3>Erweiterte Einstellungen</h3>'),
            'papersize',
            'width',
            'height',
            'resize_image_files',
            'black_white',
            Submit('Abspeichern', 'Abspeichern', css_class='btn-success'),
        )
        self.helper = helper

    class Meta:
        model = FamilyTree
        fields = ['title', 'public', 'levels_up', 'levels_down', 
                  'width', 'height', 'papersize',
                  'resize_image_files',
                  'black_white',
                  ]


class FTCreateForm(FTForm):

    # pylint: disable=no-member
    reference = forms.CharField(
            required=True,
            widget=forms.Select(choices=[]))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper.layout = Layout(
                'title',
                'levels_up',
                'levels_down',
                Div('public',
                    css_class="col-md-offset-1"),
                'reference',
                Submit('Abspeichern', 'Abspeichern', css_class='btn-success'))



