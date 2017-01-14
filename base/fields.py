# -*- coding: utf8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from django import forms


# from http://koensblog.eu/blog/7/multiple-file-upload-django/


class MultiFileInput(forms.FileInput):
    def render(self, name, value, attrs={}):
        attrs['multiple'] = 'multiple'
        attrs['class'] = attrs.get('class', '') + ' js-multi with-preview'
        return '<span class="file-wrapper"><span class="button">Datei auswählen (Klick oder Drag-and-drop)</span>' +\
                super(MultiFileInput, self).render(name, None, attrs=attrs) +\
                '</span><div id="filelist" style="margin-top: 10px;"></div>'

    def value_from_datadict(self, data, files, name):
        if hasattr(files, 'getlist'):
            return files.getlist(name)
        else:
            return [files.get(name)]

    def use_required_attribute(self, initial):
        return False

 
class MultiFileField(forms.FileField):
    widget = MultiFileInput

    def __init__(self, *args, **kwargs):
        self.min_num = kwargs.pop('min_num', 0)
        self.max_num = kwargs.pop('max_num', None)
        self.maximum_file_size = kwargs.pop('maximum_file_size', None)
        super(MultiFileField, self).__init__(*args, **kwargs)

    def to_python(self, data):
        ret = []
        for item in data:
            ret.append(super(MultiFileField, self).to_python(item))
        return ret

    def validate(self, data):
        super(MultiFileField, self).validate(data)
        num_files = len(data)
        if len(data) and not data[0]:
            num_files = 0
        if not num_files:
            raise forms.ValidationError('Es wurde keine Datei angegeben.')

