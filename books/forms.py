# -*- coding: utf8 -*-

"""The models of the books app."""

from collections import defaultdict
import json

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.forms.renderers import get_default_renderer
from django.utils.safestring import mark_safe

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit

# from base.util import eprint
from genealogio.models import Event, Family, Person, TimelineItem
from notaro.models import Note, Source
from .models import Book, Collection, Item, FLAGS, FLAGS_FLAT


class FlagWidget(forms.widgets.MultiWidget):
    template_name = 'books/flagwidget.html'

    def __init__(self, attrs=None):
        widgets = []

        # add a CheckboxInput for each flag
        # and add a HiddenInput for each flag
        # the HiddenInputs will be used to store whether these are
        # default values inherited from parent, or values stored
        # in this instance; in the template the default values will
        # be colored differently
        for x in FLAGS_FLAT:
            widgets.append(forms.CheckboxInput())
        for x in FLAGS_FLAT:
            widgets.append(forms.HiddenInput())
        super().__init__(widgets, attrs)

    def decompress(self, value):
        '''
        Value is in JSON format, for example:
        {"genealogio.family": {"include_timeline": "false_by_default",
        "include_grandchildren": false}, "genealogio.person":
        {"include_places": "true_by_default"}}

        So a string value ('true_by_default', 'false_by_default') indicates
        that this is the vale pre-defined by the parent. A bool value
        indicates an individual value for this item (which might or might
        not be equal to the default - after the first change this is not
        checked anymore).

        Returns a list of values, one for each widget (including the
        HiddenInputs).
        '''

        if value:
            d = json.loads(value)
            li = [d[x[1]][x[2]] for x in FLAGS_FLAT]
            _from_parent = [isinstance(x, str) for x in li]

            def convert_to_bool(x):
                '''
                x is either a bool (in which case we can return it directly),
                or a string of the form 'true_by_default'/'false_by_default'
                '''
                if isinstance(x, str):
                    return x[:4] == 'true'
                else:
                    return x

            return [convert_to_bool(x) for x in li] + _from_parent
        else:
            # upon creating a new Book, value is empty
            return [FLAGS[x[1]][x[2]]['default'] for x in FLAGS_FLAT] +\
                    ([False] * len(FLAGS_FLAT))

    def use_required_attribute(self, initial):
        return False

    def render(self, name, value, attrs=None, renderer=None):
        decompressed = self.decompress(value)
        length = len(decompressed)//2
        context = self.get_context(name, value, attrs)
        if renderer is None:
            renderer = get_default_renderer()
        for i, sw in enumerate(context['widget']['subwidgets'][:length]):
            sw['from_parent'] = decompressed[i+length]
            x = FLAGS_FLAT[i]
            sw['label_text'] = mark_safe(FLAGS[x[1]][x[2]]['label'])
        return mark_safe(renderer.render(self.template_name, context))


class FlagField(forms.fields.MultiValueField):
    widget = FlagWidget

    def __init__(self, *args, **kwargs):
        list_fields = [forms.fields.BooleanField() for x in FLAGS_FLAT]
        super().__init__(list_fields, *args, **kwargs)

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
    reference = forms.CharField(
            required=False,
            widget=forms.Select(choices=[]))

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
        fields = ['title', 'active', 'model', 'parent', ]
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

