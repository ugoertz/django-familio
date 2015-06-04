# -*- coding: utf8 -*-

"""The models of the books app."""

from __future__ import absolute_import
from __future__ import unicode_literals

from collections import defaultdict
import json

from django import forms
from django.contrib.contenttypes.models import ContentType

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit

from genealogio.models import Event, Family, Person, TimelineItem
from notaro.models import Note, Source
from .models import Book, Collection, Item, FLAGS, FLAGS_FLAT


class FlagWidget(forms.widgets.MultiWidget):
    def __init__(self, attrs=None):
        widgets = []

        # add two CheckboxInputs for each flag
        # the second half will be used to store whether these are
        # default values inherited from parent, or values stored
        # in this instance; in the template the default values will
        # be colored differently
        for x in FLAGS_FLAT:
            widgets.extend([
                forms.CheckboxInput(),
                forms.CheckboxInput()])
        super(FlagWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            d = json.loads(value)
            l = [d[x[1]][x[2]] for x in FLAGS_FLAT]
            _from_parent = [isinstance(x, unicode) for x in l]

            def convert_to_bool(x):
                '''
                x is either a bool (in which case we can return it directly),
                or a string of the form 'true_by_default'/'false_by_default'
                '''
                if isinstance(x, unicode):
                    return x[:4] == 'true'
                else:
                    return x

            return [convert_to_bool(x) for x in l] + _from_parent
        else:
            # upon creating a new Book, value is empty
            return [FLAGS[x[1]][x[2]]['default'] for x in FLAGS_FLAT] +\
                    ([False] * len(FLAGS_FLAT))

    def format_output(self, rendered_widgets):
        """
        Given a list of rendered widgets (as strings), returns a Unicode string
        representing the HTML for the whole lot.
        """

        # Put the "label" as text, together with the input element, in a span.
        # Set class
        #  - fromparentON: if value is true and is obtained from parent
        #  - fromparentOFF: if value is false and is obtained from parent
        #  - fromself: if value is obtained from self.
        #  (In the template, set colors of the widget so that one can easily
        #  recognize those properties that are inherited from a parent.)
        template = '<span class="%s" style="margin-right: 20px; display: ' +\
                   'inline-block; font-family: cabin, helvetica, sans;">%s</br>'

        labels = []

        # store which properties are inherited
        # (this information was stored in the "second half" of the rendered
        # widgets
        _from_parent = [
                x.find('checked') != -1
                for x in rendered_widgets[len(FLAGS_FLAT):]]

        for i, x in enumerate(FLAGS_FLAT):
            lbl = FLAGS[x[1]][x[2]]['label']
            value = rendered_widgets[i].find('checked') != -1

            if _from_parent[i]:
                cl = 'fromparent'
                if value:
                    cl += 'ON'
                else:
                    cl += 'OFF'
            else:
                cl = 'fromself'
            labels.append(template % (cl, lbl))
        close = ['</span>'] * len(FLAGS_FLAT)

        return ''.join(
                [item for l in zip(
                    labels,
                    rendered_widgets[:len(FLAGS_FLAT)],
                    close)
                    for item in l])


class FlagField(forms.fields.MultiValueField):
    widget = FlagWidget

    def __init__(self, *args, **kwargs):
        list_fields = [
                forms.fields.BooleanField(),
                forms.fields.BooleanField()]
        super(FlagField, self).__init__(list_fields, *args, **kwargs)

    def compress(self, values):
        """Compress list to single object."""

        d = defaultdict(dict)
        for i, x in enumerate(FLAGS_FLAT):
            d[x[1]][x[2]] = values[i]
        return json.dumps(d)


class BookForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BookForm, self).__init__(*args, **kwargs)

        helper = FormHelper()
        helper.form_class = 'form-horizontal'
        helper.label_class = 'col-md-2'
        helper.field_class = 'col-md-9'
        helper.layout = Layout(
                'title',
                'description',
                Div('public',
                    css_class="col-md-offset-1"),
                'flags',
                'titlepage',
                Submit('Abspeichern', 'Abspeichern', css_class='btn-success'))
        self.helper = helper

    class Meta:
        model = Book
        fields = ['title', 'description', 'public', 'titlepage', ]


class BookCreateForm(BookForm):

    populate = forms.ChoiceField(choices=(
        ('-', 'Keine Objekte hinzufügen'),
        ('DB', 'Gesamte Datenbank'),
        ('A', 'Vorfahren von Person/Familie'),
        ('AD', 'Vorfahren und Nachkommen von Person/Familie'),
        ('D', 'Nachkommen von Person/Familie')
        ), label='Objekte hinzufügen')

    # pylint: disable=no-member
    reference = forms.CharField(widget=forms.Select(choices=[]))

    def __init__(self, *args, **kwargs):
        super(BookCreateForm, self).__init__(*args, **kwargs)

        self.helper.layout = Layout(
                'title',
                'description',
                Div('public',
                    css_class="col-md-offset-1"),
                'populate',
                'reference',
                'flags',
                'titlepage',
                Submit('Abspeichern', 'Abspeichern', css_class='btn-success'))


class CollectionForm(forms.ModelForm):
    ordering = forms.CharField(widget=forms.HiddenInput, required=False)
    c_flags = FlagField(label="Einstellungen")

    def __init__(self, *args, **kwargs):
        super(CollectionForm, self).__init__(*args, **kwargs)
        helper = FormHelper()
        helper.form_class = 'form-horizontal'
        helper.label_class = 'col-md-2'
        helper.field_class = 'col-md-9'
        helper.layout = Layout(
                'title',
                Div('active',
                    css_class="col-md-offset-1"),
                'c_flags',
                'ordering',
                Submit('Abspeichern', 'Abspeichern', css_class='btn-success'))

        self.helper = helper

    def clean(self):
        super(CollectionForm, self).clean()

        d = defaultdict(dict)
        if self.instance.flags:
            d.update(json.loads(self.instance.flags))

        new_flags = json.loads(self.cleaned_data['c_flags'])

        # find those flags in self.cleaned_data['c_flags'] which differ from
        # defaults:
        if self.instance.parent:
            default_flags = json.loads(
                    self.instance.parent.get_flags_json(show_source=False))
        else:
            default_flags = json.loads(self.instance.book.flags)

        for m in new_flags:
            for o in new_flags[m]:
                if m in d and o in d[m]:
                    # stored in this instance already, so update
                    # the value from the form
                    d[m][o] = new_flags[m][o]
                else:
                    # not yet stored in this instance, so compare
                    # with default
                    if new_flags[m][o] != default_flags[m][o]:
                        # differs from default, so store:
                        d[m][o] = new_flags[m][o]

        self.instance.flags = json.dumps(d)

    class Meta:
        model = Collection
        fields = ['title', 'active', ]


class CollectionCreateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CollectionCreateForm, self).__init__(*args, **kwargs)

        modellist = [Note, Person, Family, Event, Source, TimelineItem]

        # pylint: disable=no-member
        self.fields['model'].queryset = ContentType.objects.filter(
                id__in=[ContentType.objects.get_for_model(m).id
                        for m in modellist])

        helper = FormHelper()
        helper.form_class = 'form-horizontal'
        helper.label_class = 'col-md-2'
        helper.field_class = 'col-md-9'
        helper.layout = Layout(
                'title',
                Div('active',
                    css_class="col-md-offset-1"),
                'model',
                'parent',
                Submit('Abspeichern', 'Abspeichern', css_class='btn-success'))

        self.helper = helper

    class Meta:
        model = Collection
        fields = ['title', 'active', 'model', 'parent' ]
        widgets = {'parent': forms.HiddenInput, }


class ItemForm(forms.ModelForm):

    c_flags = FlagField(label="Einstellungen")

    def __init__(self, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)

        helper = FormHelper()
        helper.form_class = 'form-horizontal'
        helper.label_class = 'col-md-2'
        helper.field_class = 'col-md-9'
        helper.layout = Layout(
                'title',
                Div('use_custom_title_in_pdf', 'active',
                    css_class="col-md-offset-1"),
                'c_flags',
                'text',
                Submit('Abspeichern', 'Abspeichern', css_class='btn-success'))

        self.helper = helper

    def clean(self):
        super(ItemForm, self).clean()

        d = defaultdict(dict)
        if self.instance.flags:
            d.update(json.loads(self.instance.flags))

        new_flags = json.loads(self.cleaned_data['c_flags'])

        # find those flags in self.cleaned_data['c_flags'] which differ from
        # defaults:
        default_flags = json.loads(
                self.instance.parent.get_flags_json(show_source=False))

        for m in new_flags:
            for o in new_flags[m]:
                if m in d and o in d[m]:
                    # stored in this instance already, so update
                    # the value from the form
                    d[m][o] = new_flags[m][o]
                else:
                    # not yet stored in this instance, so compare
                    # with default
                    if new_flags[m][o] != default_flags[m][o]:
                        # differs from default, so store:
                        d[m][o] = new_flags[m][o]

        self.instance.flags = json.dumps(d)

    class Meta:
        model = Item
        fields = ['title', 'use_custom_title_in_pdf', 'active', 'text', ]


class ItemCreateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ItemCreateForm, self).__init__(*args, **kwargs)

        modellist = [Note, Person, Family, Event, Source, TimelineItem]

        # pylint: disable=no-member
        self.fields['obj_content_type'].queryset = ContentType.objects.filter(
                id__in=[ContentType.objects.get_for_model(m).id
                        for m in modellist])

        helper = FormHelper()
        helper.form_class = 'form-horizontal'
        helper.label_class = 'col-md-2'
        helper.field_class = 'col-md-9'
        helper.layout = Layout(
                'obj_content_type',
                'obj_id',
                'title',
                Div('use_custom_title_in_pdf',
                    'active',
                    css_class="col-md-offset-1"),
                'parent',
                Submit('Abspeichern', 'Abspeichern', css_class='btn-success'))

        self.helper = helper

    class Meta:
        model = Item
        fields = ['obj_content_type', 'obj_id',
                  'title', 'use_custom_title_in_pdf',
                  'active', 'parent', ]
        widgets = {'parent': forms.HiddenInput, }

