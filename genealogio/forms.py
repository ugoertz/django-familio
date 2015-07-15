# -*- coding: utf8 -*-

"""The forms of the genealogio app."""

from __future__ import absolute_import
from __future__ import unicode_literals

import datetime

from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, Fieldset

from .models import Family, Person


def clean_date(d):
    if not d:
        return d

    try:
        assert (len(d) == 4 or
                (len(d) == 7 and d[4] == '-') or
                (len(d) == 10 and d[4] == d[7] == '-'))
        args = [int(x) for x in d.split('-')]
        assert len(args) <= 3
        assert len(args) <= 1 or 1 <= args[1] <= 12
        if len(args) == 3:
            datetime.date(*args)
    except:
        raise forms.ValidationError(
                'Bitte das Datum im Format JJJJ-MM-TT angeben.')
    return d


def clean_name(n):
    if '(' in n or ')' in n:
        raise forms.ValidationError(
                'Der Name darf keine Klammern enthalten. Spitznamen u.ä. '
                'müssen separat im Verwaltungsbereich eingegeben werden. '
                'Falls der Name selbst wirklich Klammern enthält, muss er '
                'im Verwaltungsbereich eingegeben werden.')
    return n


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
    family_rel_type = forms.ChoiceField(
            choices=Family.FAMILY_REL_TYPE)
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
    married_name_mother = forms.CharField(
            label="Ehename",
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

    def clean_first_name_father(self):
        return clean_name(self.cleaned_data['first_name_father'])

    def clean_first_name_mother(self):
        return clean_name(self.cleaned_data['first_name_mother'])

    def clean_last_name_father(self):
        return clean_name(self.cleaned_data['last_name_father'])

    def clean_last_name_mother(self):
        return clean_name(self.cleaned_data['last_name_mother'])

    def clean_married_name_mother(self):
        return clean_name(self.cleaned_data['married_name_mother'])

    def clean_family_name(self):
        return clean_name(self.cleaned_data['family_name'])

    def __init__(self, *args, **kwargs):
        super(AddParentForm, self).__init__(*args, **kwargs)

        helper = FormHelper()
        helper.form_class = 'form-horizontal'
        helper.layout = Layout(
                Div(
                    Div('family_name', css_class="col-md-8"),
                    Div('family_rel_type', css_class="col-md-2"),
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
                        Div('first_name_mother', css_class="col-md-3"),
                        Div('last_name_mother', css_class="col-md-3"),
                        Div('married_name_mother', css_class="col-md-2"),
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
            label="Ehename",
            help_text="Ehename (sofern er sich vom "
                      "Geburtsnamen unterscheidet).")

    # use this field to provide further information:
    # - id of family to which this person should be attached as
    #   a child (for AddChildView)
    # - id of spouse (for AddSpouseView)
    attach_to = forms.CharField(
            max_length=60,
            widget=forms.HiddenInput)

    def clean_first_name(self):
        return clean_name(self.cleaned_data['first_name'])

    def clean_last_name(self):
        return clean_name(self.cleaned_data['last_name'])

    def clean_marriedname(self):
        return clean_name(self.cleaned_data['marriedname'])

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
                    Div('gender_type', css_class="col-md-2"),
                    css_class="row"
                ),
                'attach_to',
                Submit('Abspeichern', 'Abspeichern', css_class='btn-success'))
        self.helper = helper

    class Meta:
        model = Person
        fields = [
                'first_name',
                'last_name',
                'datebirth',
                'datedeath',
                'gender_type', ]


class AddSpouseForm(AddPersonForm):

    family_name = forms.CharField(
            label="Familienname",
            required=False,
            max_length=200)
    family_rel_type = forms.ChoiceField(
            choices=Family.FAMILY_REL_TYPE)
    start_date = forms.CharField(
            max_length=20,
            required=False,
            label='Hochzeitsdatum',
            help_text="Im Format JJJJ-MM-TT."
            )

    def clean_family_name(self):
        return clean_name(self.cleaned_data['family_name'])

    def clean_start_date(self):
        return clean_date(self.cleaned_data['start_date'])

    def __init__(self, *args, **kwargs):
        super(AddSpouseForm, self).__init__(*args, **kwargs)

        self.helper.layout = Layout(
                Fieldset(
                    'Familie',
                    Div(
                        Div('family_name', css_class="col-md-8"),
                        Div('family_rel_type', css_class="col-md-2"),
                        Div('start_date', css_class="col-md-2"),
                        css_class="row"
                    )),
                Fieldset(
                    'Ehepartner',
                    Div(
                        Div('first_name', css_class="col-md-4"),
                        Div('last_name', css_class="col-md-4"),
                        Div('marriedname', css_class="col-md-4"),
                        css_class="row"
                    ),
                    Div(
                        Div('datebirth', css_class="col-md-2"),
                        Div('datedeath', css_class="col-md-2"),
                        css_class="row"
                    )),
                'attach_to',
                Submit('Abspeichern', 'Abspeichern', css_class='btn-success'))

    class Meta:
        model = Person
        fields = ['first_name', 'last_name', 'datebirth', 'datedeath', ]

