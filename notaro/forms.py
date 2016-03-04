# -*- coding: utf8 -*-

"""The forms of the notaro app."""

from __future__ import absolute_import
from __future__ import unicode_literals

from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field
from crispy_forms.bootstrap import PrependedText


class ThumbnailForm(forms.Form):

    page = forms.IntegerField(
            label="",
            widget=forms.TextInput(attrs={'size': '5'}))
    pk = forms.IntegerField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(ThumbnailForm, self).__init__(*args, **kwargs)

        helper = FormHelper()
        helper.layout = Layout(
                PrependedText('page', 'Vorschau für', placeholder="Seite"),
                Field('pk'),
                Submit('create', 'Erstellen', css_class="btn-sm pull-right"),
                )
        self.helper = helper

