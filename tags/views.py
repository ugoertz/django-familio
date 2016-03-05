# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals

from django.apps import apps
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView, View, ListView
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import Count

from braces.views import LoginRequiredMixin

from tags.models import CustomTag


class TagList(LoginRequiredMixin, ListView):
    model = CustomTag

    def get_queryset(self):
        return CustomTag.objects\
                        .all()\
                        .annotate(num_times=Count(
                            'tags_customtagthrough_items'))\
                        .order_by('-num_times', 'name')


class TagSearch(LoginRequiredMixin, TemplateView):

    template_name = 'tags/tag_search.html'


class SaveTags(LoginRequiredMixin, View):

    def post(self, request, app, model, pk):
        if not self.request.user.userprofile.is_staff_for_site:
            messages.error(request, 'Es ist ein Fehler aufgetreten.')
            return HttpResponseRedirect('/')

        # pylint: disable=no-member
        model_class = apps.get_model(app_label=app, model_name=model)
        obj = model_class.objects.get(pk=pk)

        taglist = []
        for x in request.POST['tags'].split(','):
            t = x.strip()
            if t.startswith('new-'):
                t = 'tag-' + t[4:]
                try:
                    # Make sure that tag does not contain non-allowed
                    # characters
                    reverse('tag-search', kwargs={'tag': t}),
                except:
                    messages.error(
                            request,
                            'Das Schlagwort "%s" kann ' % t[4:] +
                            'nicht gespeichert werden. '
                            'Erlaubte Zeichen in Schlagwörtern: '
                            'Buchstaben, ".;_+-:!" und Leerzeichen.')
                    t = ''
            elif not t.startswith('tag-'):
                # This is a tag attached to an object in the database.  Check
                # whether for this object, a tag exists already. If so, we
                # need to make sure that the object.as_tag() representation has
                # not changed in the meantime.  (This could happen, e.g., when
                # a change to a person's name is made.)
                try:
                    tag = CustomTag.objects.get(slug=t.split(' ')[-1])
                    t_text = tag.get_object_for_tag().as_tag()[0]

                    if tag.name != t_text:
                        # The as_tag representation has changed!  Update the
                        # existing tag accordingly.
                        tag.name = t
                        tag.save()
                except:
                    pass
            if t:
                taglist.append(t)

        obj.tags.set(*taglist)

        if request.POST['next']:
            return HttpResponseRedirect(request.POST['next'])

        return HttpResponseRedirect(
                reverse(
                    '%s-detail' % model,
                    kwargs={'pk': pk, }))


