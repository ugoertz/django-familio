# -*- coding: utf8 -*-

"""The models of the books app."""

from collections import defaultdict
import json
import os
import os.path
import re
import shutil
import tempfile
import time

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.db import models
from django.template.loader import render_to_string

from genealogio.models import Event, Family, Person, TimelineItem
from genealogio.views import FamilyDetail
from notaro.models import Note, Source

# In FLAGS, store options for pdf export, such as whether to include the time
# line in a family item. Book, Collection and Item all have a flag field; if
# a flag is not defined for some item, its value is looked up recursively on
# its parents. Each Book instance needs to set default values for all available
# flags.
#
# The flags field is a CharField where the values of the flags is stored as
# a JSON record. Its format is:
#
# Dictionary with
#   KEYS: model name (genealogio.family, notaro.note, etc.)
#   VALUES: Dictionaries with
#       key: name of flag (as defined in global variable FLAG below)
#       value: setting of the flag
#
# In the global variable defined here, we also define the position of the flag
# inside the FlagWidget (a MultiWidget consisting of Checkboxes), and the label
# text which should be shown in the MultiWidget.
FLAGS = {
    'genealogio.family': {
        'include_timeline': {
            'position': 0,
            'label': 'Familie:<br>Zeitstrahl einbinden',
            'default': False,
            },
        'include_grandchildren': {
            'position': 1,
            'label': 'Familie:<br>Enkel auflisten',
            'default': False,
            }
    },
    'genealogio.person': {
        # 'include_map': {
        #     'position': 2,
        #     'label': 'Person:<br>Landkarte einbinden',
        #     'default': False,
        #     },
        'include_places': {
            'position': 3,
            'label': 'Person:<br>Orte auflisten',
            'default': True,
            }
    },
}

FLAGS_FLAT = [(FLAGS[m][o]['position'], m, o) for m in FLAGS for o in FLAGS[m]]
FLAGS_FLAT.sort()  # sort by position


SEPARATORS = '&=-~`.:\'"^_*+#!$%(),/;<>?@[]{|}'


INDEX_TEMPLATE_HEADER = '''
=========================
Unsere Familiengeschichte
=========================

.. toctree::
    :maxdepth: 2

'''

INDEX_TEMPLATE_FOOTER = '\n'


class Collection(models.Model):
    book = models.ForeignKey(
            'Book',
            verbose_name="Zugehöriges Buch", on_delete=models.CASCADE)
    title = models.CharField(
            max_length=50,
            blank=True,
            verbose_name="Titel")
    flags = models.CharField(
            max_length=800,
            blank=True,
            verbose_name="Einstellungen")
    active = models.BooleanField(default=True, verbose_name="Aktiv")

    level = models.IntegerField(default=0)
    parent = models.ForeignKey(
            'Collection',
            blank=True, null=True, on_delete=models.CASCADE)

    position = models.IntegerField(default=0)

    model = models.ForeignKey(
            ContentType,
            blank=True, null=True, on_delete=models.CASCADE)
    order_by = models.CharField(
            max_length=100,
            help_text='Durch Kommata getrennte Datenbank-Felder,'
                      ' nach denen sortiert werden soll.',
            blank=True)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)

    def parents(self):
        if self.level == 0:
            return [self, ]

        # pylint: disable=no-member
        return self.parent.parents() + [self, ]

    def save(self, *args, **kwargs):
        # pylint: disable=no-member
        if self.parent_id and not self.book_id:
            self.book = self.parent.book

        if self.level == 0 and self.parent_id:
            self.level = self.parent.level + 1

        # pylint: disable=no-member
        if self.site_id is None:
            self.site = Site.objects.get_current()

        super(Collection, self).save(*args, **kwargs)

    def delete_children(self):
        """
        Recursively delete everything attached to this collection.
        """

        for item in self.item_set.all():
            item.delete()
        for collection in self.collection_set.all():
            collection.delete_children()
            collection.delete()

    def populate(self, id_dict=None, keep_existing_items=False):
        if not keep_existing_items:
            self.delete_children()

        if self.model:
            # if self.model is set, populate from model
            m = self.model.model_class()
            m_id = ContentType.objects.get_for_model(m).id
            order_by = [
                    x.strip()
                    for x in self.order_by.split(',') if x.strip()]
            qs = m.objects.all()

            if id_dict:
                if m_id in id_dict:
                    qs = qs.filter(id__in=id_dict[m_id])
                else:
                    qs = qs.none()

            if order_by:
                qs = qs.order_by(*order_by)
            for counter, i in enumerate(qs):
                Item.objects.create(
                        parent=self, site=self.site,
                        obj=i, text='', flags='',
                        active=True, position=counter)
        else:
            # populate from db: create "chapters", i.e. sub-collections,
            # one for each relevant db model

            for counter, m in enumerate(
                    [Note, Person, Family, Event, Source, TimelineItem, ]):

                # do not create "empty" chapters
                m_id = ContentType.objects.get_for_model(m).id
                if id_dict and ((m_id not in id_dict) or not id_dict[m_id]):
                    continue

                c = Collection(
                        parent=self,
                        site=self.site,
                        book=self.book,
                        title=m._meta.verbose_name_plural,
                        model=ContentType.objects.get_for_model(m),
                        flags='',
                        order_by='',
                        level=self.level+1,
                        position=counter)
                c.save()
                c.populate(id_dict)

    def get_rst(self):
        """
        Return the ReStructuredText attached to the items of this collection
        as a string.
        """

        header = '%s\n%s\n\n' % (
                self.title, SEPARATORS[self.level]*len(self.title))

        content = '\n\n'.join(
                [item.get_rst() for item in self.item_set.all()] +
                [collection.get_rst()
                    for collection in self.collection_set.all()])
        return header + content + '\n\n'

    def get_gedcom_data(self, data):
        for item in self.item_set.all():
            item.get_gedcom_data(data)
        for collection in self.collection_set.all():
            collection.get_gedcom_data(data)

    def get_flags_json(self, show_source=True):
        d = defaultdict(dict)
        for _, m, o in FLAGS_FLAT:
            d[m][o] = self.get_flag(m, o, show_source=show_source)
        return json.dumps(d)

    def get_flag(self, model, flag, show_source=False):
        """
        Look up the value of the flag specified, in self.flags, and recursively
        in all parents until found.

        If show_source is True, return 'true_by_default'/'false_by_default' for
        flags which are not set in self, but in some parent.
        """

        if self.flags:
            f = json.loads(self.flags)
        else:
            f = {}
        try:
            return f[model][flag]
        except (AttributeError, KeyError):
            # pylint: disable=no-member
            if self.parent:
                f = self.parent.get_flag(model, flag)
            else:
                f = self.book.get_flag(model, flag)
            if show_source:
                return 'true_by_default' if f else 'false_by_default'
            else:
                return f

    def get_absolute_url(self):
        return reverse('collection-detail', kwargs={'pk': self.pk, })

    def __str__(self):
        # pylint: disable=no-member
        return '%s' % (self.title, )

    class Meta:
        ordering = ('position', )
        verbose_name = 'Kollektion'
        verbose_name_plural = 'Kollektionen'


def get_upload_to(instance, filename):
    filename = os.path.basename(filename)

    return os.path.join(
            settings.PDF_DIRECTORY,
            instance.directory,
            'titlepage.pdf')


class Book(models.Model):

    RENDERED = 'RENDERED'

    title = models.CharField(
            max_length=50,
            blank=True,
            verbose_name="Projekttitel")

    description = models.TextField(
            blank=True,
            verbose_name="Kurzbeschreibung")

    public = models.BooleanField(
            default=False,
            verbose_name="Verfügbar für andere Benutzer")
    authors = models.ManyToManyField(
            settings.AUTH_USER_MODEL,
            verbose_name="Autoren")
    site = models.ForeignKey(
            Site,
            verbose_name="Familienbaum", on_delete=models.CASCADE)
    directory = models.CharField(max_length=300, blank=True)
    render_status = models.CharField(
            max_length=800,
            blank=True,
            verbose_name="Status")

    # root collection:
    root = models.ForeignKey(
            Collection, blank=True, null=True,
            related_name='book_root', on_delete=models.CASCADE)

    sphinx_conf = models.TextField(blank=True)
    mogrify_options = models.CharField(max_length=300, blank=True)
    flags = models.CharField(
            max_length=800,
            blank=True,
            verbose_name="Einstellungen")

    titlepage = models.FileField(
            verbose_name="Titelseite",
            max_length=200,
            blank=True, null=True,
            upload_to=get_upload_to)

    def save(self, *args, **kwargs):
        ctr = 0
        while ctr < 5 and not self.directory:
            ctr += 1
            tmpdir = tempfile.mkdtemp(
                    dir=os.path.join(
                        settings.MEDIA_ROOT,
                        'tmp',
                        settings.PDF_DIRECTORY))
            os.chmod(tmpdir, 0o775)
            d = os.path.basename(tmpdir)
            dest = os.path.join(
                    settings.MEDIA_ROOT, settings.PDF_DIRECTORY, d)
            if not os.path.exists(dest):
                os.mkdir(dest)
                os.chmod(dest, 0o775)
                self.directory = d
        if not self.directory:
            # something went wrong
            raise Exception

        # pylint: disable=no-member
        if self.site_id is None:
            self.site = Site.objects.get_current()

        # set default values for flags
        if not self.flags:
            fl = {m: {k: v['default'] for k, v in vdict.items()}
                  for m, vdict in FLAGS.items()}
            self.flags = json.dumps(fl)

        # create root collection
        if not self.root:
            # obtain id
            if not self.id:
                super(Book, self).save()

            self.root = Collection.objects.create(
                    book=self,
                    title=self.title,
                    # Store the Book flags (as set upon creating the book)
                    # here, so that for the root collection the flags are not
                    # displayed as inherited.
                    # In this way, the Book flags are never used after the
                    # creation process.
                    #
                    # FIXME could remove the Book.flags field from the db.
                    flags=self.flags,
                    level=0,
                    site=self.site,
                    position=0)

        super(Book, self).save(*args, **kwargs)

    def populate(self, selector, reference):
        if selector == 'DB':
            self.root.populate()
            return

        refs = []
        if reference:
            # pylint: disable=no-member
            if reference.startswith('P'):
                try:
                    refs = [Person.objects.get(handle=reference), ]
                except ObjectDoesNotExist:
                    pass
            elif reference.startswith('F'):
                try:
                    family = Family.objects.get(handle=reference)
                except ObjectDoesNotExist:
                    pass
                refs = [x for x in [family.father, family.mother] if x]
        if not refs:
            return

        id_dict = defaultdict(set)
        id_dict[ContentType.objects.get_for_model(Person).id] |= set(refs)
        if selector == 'A':
            for p in refs:
                id_dict[ContentType.objects.get_for_model(Person).id] |=\
                        p.ancestors()
        elif selector == 'D':
            id_dict[ContentType.objects.get_for_model(Person).id] |=\
                    refs[0].descendants()
        elif selector == 'AD':
            for p in refs:
                id_dict[ContentType.objects.get_for_model(Person).id] |=\
                        p.ancestors()
            id_dict[ContentType.objects.get_for_model(Person).id] |=\
                refs[0].descendants()

        # add families, notes, sources for these persons:

        # pylint: disable=no-member
        for p in id_dict[ContentType.objects.get_for_model(Person).id]:
            id_dict[ContentType.objects.get_for_model(Family).id] |=\
                set(Family.objects.filter(father=p)) |\
                set(Family.objects.filter(mother=p))
            id_dict[ContentType.objects.get_for_model(Note).id] |=\
                set(p.notes.all())
            id_dict[ContentType.objects.get_for_model(Source).id] |=\
                set(p.sources.all())
        for f in id_dict[ContentType.objects.get_for_model(Family).id]:
            id_dict[ContentType.objects.get_for_model(Note).id] |=\
                set(f.notes.all())
            id_dict[ContentType.objects.get_for_model(Source).id] |=\
                set(f.sources.all())

        # transform the values of id_dict: replace instances by their ids
        for k in id_dict:
            id_dict[k] = [x.id for x in id_dict[k]]

        self.root.populate(id_dict)

    def get_flag(self, model, flag):
        f = json.loads(self.flags)
        return f[model][flag]

    def get_directory_tmp(self):
        """
        Returns the directory where sphinx and xelatex are run.
        """

        return os.path.join(
                settings.MEDIA_ROOT,
                'tmp',
                settings.PDF_DIRECTORY,
                self.directory)

    def get_directory_dest(self):
        """
        Returns the directory where the final zip and pdf will be stored (and
        which is exposed to the user.).
        """

        return os.path.join(
                settings.MEDIA_ROOT,
                settings.PDF_DIRECTORY,
                self.directory)

    def setup_sphinx(self):
        """
        Create sphinx environment in self.get_directory_tmp().
        Write custom conf.py.
        """

        # copy sphinx files ...
        for f in [
                'sphinx.sty',
                'appendix.rst', 'license_custom.rst',
                'Makefile', ]:
            shutil.copy(
                    os.path.join(
                        settings.PROJECT_ROOT,
                        'pdfexport',
                        f),
                    self.get_directory_tmp())

        if not os.path.exists(os.path.join(self.get_directory_tmp(), 'myext')):
            os.mkdir(os.path.join(self.get_directory_tmp(), 'myext'))
        for f in ['myext/__init__.py', 'myext/genealogio.py', ]:
            shutil.copy(
                    os.path.join(
                        settings.PROJECT_ROOT,
                        'pdfexport',
                        f),
                    os.path.join(self.get_directory_tmp(), 'myext'))

    def create_rst(self):
        """
        Write the ReStructuredText for the root collection to chapter?.rst
        files in self.directory. Also create a corresponding index.rst file.
        """

        index = open(os.path.join(self.get_directory_tmp(), 'index.rst'), 'w')
        index.write(INDEX_TEMPLATE_HEADER)

        for counter, collection in enumerate(self.root.collection_set.all()):
            # append line to index.rst
            index.write('    chapter_%d\n' % counter)

            # write chapter?.rst
            chapter = open(os.path.join(
                self.get_directory_tmp(),
                'chapter_%d.rst' % counter), 'w')
            chapter.write(collection.get_rst())
            chapter.write('\n\n.. |br| raw:: html\n\n  <br />\n\n')
            chapter.close()
        index.write(INDEX_TEMPLATE_FOOTER)
        index.close()

        # create conf.py based on self.root.title
        with open(os.path.join(settings.PROJECT_ROOT, 'pdfexport', 'conf.py'))\
                as source:
            with open(os.path.join(self.get_directory_tmp(), 'conf.py'), 'w')\
                    as dest:
                for l in source:
                    if l.find('# TITLE') != -1:
                        dest.write("'%s',\n" % (
                            self.root.title
                            or 'Unsere Familiengeschichte'))
                    elif l.find('# RELEASENAME') != -1:
                        dest.write("'%s',\n"
                                   % Site.objects.get_current().domain)
                    else:
                        dest.write(l)

    def create_tex(self):
        """
        Compile tex file from the *.rst files (which must be created before).
        Also set up things in order to run xelatex.
        """

        shutil.rmtree(
                os.path.join(self.get_directory_tmp(), '_build'),
                ignore_errors=True)
        os.environ['DJANGO_PROJECT_DIR'] = settings.PROJECT_ROOT
        os.environ['DJANGO_SETTINGS_MODULE'] = settings.SETTINGS_PATH
        try:
            # try to run sphinx in virtualenv
            os.system('. %s/bin/activate && cd %s && make latex' %
                      (settings.SPHINX_VIRTUALENV, self.get_directory_tmp()))
        except AttributeError:
            os.system('cd %s && make latex' %
                      (self.get_directory_tmp(), ))
        shutil.copy(
                os.path.join(
                    settings.PROJECT_ROOT, 'pdfexport', 'Makefile-pdf'),
                os.path.join(
                    self.get_directory_tmp(), '_build/latex/Makefile'))

    def create_pdf(self):
        # FIXME set mogrify options, if required
        os.system(
                'cd %s && make pdf'
                % os.path.join(self.get_directory_tmp(), '_build/latex'))
        if self.titlepage:
            shutil.copy(
                    os.path.join(self.get_directory_dest(), 'titlepage.pdf'),
                    os.path.join(self.get_directory_tmp(), '_build/latex'))
            os.system(
                'cd %s '
                % os.path.join(self.get_directory_tmp(), '_build/latex') +
                '&& pdftk A=titlepage.pdf B=chronicle.pdf '
                'cat A B2-end output c.pdf')
            fn = 'c'
        else:
            fn = 'chronicle'

        # create zip file (will include the final pdf ...) (should not be moved
        # to create_tex because we want to have the sphinx.sty file used by
        # xelatex which is copied to the build directory by "make pdf" above.)
        shutil.make_archive(
                os.path.join(self.get_directory_dest(), 'chronik'), 'zip',
                root_dir=os.path.join(self.get_directory_tmp(), '_build'),
                base_dir='latex')

        shutil.copy(
                os.path.join(
                    self.get_directory_tmp(),
                    '_build/latex/%s.pdf' % fn),
                os.path.join(self.get_directory_dest(), 'chronik.pdf'))

    def get_pdf_url(self):
        fn = os.path.join(self.get_directory_dest(), 'chronik.pdf')
        if os.path.exists(fn):
            return settings.MEDIA_URL +\
                '%s/%s/chronik.pdf' % (settings.PDF_DIRECTORY, self.directory)
        return None

    def get_zip_url(self):
        fn = os.path.join(self.get_directory_dest(), 'chronik.zip')
        if os.path.exists(fn):
            return settings.MEDIA_URL +\
                '%s/%s/chronik.zip' % (settings.PDF_DIRECTORY, self.directory)
        return None

    def get_pdf_creation_date(self):
        if not self.get_pdf_url():
            return
        return time.ctime(os.path.getmtime(
            os.path.join(self.get_directory_dest(), 'chronik.pdf')))

    def get_absolute_url(self):
        return reverse('book-detail', kwargs={'pk': self.pk, })

    def __str__(self):
        return '%s. Von %s' % (
                self.title,
                ', '.join([u.get_full_name() for u in self.authors.all()]))

    class Meta:
        verbose_name = 'Buch'
        verbose_name_plural = 'Bücher'


class Item(models.Model):
    parent = models.ForeignKey(Collection, on_delete=models.CASCADE)

    obj_content_type = models.ForeignKey(
            ContentType, blank=True, null=True,
            verbose_name='Typ des zugeordneten Objekts',
            on_delete=models.CASCADE)
    obj_id = models.IntegerField(
            blank=True, null=True,
            verbose_name='Zugeordnetes Objekt')
    obj = GenericForeignKey('obj_content_type', 'obj_id')

    title = models.CharField(max_length=200, blank=True, verbose_name='Titel')
    use_custom_title_in_pdf = models.BooleanField(
            default=False,
            verbose_name="Eigenen Titel im PDF verwenden")

    # TextField to allow editing of the ReST obtained by rendering the template
    # for obj
    text = models.TextField(
            blank=True,
            verbose_name="Eigener Text")

    # allow storing some 'flags' (which might depend on content type of related
    # object), e.g., for Family, whether to include time line
    # JSON formatted
    flags = models.CharField(
            max_length=800,
            blank=True,
            verbose_name="Einstellungen")

    active = models.BooleanField(default=True, verbose_name="Aktiv")
    position = models.IntegerField(default=1)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)

    def get_gedcom_data(self, data):
        if (self.obj_content_type
                == ContentType.objects.get_for_model(Person)):
            data['persons'].add(self.obj)
        elif (self.obj_content_type
                == ContentType.objects.get_for_model(Family)):
            data['families'].add(self.obj)
        elif (self.obj_content_type
                == ContentType.objects.get_for_model(Event)):
            data['events'].add(self.obj)
        elif (self.obj_content_type
                == ContentType.objects.get_for_model(Note)):
            data['notes'].add(self.obj)

    def get_rst(self, force_from_template=False):
        """
        Render the rst template corresponding to this item and store it in
        text.
        """

        if self.text and not force_from_template:
            result = self.text
        elif not self.obj:
            return ''
        else:
            try:
                if not Site.objects.get_current() in self.obj.sites.all():
                    return ''
            except AttributeError:
                # If self.obj has no attribute "sites", then it is available on
                # all sites.
                pass
            context = {
                    'object': self.obj,
                    'latexmode': True,
                    'current_site': Site.objects.get_current(),
                    'itemtitle':
                    self.title if self.use_custom_title_in_pdf else '', }

            if (self.obj_content_type
                    == ContentType.objects.get_for_model(Family)):
                if self.get_flag('genealogio.family', 'include_timeline'):
                    context.update(FamilyDetail.get_context_data_for_object(
                        self.obj, latex=True))
                if not self.get_flag(
                        'genealogio.family', 'include_grandchildren'):
                    context.update({'hide_grandchildren': True, })

            if (self.obj_content_type
                    == ContentType.objects.get_for_model(Person)):
                if not self.get_flag('genealogio.person', 'include_places'):
                    context.update({'hide_places': True, })

                # --- include_map
                # (this is more complicated?!, since we need to start
                # a celery task to get this done...; could return value to the
                # caller of all things that need to be done before proceeeding
                # ...)

            result = render_to_string(
                    "%s/%s_detail.rst" % (
                        self.obj._meta.app_label, self.obj._meta.model_name),
                    context)
            if force_from_template:
                return result

        # Correct headings according to collection level:
        # Replace heading defined by SEPARATORS[i] in result by heading defined
        # by SEPARATORS[i+self.parent.level]
        for i in range(len(SEPARATORS)-self.parent.level-1, -1, -1):
            expr = re.compile('^\\%s{4,}' % SEPARATORS[i], re.MULTILINE)
            result = re.sub(
                    expr,
                    lambda m: SEPARATORS[i+self.parent.level]*len(m.group(0)),
                    result)
        return result

    def set_text_from_template(self):
        self.text = self.get_rst(force_from_template=True)
        self.save()

    def get_flags_json(self, show_source=True):
        d = defaultdict(dict)
        for _, m, o in FLAGS_FLAT:
            d[m][o] = self.get_flag(m, o, show_source=show_source)
        return json.dumps(d)

    def get_flag(self, model, flag, show_source=False):
        """
        Look up the value of the flag specified, in self.flags, and recursively
        in all parents until found.
        """

        if self.flags:
            f = json.loads(self.flags)
        else:
            f = {}
        try:
            return f[model][flag]
        except (AttributeError, KeyError):
            # pylint: disable=no-member
            if self.parent:
                fl = self.parent.get_flag(model, flag)
            else:
                fl = self.book.get_flag(model, flag)
            if show_source:
                return 'true_by_default' if fl else 'false_by_default'
            else:
                return fl

    def get_absolute_url(self):
        return reverse('item-detail', kwargs={'pk': self.pk, })

    def save(self, *args, **kwargs):
        # pylint: disable=no-member
        if self.site_id is None:
            self.site = Site.objects.get_current()

        if not self.title and self.obj:
            self.title = self.obj.__str__()
        super(Item, self).save(*args, **kwargs)

    def __str__(self):
        return '%s: %s' % (
                self.obj_content_type.name if self.obj_content_type else '',
                self.title)

    class Meta:
        ordering = ('position', )
        verbose_name = 'Eintrag'
        verbose_name_plural = 'Einträge'

