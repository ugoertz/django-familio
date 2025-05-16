# -*- coding: utf8 -*-

from django.conf import settings
from django.utils.translation import gettext_lazy as _

from grappelli.dashboard import modules, Dashboard


class CustomIndexDashboard(Dashboard):
    """
    Custom index dashboard for www.
    """

    def init_with_context(self, context):

        # append a group for "Administration" & "Applications"
        self.children.append(modules.Group(
            _('Verwaltung der Datenbank'),
            column=1,
            collapsible=True,
            children=[
                modules.AppList(
                    _('Administration'),
                    column=1,
                    collapsible=False,
                    models=('django.contrib.*',),
                ),
                modules.AppList(
                    _('Module'),
                    column=1,
                    css_classes=('collapse closed',),
                    exclude=('django.contrib.*',),
                )
            ]
        ))

        # append another link list module for "support".
        self.children.append(modules.LinkList(
            _('Nützliche Links'),
            column=2,
            children=[
                {
                    'title': _('Text importieren (docx/HTML)'),
                    'url': '/admin/notaro/note/import/',
                    'external': False,
                },
                {
                    'title': _('Hochgeladene Bilder'),
                    'url': '/admin/filebrowser/browse/?&dir=images',
                    'external': False,
                },
                {
                    'title': _('Bilddateien, '
                               'die keinem Bildobjekt zugeordnet sind'),
                    'url': '/notes/unbound-images/',
                    'external': False,
                },
                {
                    'title': _('Hochgeladene Dokumente'),
                    'url': '/admin/filebrowser/browse/?&dir=documents',
                    'external': False,
                },
                {
                    'title': _('Bilder/Dokumente hochladen'),
                    'url': '/admin/notaro/picture/uploadarchive',
                    'external': False,
                },
                {
                    'title': _('Virusscanner'),
                    'url': '/admin/notaro/picture/virusscanall',
                    'external': False,
                },
            ]
        ))

        # append another link list module for "support".
        self.children.append(modules.LinkList(
            _('Dokumentation'),
            column=3,
            children=[
                {
                    'title': _('unserefamilie.net Dokumentation'),
                    'url': settings.DOCUMENTATION_URL,
                    'external': False,
                },
                {
                    'title': _('unserefamilie.net Dokumentation (pdf)'),
                    'url': settings.STATIC_URL + 'dokumentation.pdf',
                    'external': False,
                },
                {
                    'title': _('ReStructuredText Dokumentation'),
                    'url': 'http://sphinx-doc.org/rest.html',
                    'external': True,
                },
            ]
        ))

        # # append a feed module
        # self.children.append(modules.Feed(
        #     _('Latest Django News'),
        #     column=2,
        #     feed_url='http://www.djangoproject.com/rss/weblog/',
        #     limit=5
        # ))

        # append a recent actions module
        self.children.append(modules.RecentActions(
            _('Recent Actions'),
            limit=5,
            collapsible=False,
            column=1,
        ))


