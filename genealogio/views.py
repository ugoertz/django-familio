# -*- coding: utf8 -*-

import datetime
import math
import cairocffi as cairo
import json

from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.models import Site
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.generic import (
        CreateView, DetailView, FormView, View)
from django.shortcuts import render

from djgeojson.views import GeoJSONLayerView

from base.views import CurrentSiteMixin, PaginateListView
from maps.models import Place
from partialdate.fields import string_to_partialdate

from .forms import AddParentForm, AddPersonForm, AddSpouseForm
from .models import (
        Name, Person, PersonPlace, Event, Family, TimelineItem, PersonFamily)


class HomeGeoJSON(LoginRequiredMixin, GeoJSONLayerView):
    model = Place
    geometry_field = 'location'
    properties = ['title', 'typ', ]
    bbox_auto = True

    def get_queryset(self):

        # pylint: disable=no-member
        p_birth = set(PersonPlace.objects.filter(
            person__sites=Site.objects.get_current(), typ=PersonPlace.BIRTH)
            .values_list('place', flat=True))
        # pylint: disable=no-member
        p_death = set(PersonPlace.objects.filter(
            person__sites=Site.objects.get_current(), typ=PersonPlace.DEATH)
            .values_list('place', flat=True))

        p_combined = p_birth | p_death

        qs = Place.objects.filter(id__in=p_combined)\
            .filter(personplace__person__sites=Site.objects.get_current(),
                    personplace__typ__in=[PersonPlace.BIRTH,
                                          PersonPlace.DEATH])\
            .annotate(num=Count('personplace'))

        def get_t(n):
            if n >= 9:
                return '9'
            elif n >= 6:
                return '6'
            elif n >= 3:
                return '3'
            return ''

        for p in qs:
            if p.id in p_birth and p.id in p_death:
                p.typ = 'birthdeath' + get_t(p.num)
            elif p.id in p_death:
                p.typ = 'death' + get_t(p.num)
            else:
                p.typ = 'birth' + get_t(p.num)

        return qs


class PPlacesGeoJSON(LoginRequiredMixin, GeoJSONLayerView):
    model = Place
    geometry_field = 'location'
    properties = ['title', 'typ', ]
    bbox_auto = True

    def get_queryset(self):
        # pylint: disable=no-member
        person = Person.objects.get(id=self.request.GET['person_id'])

        qs = person.places.all().distinct()
        for p in qs:
            if p.personplace_set.filter(
                    person=person, typ=PersonPlace.BIRTH).exists():
                if p.personplace_set.filter(
                        person=person, typ=PersonPlace.DEATH).exists():
                    p.typ = 'birthdeath'
                else:
                    p.typ = 'birth'
            elif p.personplace_set.filter(
                    person=person, typ=PersonPlace.DEATH).exists():
                p.typ = 'death'
            else:
                # for other places choose the type according to order
                # specified in model definition (i.e., by start date)
                p.typ = p.personplace_set.filter(
                        person=person)[0].typ
        return qs


class PersonList(LoginRequiredMixin, CurrentSiteMixin, PaginateListView):
    """Display list of all persons."""

    model = Person

    def get_queryset(self):
        qs = super(PersonList, self).get_queryset()
        if 'order_by' in self.kwargs:
            if self.kwargs['order_by'] == 'birthname':
                qs = qs.order_by('last_name', 'first_name', 'datebirth')
            elif self.kwargs['order_by'] == 'lastname':
                qs = qs.order_by(
                        'last_name_current', 'first_name', 'datebirth')
            elif self.kwargs['order_by'] == 'firstname':
                qs = qs.order_by('first_name', 'last_name', 'datebirth')
            elif self.kwargs['order_by'] == 'datebirth':
                qs = qs.order_by('datebirth', 'datedeath', 'last_name')
            elif self.kwargs['order_by'] == 'datebirthdesc':
                qs = qs.order_by('-datebirth', '-datedeath', 'last_name')
        return qs


class FamilyList(LoginRequiredMixin, CurrentSiteMixin, PaginateListView):
    """Display list of all persons."""

    model = Family


class PersonDetail(LoginRequiredMixin, CurrentSiteMixin, DetailView):
    """Display details for a person."""

    model = Person


class FamilyDetail(LoginRequiredMixin, CurrentSiteMixin, DetailView):
    """Display details for a family."""

    model = Family

    @staticmethod
    def get_timeline_items(objid, fr, to):
        # pylint: disable=no-member
        timeline = TimelineItem.objects.filter(families__isnull=True) |\
                   TimelineItem.objects.filter(families=objid)
        timeline = timeline.order_by('start_date', 'end_date', 'title')

        # not so beautiful, but we cannot filter on properties:
        timeline = [x for x in timeline if fr <= x.end and x.start <= to]
        return timeline

    @staticmethod
    def get_legref(timeline, fr=0, to=3000, latex=False, label=''):
        image_directive = 'sparklineimg' if latex else 'image'

        legref = ''

        # pylint: disable=no-member
        legref += '\n\n'.join(['.. |T%02d%s| replace::\n' % (x.id, label) +
                               '   :cabin:`%s` |br| :cabin:`%s`'
                               % (x.title, x.period)
                               for x in timeline])
        legref += '\n\n'
        legref += '\n\n'.join([
            '.. |Tmg%02d%s| %s:: %s'
            % (x.id, label, image_directive,
               reverse('sparkline-tlitem',
                       kwargs={'tlid': x.id, 'fr': fr, 'to': to, }))
            for x in timeline])

        legref += '\n\n'
        legref += '\n\n'.join(['.. _T%02d%s: %s' % (x.id, label, x.url)
                               for x in timeline if x.url])
        legref += '\n\n'

        return legref

    @classmethod
    def get_context_data_for_object(cls, obj, latex=False):
        context = {}

        fr = 2110
        to = 1200
        try:
            if obj.father and not obj.father.datedeath\
                    and obj.father.probably_alive:
                to = datetime.date.today().year + 2
            else:
                to = max(to, obj.father.datedeath.year)
        except:
            pass
        try:
            fr = min(fr, obj.father.datebirth.year)
            to = max(to, fr + 80)
        except:
            pass
        try:
            if obj.mother and not obj.mother.datedeath\
                    and obj.mother.probably_alive:
                to = datetime.date.today().year + 2
            else:
                to = max(to, obj.mother.datedeath.year)
        except:
            pass
        try:
            fr = min(fr, obj.mother.datebirth.year)
            to = max(to, fr + 80)
        except:
            pass

        for ch in obj.person_set.all():
            try:
                if not ch.datedeath and ch.probably_alive:
                    to = datetime.date.today().year + 2
                else:
                    to = max(to, ch.datedeath.year)
            except:
                pass

        fr = fr - 10
        context['fr'] = fr
        to = min(max(to + 5, fr + 80), datetime.date.today().year + 2)
        context['to'] = to

        timeline = cls.get_timeline_items(obj.id, fr, to)

        l = ['| |T%02d%04d|%s    | |Tmg%02d%04d|                    |\n'
             % (x.id, obj.id, '_' if x.url else ' ', x.id, obj.id)
             for x in timeline]
        l.append('\n')

        legend = '+---------------+--------------------------------+\n'.join(l)

        context['sparkline_legend'] = legend
        context['sparkline_legend_ref'] = cls.get_legref(
                timeline,
                fr=fr, to=to,
                latex=latex,
                label='%04d' % obj.id)

        context['display_timeline'] = fr != 2100
        return context

    def get_context_data(self, **kwargs):
        context = super(FamilyDetail, self).get_context_data(**kwargs)
        obj = self.get_object()
        context.update(self.get_context_data_for_object(obj))

        # print render_to_string('genealogio/family_detail.rst', context)
        return context


class EventDetail(LoginRequiredMixin, CurrentSiteMixin, DetailView):
    """Display details for a person."""

    model = Event


def get_dict_pedigree(p, total, level=0):
    if level < 0:
        return
    if p is None:
        return ''
    data = {'name': p.get_short_name(),
            'born': p.datebirth.year if p.datebirth else '',
            'died': p.datedeath.year if p.datedeath else '',
            'url': p.get_absolute_url(),
            'urlp': reverse("pedigree", kwargs={"pk": p.id, }),
            'pk': p.pk,
            }
    if total - level > 3:
        data['name'] += ' (%s-%s)' % (data['born'], data['died'])
        data['born'] = ''
        data['died'] = ''
    if level > 0:
        data['parents'] = [get_dict_pedigree(p.get_father(), total, level-1),
                           get_dict_pedigree(p.get_mother(), total, level-1), ]

    return data


class Pedigree(LoginRequiredMixin, View):
    """Display pedigree for a person."""

    def get(self, request, pk, level=3):
        # pylint: disable=no-member
        person = Person.objects.get(pk=pk)

        data = get_dict_pedigree(
                person,
                total=int(level)-1,
                level=int(level)-1)

        return render(request, 'genealogio/pedigree.html',
                      {
                          'person': person,
                          'data': json.dumps(data),
                          'generations': int(level),
                          })


class PedigreePDF(LoginRequiredMixin, View):
    """
    Display simple pedigree page for a person which we can render to PDF via
    phantomjs, in order to include it in a Book.
    """

    def get(self, request, handle, generations):
        # pylint: disable=no-member
        person = Person.objects.get(handle=handle)

        data = get_dict_pedigree(
                person,
                total=int(generations),
                level=int(generations))

        return render(request, 'genealogio/pedigree_pdf.html',
                      {
                          'person': person,
                          'generations': generations,
                          'data': json.dumps(data), })


def p_dict_descendants(person, suffix):
    try:
        return {
            'name' + suffix: person.get_short_name(),
            'born' + suffix:
            person.datebirth.year if person.datebirth else '',
            'died' + suffix:
            person.datedeath.year if person.datedeath else '',
            'url' + suffix: person.get_absolute_url(),
            'urlp' + suffix:
            reverse("descendants", kwargs={"pk": person.id, }),
            'pk' + suffix: person.pk,
            }
    except:
        pass
    return {
        'name' + suffix: person or '',
        'born' + suffix: '',
        'died' + suffix: '',
        'url' + suffix: '',
        'urlp' + suffix: None,
        'pk' + suffix: '',
        }


def get_dict_descendants(p, level=0):
    """Returns a list of dictionaries, one for each family where p is
    father or mother."""

    if level < 0:
        return 1, level, None
    if p is None:
        return 0, 100, {}  # do not decrease level

    data = [p_dict_descendants(p, '1')]
    fams = p.get_children()
    height = 0
    new_level = level

    def add_family(data, family):
        height = 0
        partner, children, _family = family
        data[-1].update(p_dict_descendants(partner, '2'))
        new_level = level

        if level > 0:
            data[-1]['parents'] = []
            for ch in children:
                h, nl, d = get_dict_descendants(ch, level-1)
                height += h
                new_level = min(new_level, nl)
                data[-1]['parents'].extend(d)
            else:
                height += 1
        return height, new_level

    if fams:
        ht, new_level = add_family(data, fams[0])
        height += ht
    for family in fams[1:]:
        # Now handle other families
        # Here, replace name of p by '...'
        data.append(p_dict_descendants('...', '1'))
        ht, nl = add_family(data, family)
        height += ht
        new_level = min(new_level, nl)

    return height+2, new_level, data


class Descendants(LoginRequiredMixin, View):
    """Display descendants of a person."""

    def get(self, request, pk, level=3):
        # pylint: disable=no-member
        person = Person.objects.get(pk=pk)
        height = 0

        if person.get_children():
            height, nl, d = get_dict_descendants(
                    person,
                    level=int(level)-1)
            new_level = min(int(level), nl)
            data = {'parents': d, }
        else:
            data = []
            new_level = int(level)
        # print json.dumps(data, indent=4)

        return render(request, 'genealogio/descendants.html',
                      {'person': person,
                       'height': height * 30,
                       'generations': int(level) - new_level,
                       'data': json.dumps(data), })


class DescendantsPDF(LoginRequiredMixin, View):
    """Display descendants of a person."""

    def get(self, request, handle, generations):
        # pylint: disable=no-member
        person = Person.objects.get(handle=handle)
        height = 0

        if person.get_children():
            height, _, d = get_dict_descendants(person, level=int(generations))
            data = {'parents': d, }
        else:
            data = []
        # print json.dumps(data, indent=4)

        return render(request, 'genealogio/descendants_pdf.html',
                      {'person': person,
                       'height': height * 30,
                       'generations': int(generations),
                       'data': json.dumps(data), })


class Sparkline(LoginRequiredMixin, View):

    """Sparkline view. """

    width = 512
    height = 32

    def get(self, request, fampk=None, pk=None, tlid=None, fr=None, to=None):
        response = HttpResponse(content_type="image/png")
        surface = self.get_image(fampk=fampk, pk=pk, tlid=tlid, fr=fr, to=to)
        surface.write_to_png(response)
        return response

    @classmethod
    def get_image(cls, fampk=None, pk=None, tlid=None,
                  fr=None, to=None, width=None, height=None):
        """
        If pk (== person's id) and fampk (== family's id) are both not None,
        then return sparkline image for that person/family.

        If pk is None but fampk is not None, then return the headline image for
        that family.

        If tlid is not None, then return image for the corresponding timeline
        item.
        """

        width = width or cls.width
        height = height or cls.height

        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                     width, height)

        if pk is not None and fampk is not None:
            # pk is the id of a Person object

            # pylint: disable=no-member
            try:
                person = Person.objects.get(pk=pk)
                if not person.datebirth:
                    # no date of birth known, so just display empty sparkline
                    return surface

                BIRTH_YEAR = person.datebirth.year
                if person.datedeath:
                    DEATH_YEAR = person.datedeath.year
                else:
                    DEATH_YEAR = min(BIRTH_YEAR+120,
                                     datetime.date.today().year)
                # if we do not have a deathdate, check whether it is plausible
                # that this person is still alive
                guess_dead = (
                        not person.datedeath
                        and (not person.probably_alive
                             or BIRTH_YEAR + 120 < datetime.date.today().year))
            except ObjectDoesNotExist:
                person = None
        else:
            person = None

        if fr is not None:
            FROM_YEAR = int(fr)
        elif person:
            FROM_YEAR = person.datebirth.year - 10
        else:
            FROM_YEAR = 1900

        if to is not None:
            TO_YEAR = int(to)
        elif person:
            TO_YEAR = (person.datedeath.year + 10) if person.datedeath\
                    else FROM_YEAR + 100
        else:
            TO_YEAR = 2020

        def year_to_x(year):
            r = width/height *\
                (year - FROM_YEAR) / (TO_YEAR - FROM_YEAR)
            return r

        ctx = cairo.Context(surface)
        ctx.scale(height/1.0, height/1.0)

        def draw_line(f, t, width, rgba=(0, 0, 0)):
            ctx.move_to(f, 0.5)
            ctx.line_to(t, 0.5)
            ctx.set_source_rgba(*rgba)
            ctx.set_line_width(width)
            ctx.stroke()

        if fampk is not None:
            # head or person
            for x in FamilyDetail.get_timeline_items(
                    fampk, FROM_YEAR, TO_YEAR):
                draw_line(year_to_x(x.start-0.2),
                          year_to_x(x.end if x.end > x.start else x.start+0.2),
                          0.3,
                          x.color[:3] + [0.2 if pk is not None else 1, ])

        if pk is None:
            if tlid is None:
                # header line
                for i in range((FROM_YEAR-1)//10 + 1, TO_YEAR//10 + 1):
                    draw_line(year_to_x(i*10),
                              year_to_x(i*10)+0.02,
                              0.2)
                for i in range((FROM_YEAR-1)//100 + 1, TO_YEAR//100 + 1):
                    draw_line(year_to_x(i*100),
                              year_to_x(i*100)+0.06,
                              0.6)
            else:
                # single timeline item

                # pylint: disable=all
                x = TimelineItem.objects.get(id=int(tlid))

                draw_line(year_to_x(x.start-0.2),
                          year_to_x(x.end if x.end > x.start else x.start+0.2),
                          0.3,
                          x.color)

        elif person:
            if not guess_dead:
                # death date is known, or person is alive
                # draw solid life line
                draw_line(year_to_x(BIRTH_YEAR),
                          year_to_x(DEATH_YEAR),
                          0.04)
            else:
                # person is probably dead, but we do not have date of death
                # draw last part of corresponding line dashed
                # LIMIT determines where to switch from solid to dashed
                LIMIT = max(DEATH_YEAR - 20, (BIRTH_YEAR + DEATH_YEAR)/2)

                draw_line(year_to_x(BIRTH_YEAR),
                          year_to_x(LIMIT),
                          0.04)
                ctx.set_dash([0.08, 0.14], 0.04)
                draw_line(year_to_x(LIMIT),
                          year_to_x(DEATH_YEAR),
                          0.04)
                ctx.set_dash([])

            # draw limiter at birth year
            draw_line(year_to_x(BIRTH_YEAR),
                      year_to_x(BIRTH_YEAR)+0.04,
                      0.4)
            if person.datedeath:
                # draw limiter at death year
                draw_line(year_to_x(DEATH_YEAR),
                          year_to_x(DEATH_YEAR)+0.04,
                          0.4)

            for p, c, _f in person.get_children():
                for child in c:
                    if not child.datebirth:
                        continue
                    ctx.set_source_rgb(0, 0, 0)
                    ctx.arc(year_to_x(child.datebirth.year),
                            0.5, 0.1, 0, 2*math.pi)
                    ctx.fill()

            # pylint: disable=no-member
            qs = Family.objects.filter(father=person) |\
                Family.objects.filter(mother=person)
            for f in qs.exclude(start_date='')\
                       .exclude(start_date__isnull=True):
                ctx.rectangle(year_to_x(f.start_date.year)-0.1, 0.4, 0.2, 0.2)
                ctx.set_source_rgb(1, 1, 1)
                ctx.fill()
                ctx.set_line_width(0.04)
                ctx.set_source_rgb(0, 0, 0)
                ctx.rectangle(year_to_x(f.start_date.year)-0.1, 0.4, 0.2, 0.2)
                ctx.stroke()

        return surface


class AddParents(LoginRequiredMixin, FormView):
    template_name = "genealogio/add_parents.html"
    form_class = AddParentForm

    def get_initial(self):
        child = Person.objects.get(pk=self.kwargs['pk'])
        initial = super(AddParents, self).get_initial()
        initial.update({
            'family_for': int(self.kwargs['pk']),
            'family_name': child.last_name,
            'last_name_father': child.last_name,
            'married_name_mother': child.last_name,
            'family_rel_type': Family.MARRIED,
            })
        return initial

    def form_valid(self, form):
        if not self.request.user.userprofile.is_staff_for_site:
            messages.error(self.request, 'Es ist ein Fehler aufgetreten.')
            return HttpResponseRedirect('/')

        family_kwargs = {
                'name': form.cleaned_data['family_name']
                or form.cleaned_data['last_name_father'],
                'family_rel_type': form.cleaned_data['family_rel_type'],
                'start_date': string_to_partialdate(
                    form.cleaned_data['start_date']),
                }

        if (
                form.cleaned_data['last_name_father'] or
                form.cleaned_data['first_name_father']):
            father_kwargs = {
                    'last_name': form.cleaned_data['last_name_father'],
                    'last_name_current': form.cleaned_data['last_name_father'],
                    'first_name': form.cleaned_data['first_name_father'],
                    'datebirth': string_to_partialdate(
                        form.cleaned_data['date_birth_father']),
                    'datedeath': string_to_partialdate(
                        form.cleaned_data['date_death_father']),
                    'gender_type': Person.MALE,
                    'probably_alive': (
                        form.cleaned_data['date_death_father'] == '' and
                        (form.cleaned_data['date_birth_father'] == '' or
                            int(form.cleaned_data['date_birth_father'][:4])
                         >= 1915)),
                    }

            father_kwargs['handle'] = Person.get_handle(**father_kwargs)
            father = Person.objects.create(**father_kwargs)

            site = Site.objects.get_current()
            father.sites.add(site)
            for s in site.siteprofile.neighbor_sites.all():
                father.sites.add(s)

            if form.cleaned_data['last_name_father']:
                Name.objects.create(
                        name=father.last_name,
                        typ=Name.BIRTHNAME,
                        person=father)
            if form.cleaned_data['first_name_father']:
                Name.objects.create(
                        name=father.first_name,
                        typ=Name.FIRSTNAME,
                        person=father)
            family_kwargs['father'] = father

        if (
                form.cleaned_data['last_name_mother'] or
                form.cleaned_data['first_name_mother']):
            mother_kwargs = {
                    'last_name':
                    form.cleaned_data['last_name_mother'] or
                    form.cleaned_data['married_name_mother'],
                    'last_name_current':
                    form.cleaned_data['married_name_mother'] or
                    form.cleaned_data['last_name_mother'],
                    'first_name': form.cleaned_data['first_name_mother'],
                    'datebirth': string_to_partialdate(
                        form.cleaned_data['date_birth_mother']),
                    'datedeath': string_to_partialdate(
                        form.cleaned_data['date_death_mother']),
                    'gender_type': Person.FEMALE,
                    'probably_alive': (
                        form.cleaned_data['date_death_mother'] == '' and
                        (form.cleaned_data['date_birth_mother'] == '' or
                            int(form.cleaned_data['date_birth_mother'][:4])
                         >= 1915)),
                    }

            mother_kwargs['handle'] = Person.get_handle(
                    married_name=form.cleaned_data['married_name_mother'],
                    **mother_kwargs)
            mother = Person.objects.create(**mother_kwargs)

            site = Site.objects.get_current()
            mother.sites.add(site)
            for s in site.siteprofile.neighbor_sites.all():
                mother.sites.add(s)

            if form.cleaned_data['last_name_mother']:
                Name.objects.create(
                        name=form.cleaned_data['last_name_mother'],
                        typ=Name.BIRTHNAME,
                        person=mother)
            if form.cleaned_data['married_name_mother']:
                Name.objects.create(
                        name=form.cleaned_data['married_name_mother'],
                        typ=Name.MARRIEDNAME,
                        person=mother)
            if form.cleaned_data['first_name_mother']:
                Name.objects.create(
                        name=mother.first_name,
                        typ=Name.FIRSTNAME,
                        person=mother)
            family_kwargs['mother'] = mother

        family = Family.objects.create(**family_kwargs)
        site = Site.objects.get_current()
        family.sites.add(site)
        for s in site.siteprofile.neighbor_sites.all():
            family.sites.add(s)

        child = Person.objects.get(pk=form.cleaned_data['family_for'])
        PersonFamily.objects.create(
                person=child,
                family=family,
                child_type=PersonFamily.BIRTH)

        return HttpResponseRedirect(
                reverse('family-detail', kwargs={'pk': family.pk, }))


class AddPersonView(CreateView):

    model = Person

    def save_person(self, form):
        handle = Person.get_handle(
                last_name=form.cleaned_data['last_name'],
                first_name=form.cleaned_data['first_name'],
                married_name=form.cleaned_data['marriedname'],
                datebirth=string_to_partialdate(
                    form.cleaned_data['datebirth']),
                datedeath=string_to_partialdate(
                    form.cleaned_data['datedeath']))
        person = Person.objects.create(
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name']
                or form.cleaned_data['marriedname'],
                last_name_current=form.cleaned_data['marriedname']
                or form.cleaned_data['last_name'],
                probably_alive=(form.cleaned_data['datedeath'] == ''),
                gender_type=form.cleaned_data['gender_type'],
                datebirth=string_to_partialdate(
                    form.cleaned_data['datebirth']),
                datedeath=string_to_partialdate(
                    form.cleaned_data['datedeath']),
                handle=handle
                )

        site = Site.objects.get_current()
        person.sites.add(site)
        for s in site.siteprofile.neighbor_sites.all():
            person.sites.add(s)

        if form.cleaned_data['last_name']:
            Name.objects.create(
                    name=form.cleaned_data['last_name'],
                    typ=Name.BIRTHNAME,
                    person=person)
        if form.cleaned_data['marriedname']:
            Name.objects.create(
                    name=form.cleaned_data['marriedname'],
                    typ=Name.MARRIEDNAME,
                    person=person)
        if form.cleaned_data['first_name']:
            Name.objects.create(
                    name=form.cleaned_data['first_name'],
                    typ=Name.FIRSTNAME,
                    person=person)
        return person

    def get_initial(self):
        initial = super(AddPersonView, self).get_initial()
        initial.update({
            'attach_to': self.kwargs['pk'],
            })

        return initial


class AddChildView(AddPersonView):

    form_class = AddPersonForm

    def form_valid(self, form):
        if not self.request.user.userprofile.is_staff_for_site:
            messages.error(self.request, 'Es ist ein Fehler aufgetreten.')
            return HttpResponseRedirect('/')

        # save person
        person = self.save_person(form)

        family = Family.objects.get(pk=form.cleaned_data['attach_to'])
        PersonFamily.objects.create(
                person=person,
                family=family,
                child_type=PersonFamily.BIRTH)

        return HttpResponseRedirect(
                reverse('person-detail', kwargs={'pk': person.pk, }))

    def get_context_data(self, **kwargs):
        context = super(AddChildView, self).get_context_data(**kwargs)

        f = Family.objects.get(pk=self.kwargs['pk'])
        context.update({
            'info_text':
            'Füge ein Kind zur Familie <b>%s</b> hinzu.' % f
            })

        return context

    def get_initial(self):
        family = Family.objects.get(pk=self.kwargs['pk'])
        last_name = family.name or (
                family.father.last_name if family.father else '')
        initial = super(AddChildView, self).get_initial()
        initial.update({
            'last_name': last_name
            })

        return initial


class AddSpouseView(AddPersonView):

    form_class = AddSpouseForm

    def form_valid(self, form):
        if not self.request.user.userprofile.is_staff_for_site:
            messages.error(self.request, 'Es ist ein Fehler aufgetreten.')
            return HttpResponseRedirect('/')

        p = Person.objects.get(pk=form.cleaned_data['attach_to'])
        form.cleaned_data['gender_type'] =\
            Person.MALE if p.gender_type == Person.FEMALE else Person.FEMALE

        # save person
        spouse = self.save_person(form)

        if p.gender_type == Person.MALE:
            father = p
            mother = spouse
        else:
            father = spouse
            mother = p
        family = Family.objects.create(
                father=father, mother=mother,
                family_rel_type=form.cleaned_data['family_rel_type'],
                name=form.cleaned_data['family_name'],
                start_date=string_to_partialdate(
                    form.cleaned_data['start_date']),
                )
        site = Site.objects.get_current()
        family.sites.add(site)
        for s in site.siteprofile.neighbor_sites.all():
            family.sites.add(s)

        return HttpResponseRedirect(
                reverse('person-detail', kwargs={'pk': spouse.pk, }))

    def get_context_data(self, **kwargs):
        context = super(AddSpouseView, self).get_context_data(**kwargs)

        p = Person.objects.get(pk=self.kwargs['pk'])
        context.update({
            'info_text':
            'Füge den Ehepartner von <b>%s</b> hinzu.' % p
            })

        return context

    def get_initial(self):
        p = Person.objects.get(pk=self.kwargs['pk'])
        initial = super(AddSpouseView, self).get_initial()
        initial.update({
            'family_rel_type': Family.MARRIED,
            })
        if p.gender_type == Person.MALE:
            initial.update({
                'marriedname': p.last_name,
                'family_name': p.last_name
                })
        else:
            try:
                p_marriedname = Name.objects.filter(
                        person=p, typ=Name.MARRIEDNAME)[0].name
                initial.update({
                    'last_name': p_marriedname,
                    })
            except:
                pass

        return initial

