# -*- coding: utf8 -*-

"""The forms of the genealogio app."""

from __future__ import absolute_import
from __future__ import unicode_literals

from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, Fieldset, MultiField

from partialdate.fields import PartialDateField
from .models import Family, Person


def clean_date(d):
    if not d:
        return d

    try:
        args = [int(x) for x in d.split('-')]
        assert len(args) <= 3
        assert len(args) <= 1 or 1 <= args[1] <= 12
        assert len(args) <= 2 or 1 <= args[2] <= 31
    except:
        raise forms.ValidationError(
                'Bitte das Datum im Format JJJJ-MM-TT angeben.')
    return d


class AddParentForm(forms.Form):

    family_name = forms.CharField(
            label="Familienname",
            required=False,
            max_length=200)
    start_date = forms.CharField(
            label="Hochzeitsdatum",
            required=False,
            help_text="Im Format JJJJ-MM-TT.",
            max_length=20)
    last_name_father = forms.CharField(
            label="Nachname",
            required=False,
            max_length=200)
    first_name_father = forms.CharField(
            label="Vorname",
            required=False,
            max_length=200)
    date_birth_father = forms.CharField(
            label="Geburtsdatum",
            required=False,
            help_text="Im Format JJJJ-MM-TT.",
            max_length=20)
    date_death_father = forms.CharField(
            label="Todesdatum",
            required=False,
            help_text="Im Format JJJJ-MM-TT.",
            max_length=20)
    last_name_mother = forms.CharField(
            label="Geburtsname",
            required=False,
            max_length=200)
    first_name_mother = forms.CharField(
            label="Vorname",
            required=False,
            max_length=200)
    date_birth_mother = forms.CharField(
            label="Geburtsdatum",
            required=False,
            help_text="Im Format JJJJ-MM-TT.",
            max_length=20)
    date_death_mother = forms.CharField(
            label="Todesdatum",
            required=False,
            help_text="Im Format JJJJ-MM-TT.",
            max_length=20)
    family_for = forms.IntegerField(widget=forms.HiddenInput)

    def clean_start_date(self):
        return clean_date(self.cleaned_data['start_date'])

    def clean_date_birth_father(self):
        return clean_date(self.cleaned_data['date_birth_father'])

    def clean_date_death_father(self):
        return clean_date(self.cleaned_data['date_death_father'])

    def clean_date_birth_mother(self):
        return clean_date(self.cleaned_data['date_birth_mother'])

    def clean_date_death_mother(self):
        return clean_date(self.cleaned_data['date_death_mother'])

    def __init__(self, *args, **kwargs):
        super(AddParentForm, self).__init__(*args, **kwargs)

        helper = FormHelper()
        helper.form_class = 'form-horizontal'
        helper.layout = Layout(
                Div(
                    Div('family_name', css_class="col-md-10"),
                    Div('start_date', css_class="col-md-2"),
                    css_class="row"
                ),
                Fieldset(
                    'Vater',
                    Div(
                        Div('first_name_father', css_class="col-md-4"),
                        Div('last_name_father', css_class="col-md-4"),
                        Div('date_birth_father', css_class="col-md-2"),
                        Div('date_death_father', css_class="col-md-2"),
                        css_class="row"
                    )
                ),
                Fieldset(
                    'Mutter',
                    Div(
                        Div('first_name_mother', css_class="col-md-4"),
                        Div('last_name_mother', css_class="col-md-4"),
                        Div('date_birth_mother', css_class="col-md-2"),
                        Div('date_death_mother', css_class="col-md-2"),
                        css_class="row"
                    )
                ),
                'family_for',
                Submit('Abspeichern', 'Abspeichern', css_class='btn-success'))
        self.helper = helper


class AddPersonForm(forms.ModelForm):

    marriedname = forms.CharField(
            required=False,
            max_length=200,
            label="Geburtsname",
            help_text="Ehename (sofern er sich vom jetzigen "
                      "Nachnamen unterscheidet).")
    gender = forms.ChoiceField(
            label="Geschlecht",
            choices=(
                (Person.MALE, 'männlich'),
                (Person.FEMALE, 'weiblich')))

    # use this field to provide further information:
    # - id of family to which this person should be attached as
    #   a child (for AddChildView)
    # - id of spouse (for AddSpouseView)
    attach_to = forms.CharField(
            max_length=60,
            widget=forms.HiddenInput)

    def clean_datebirth(self):
        return clean_date(self.cleaned_data['datebirth'])

    def clean_datedeath(self):
        return clean_date(self.cleaned_data['datedeath'])

    def __init__(self, *args, **kwargs):
        super(AddPersonForm, self).__init__(*args, **kwargs)

        helper = FormHelper()
        helper.form_class = 'form-horizontal'
        helper.layout = Layout(
                Div(
                    Div('first_name', css_class="col-md-4"),
                    Div('last_name', css_class="col-md-4"),
                    Div('marriedname', css_class="col-md-4"),
                    css_class="row"
                ),
                Div(
                    Div('datebirth', css_class="col-md-2"),
                    Div('datedeath', css_class="col-md-2"),
                    Div('gender', css_class="col-md-2"),
                    css_class="row"
                ),
                'attach_to',
                Submit('Abspeichern', 'Abspeichern', css_class='btn-success'))
        self.helper = helper

    class Meta:
        model = Person
        fields = ['first_name', 'last_name', 'datebirth', 'datedeath', ]

