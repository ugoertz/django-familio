# -*- coding: utf8 -*-

import re

from django.contrib.auth import get_user_model
from django import forms
from userena.forms import EditProfileForm


class EditProfileFormExtra(EditProfileForm):
    class Meta(EditProfileForm.Meta):
        fields = ['mugshot',
                  'email_on_message',
                  'email_on_comment_answer',
                  'autosubscribe',
                  'signature',
                  'show_signatures',
                  'time_zone',
                  ]


class InviteForm(forms.Form):
    email = forms.EmailField(label="Email-Adresse",
                             widget=forms.TextInput(
                                 attrs={'style': 'width: 100%;'}))
    first_name = forms.CharField(label="Vorname",
                                 widget=forms.TextInput(
                                     attrs={'style': 'width: 100%;'}))
    last_name = forms.CharField(label="Nachname",
                                widget=forms.TextInput(
                                    attrs={'style': 'width: 100%;'}))
    message = forms.CharField(widget=forms.Textarea(
                                    attrs={'style': 'width: 100%;'}),
                              label="Nachricht")

    def clean_email(self):
        """ Validate that the e-mail address is unique. """

        if get_user_model().objects.filter(
                email__iexact=self.cleaned_data['email']):
            raise forms.ValidationError('Diese Email-Adresse gehört zu ' +
                                        'einem registrierten Benutzer. ' +
                                        'Bitte gib eine andere Adresse an.')
        return self.cleaned_data['email']


class AcceptInviteForm(forms.Form):
    username = forms.CharField(label="Benutzername",
                               widget=forms.TextInput(
                                   attrs={'style': 'width: 100%;'}))
    email = forms.EmailField(label="Email-Adresse",
                             widget=forms.TextInput(
                                 attrs={'style': 'width: 100%;'}))
    first_name = forms.CharField(label="Vorname",
                                 widget=forms.TextInput(
                                     attrs={'style': 'width: 100%;'}))
    last_name = forms.CharField(label="Nachname",
                                widget=forms.TextInput(
                                    attrs={'style': 'width: 100%;'}))
    password1 = forms.CharField(widget=forms.PasswordInput(
                                    render_value=False,
                                    attrs={'style': 'width: 100%;'}),
                                label="Passwort")
    password2 = forms.CharField(widget=forms.PasswordInput(
                                    render_value=False,
                                    attrs={'style': 'width: 100%;'}),
                                label="Passwort wiederholen")

    def clean_username(self):
        username = self.cleaned_data['username']
        if re.match('^[\@\. \w-]+$', username) is None:
            raise forms.ValidationError(
                    'Der Benutzername darf nur A-Z, a-z, Leerzeichen, ., - '
                    'und @ enthalten.')
        if get_user_model().objects.filter(username__iexact=username).exists():
            raise forms.ValidationError(
                    'Diesen Benutzernamen gibt es schon. Bitte wähle einen '
                    'anderen aus.')

        return username


    def clean(self):
        """
        Validates that the values entered into the two password fields match.
        Note that an error here will end up in ``non_field_errors()`` because
        it doesn't apply to a single field.
        """
        if 'password1' in self.cleaned_data and\
           'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] !=\
                    self.cleaned_data['password2']:
                raise forms.ValidationError(
                        'Die Passwörter stimmen nicht überein.')
            return self.cleaned_data

