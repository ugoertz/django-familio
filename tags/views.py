from __future__ import unicode_literals

from django.http import HttpResponseRedirect
from django.views.generic import TemplateView, View
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models.loading import get_model

from braces.views import LoginRequiredMixin


class TagSearch(LoginRequiredMixin, TemplateView):

    template_name = 'tags/tag_search.html'


class SaveTags(LoginRequiredMixin, View):

    def post(self, request, app, model, pk):
        if not self.request.user.userprofile.is_staff_for_site:
            messages.error(request, 'Es ist ein Fehler aufgetreten.')
            return HttpResponseRedirect('/')

        # pylint: disable=no-member
        model_class = get_model(app, model)
        obj = model_class.objects.get(pk=pk)

        taglist = []
        for x in request.POST['tags'].split(','):
            t = x.strip()
            if t.startswith('new-'):
                t = 'tag-' + t[4:]
            if t:
                taglist.append(t)

        obj.tags.set(*taglist)

        if request.POST['next']:
            return HttpResponseRedirect(request.POST['next'])

        return HttpResponseRedirect(
                reverse(
                    '%s-detail' % model,
                    kwargs={'pk': pk, }))

