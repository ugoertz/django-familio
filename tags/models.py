# -*- coding: utf8 -*-

from __future__ import unicode_literals

from django.db import models
from django.core.urlresolvers import reverse
from taggit.models import GenericTaggedItemBase, TagBase


class CustomTag(TagBase):
    """
    A tag can have one of the following two forms:

    - a "free" tag, of the form "tag-XXX", where XXX is the keyword (e.g.,
      "tag-marriage"). In this case, slug == name.

    - an "object tag", pointing to an object of the database, represented by
      a string of the form "displayed_tag app.model-id", where displayed_tag is
      the text displayed on the web site, app.model points to some model (e.g.,
      genealogio.person), and id is the id of the specific instance of that
      model. In this case, slug == "app.model-id".

      It is assumed that the detail view for objects of this kind is named
      "model-detail".

      The model must have an as_tag method which returns a a pair consisting of
      the displayed_tag string for the given instance and a second string
      describing the tag which is used as the selectize option. Neither of these
      strings should contain the "app.model-id" part. The second string could just
      be the same as the first one, or it could contain additional information
      that might be useful for making a choice of text (e.g., date of birth of
      a person to distinguish between several persons with the same or similar
      names).
    """

    SPAN_TEMPLATE = '<a href="%s" class="btn btn-default btn-xs cabin" style="margin: 3px; background-color: %s;">%s</a>'

    def slugify(self, tag, i=None):
        if not tag:
            raise Exception('Error in CustomTag.slugify: empty tag.')

        if tag.startswith('tag-'):
            try:
                reverse('tag-search', kwargs={'tag': tag}),
                return tag
            except:
                raise Exception('Error in CustomTag.slugify: empty tag.')
        else:
            try:
                slug = tag.split(' ')[-1]
                assert slug.find('.') != -1
                _, id = slug.split('-')
                int(id)
                return slug
            except:
                raise Exception('Error in CustomTag.slugify: empty tag.')

    def as_span(self):
        if self.slug.startswith('tag-'):
            return CustomTag.SPAN_TEMPLATE % (
                    reverse('tag-search', kwargs={'tag': self.slug}),
                    '#eeeeee',
                    self.name[4:])

        try:
            model = self.slug[self.slug.find('.')+1:self.slug.find('-')]
            bg_color = {
                    'person': 'lightgreen',
                    'family': 'lightblue',
                    'event': 'yellow',
                    'place': 'orange',
                    }.get(model, 'red')
            tag = ' '.join(self.name.split(' ')[:-1])
            url = reverse(
                    '%s-detail' % model,
                    kwargs={'pk': int(self.slug.split('-')[1])})

            return CustomTag.SPAN_TEMPLATE % (url, bg_color, tag)
        except:
            return '<span>%s</span>' % self.name

    def as_tag_text(self):
        if self.slug.startswith('tag-'):
            return self.name[4:]

        return ' '.join(self.name.split(' ')[:-1])



class CustomTagThrough(GenericTaggedItemBase):
    tag = models.ForeignKey(
            CustomTag,
            related_name="%(app_label)s_%(class)s_items")



