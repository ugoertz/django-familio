import os
import os.path
import shutil
import time

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.db import models
from django.db.models import Q
from django.urls import reverse

from books.models import get_tmp_dir
from genealogio.models import Family, Person


# node sizes according to level, without and with foto, resp.
NODE_SIZE = {
    5: (2.5, 6),
    4: (4.5, 8),
    3: (4.5, 8),
    2: (4.5, 8),
    1: (4.5, 8),
    0: (4.5, 8),
    -1: (4.5, 8),
    -2: (3.5, 3.5),
    -3: (3.5, 3.5),
    -4: (3.5, 3.5),
    -5: (3.5, 3.5),
}



FTREE_HEADER = r'''
\documentclass[landscape]{article}
\usepackage[paperheight=%dcm, paperwidth=%dcm, left=2cm, right=2cm, top=1.3cm, bottom=1cm]{geometry}
\usepackage[all]{genealogytree}
\usepackage{mathfont}
\setfont{Vollkorn}
\pagestyle{empty}
\begin{document}
\begin{center}
    \fontsize{%dpt}{%dpt}\selectfont
    %s

\vspace{%dmm}
\begin{tikzpicture}
'''

GENTREE_HEADER = r'''
\genealogytree
    [
    processing=database,
    database format=medium marriage below,
    date format=yyyy,
    level distance=10mm,
    name font=\bfseries,
    surn code={\textcolor{red!50!black}{#1}},
    place text={\newline}{},
    date format=yyyy,
    level size=4.5cm,
    child distance=.3cm,
    further distance=.8cm,
    level 5/.style={
        node size=2.5cm,
        node box={fit basedim=11pt,boxsep=2pt,segmentation style=solid,
            colback=white,
            before upper=\parskip10pt,
            halign=left,before upper=\parskip1pt,
            if image defined={add to width=35mm,right=35mm,
                underlay={\begin{tcbclipinterior}\path[fill overzoom DBimage]
                        ([xshift=-34mm]interior.south east) rectangle (interior.north east);
                \end{tcbclipinterior}},
            }{},
        },
    },
    level 4/.style={
        node size=4.5cm,
        node box={fit basedim=11pt,boxsep=2pt,segmentation style=solid,
            colback=white,
            before upper=\parskip10pt,
            halign=left,before upper=\parskip1pt,
            if image defined={add to width=35mm,right=35mm,
                underlay={\begin{tcbclipinterior}\path[fill overzoom DBimage]
                        ([xshift=-34mm]interior.south east) rectangle (interior.north east);
                \end{tcbclipinterior}},
            }{},
        },
    },
    level 3/.style={
        node size=4.5cm,
        node box={fit basedim=11pt,boxsep=2pt,segmentation style=solid,
            colback=white,
            before upper=\parskip10pt,
            halign=left,before upper=\parskip1pt,
            if image defined={add to width=35mm,right=35mm,
                underlay={\begin{tcbclipinterior}\path[fill overzoom DBimage]
                        ([xshift=-34mm]interior.south east) rectangle (interior.north east);
                \end{tcbclipinterior}},
            }{},
        },
    },
    level 2/.style={
        node size=4.5cm,
        node box={fit basedim=11pt,boxsep=2pt,segmentation style=solid,
            colback=white,
            before upper=\parskip10pt,
            halign=left,before upper=\parskip1pt,
            if image defined={add to width=35mm,right=35mm,
                underlay={\begin{tcbclipinterior}\path[fill overzoom DBimage]
                        ([xshift=-34mm]interior.south east) rectangle (interior.north east);
                \end{tcbclipinterior}},
            }{},
        },
    },
    level 1/.style={
        node size=4.5cm,
        node box={fit basedim=11pt,boxsep=2pt,segmentation style=solid,
            colback=white,
            before upper=\parskip10pt,
            halign=left,before upper=\parskip1pt,
            if image defined={add to width=35mm,right=35mm,
                underlay={\begin{tcbclipinterior}\path[fill overzoom DBimage]
                        ([xshift=-34mm]interior.south east) rectangle (interior.north east);
                \end{tcbclipinterior}},
            }{},
        },
    },
    level 0/.style={
        node size=4.5cm,
        node box={fit basedim=11pt,boxsep=2pt,segmentation style=solid,
            colback=white,
            before upper=\parskip10pt,
            halign=left,before upper=\parskip1pt,
            if image defined={add to width=35mm,right=35mm,
                underlay={\begin{tcbclipinterior}\path[fill overzoom DBimage]
                        ([xshift=-34mm]interior.south east) rectangle (interior.north east);
                \end{tcbclipinterior}},
            }{},
        },
    },
    level -1/.style={
        node size=4.5cm,
        node box={fit basedim=11pt,boxsep=2pt,segmentation style=solid,
            colback=white,
            before upper=\parskip10pt,
            halign=left,before upper=\parskip1pt,
            if image defined={add to width=35mm,right=35mm,
                underlay={\begin{tcbclipinterior}\path[fill overzoom DBimage]
                        ([xshift=-34mm]interior.south east) rectangle (interior.north east);
                \end{tcbclipinterior}},
            }{},
        },
    },
    level -2/.style={
        node size=3.5cm,
        level size=7cm,
        node box={fit basedim=11pt,boxsep=2pt,segmentation style=solid,
            colback=white,
            before upper=\parskip10pt,
            halign=left,before upper=\parskip1pt,
            if image defined={
                underlay={\begin{tcbclipinterior}\path[fill overzoom DBimage]
                        ([yshift=45mm]interior.south west) rectangle (interior.south east);
                \end{tcbclipinterior}},
            }{},
        },
    },
    level -3/.style={
        node size=3.5cm,
        level size=7cm,
        node box={fit basedim=11pt,boxsep=2pt,segmentation style=solid,
            colback=white,
            before upper=\parskip10pt,
            halign=left,before upper=\parskip1pt,
            if image defined={
                underlay={\begin{tcbclipinterior}\path[fill overzoom DBimage]
                        ([yshift=45mm]interior.south west) rectangle (interior.south east);
                \end{tcbclipinterior}},
            }{},
        },
    },
    level -4/.style={
        node size=3.5cm,
        level size=7cm,
        node box={fit basedim=11pt,boxsep=2pt,segmentation style=solid,
            colback=white,
            before upper=\parskip10pt,
            halign=left,before upper=\parskip1pt,
            if image defined={
                underlay={\begin{tcbclipinterior}\path[fill overzoom DBimage]
                        ([yshift=45mm]interior.south west) rectangle (interior.south east);
                \end{tcbclipinterior}},
            }{},
        },
    },
    level -5/.style={
        node size=3.5cm,
        level size=7cm,
        node box={fit basedim=11pt,boxsep=2pt,segmentation style=solid,
            colback=white,
            before upper=\parskip10pt,
            halign=left,before upper=\parskip1pt,
            if image defined={
                underlay={\begin{tcbclipinterior}\path[fill overzoom DBimage]
                        ([yshift=45mm]interior.south west) rectangle (interior.south east);
                \end{tcbclipinterior}},
            }{},
        },
    }, '''

FTREE_FOOTER = r'''
\end{tikzpicture}
\end{center}
\end{document}
'''

FT_TYPE_CHOICES = (
    ('fam_a_d', 'Vorfahren und Nachkommen einer Familie', ),
)

FT_PAPERSIZE_CHOICES = (
    ('auto', 'Automatisch berechnete Länge/Breite'),
    ('a4', 'DIN A4'),
    ('a3', 'DIN A3'),
    ('a2', 'DIN A2'),
    ('a1', 'DIN A1'),
    ('a0', 'DIN A0'),
    ('custom', 'Manuell, Länge/Breite in mm'),
)

class FamilyTree(models.Model):

    RENDERED = 'RENDERED'

    tpe = models.CharField(
        max_length=10, choices=FT_TYPE_CHOICES,
        default='fam_a_d',
        verbose_name='Art des Stammbaums',
    )

    papersize = models.CharField(
        choices=FT_PAPERSIZE_CHOICES, default='a3',
        verbose_name='Papierformat',
    )
    width = models.IntegerField(
        default=0,
        verbose_name='Breite',
        help_text='Nur für Papierformat Manuell',
    )
    height = models.IntegerField(
        default=0,
        verbose_name='Höhe',
        help_text='Nur für Papierformat Manuell',
    )
    resize_image_files = models.IntegerField(
        default=0,
        verbose_name='Bilddateien skalieren?',
        help_text='Breite in Pixeln; 0 = Automatisch anhand Papierformat',
    )
    black_white = models.BooleanField(
        default=False,
        verbose_name='Schwarz/Weiß?',
        help_text='Bilder nach schwarz/weiß konvertieren',
    )

    levels_up = models.IntegerField(default=2, verbose_name='Vorfahren-Ebenen')
    levels_down = models.IntegerField(default=3, verbose_name='Nachkommen-Ebenen')

    obj_content_type = models.ForeignKey(
            ContentType, blank=True, null=True,
            verbose_name='Typ des zugeordneten Objekts',
            on_delete=models.CASCADE)
    obj_id = models.IntegerField(
            blank=True, null=True,
            verbose_name='Zugeordnetes Objekt')
    obj = GenericForeignKey('obj_content_type', 'obj_id')

    title = models.CharField(max_length=200, blank=True, verbose_name='Titel')

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
    preview_img = models.CharField(max_length=15, default='preview', blank=True)

    def save(self, *args, **kwargs):
        if not self.directory:
            self.directory = get_tmp_dir()
            os.mkdir(os.path.join(self.get_directory_tmp(), 'imgs'))

        # pylint: disable=no-member
        if self.site_id is None:
            self.site = Site.objects.get_current()

        super().save(*args, **kwargs)

    def get_directory_tmp(self):
        """
        Returns the directory where lualatex is run.
        """

        return os.path.join(
                settings.MEDIA_ROOT,
                'tmp',
                settings.PDF_DIRECTORY,
                self.directory)

    def person_details(self, person):
        if person is None:
            return '{}\n'

        result = [
            'name={%s}' % person.get_short_name(),
            'birth={%s}{%s}' % (person.year_of_birth, person.placebirth or ''),
            'death={%s}{%s}' % (person.year_of_death, person.placedeath or ''),
        ]

        if person.portrait:
            _, ext = os.path.splitext(person.portrait.image.path)
            fn = '%d%s' % (person.pk, ext)
            shutil.copy(
                os.path.join(settings.MEDIA_ROOT, person.portrait.image.path),
                os.path.join(self.get_directory_tmp(), 'imgs', fn)
            )
            if self.resize_image_files:
                os.system('cd %s && mogrify -resize %d %s'
                          % (os.path.join(self.get_directory_tmp(), 'imgs'),
                             self.resize_image_files,
                             fn,
                             )
                          )
            if self.black_white:
                os.system('cd %s && mogrify -colorspace Gray %s'
                          % (os.path.join(self.get_directory_tmp(), 'imgs'),
                             fn,
                             )
                          )
            result.append('image={imgs/%d%s}' % (person.pk, ext))
        return '{' + ', '.join(result) + '}\n'

    def add_child(self, person, levels):
        result =  ['g ' + self.person_details(person), ]
        width = NODE_SIZE[levels][1 if person.portrait else 0]
        c_width = 0

        fam = Family.objects.filter(Q(father=person) | Q(mother=person))
        for index, family in enumerate(fam):
            if index > 0:
                result.append('union {\n')
            spouse = family.father if family.mother == person else family.mother

            if spouse:
                width += NODE_SIZE[levels][1 if spouse.portrait else 0]
                result.append('p ' + self.person_details(spouse))

            if levels >= -self.levels_down:
                for child in family.get_children():
                    w, tex = self.add_child(child, levels+1)
                    result.append(tex)
                    c_width += w

            if index > 0:
                result.append('}\n')  # close 'union'
        return max(width, c_width), 'child { ' + '\n'.join(result) + '}\n'

    def add_ancestors(self, person, levels):
        if person is None:
            return 0, ''
        result = ['parent { g[tikz={xshift=XSHIFTcm}] %s \n'
                  % self.person_details(person), ]
        if levels < self.levels_up:
            f_width, tex = self.add_ancestors(person.get_father(), levels+1)
            result.append(tex)
            m_width, tex = self.add_ancestors(person.get_mother(), levels+1)
            result.append(tex)
        else:
            f_width, m_width = 0, 0
        result.append('}\n')

        p_width = NODE_SIZE[levels][1 if person.portrait else 0]
        width = max(p_width, f_width + m_width)
        return width, ''.join(result)

    def create_tex(self):
        width = 10

        family = self.obj

        # descendants of the attached family object
        result = [
            GENTREE_HEADER +
            ', insert phantom for childless families' +
            ', insert for childless families level limit=-%d]' % self.levels_down,
            '''{ child {
                g[id=father] %s
                p[id=mother] %s
        ''' % (
            self.person_details(family.father),
            self.person_details(family.mother),
        ), ]
        for child in family.get_children():
            w, tex = self.add_child(child, 1)
            result.append(tex)
            width += w
        result.append('}\n }\n')

        # add ancestors and siblings of father
        # as sandclock graph with father of the original family as proband
        if family.father and self.levels_up:
            grandfather = family.father.get_father()
            grandmother = family.father.get_mother()
            grandfamily = Family.objects.get(father=grandfather, mother=grandmother)
            f_result = [
                GENTREE_HEADER + 'set position=father1 at father]',
                '{ sandclock {\n',
            ]

            # add siblings of father (in this family) to the left
            fc_width = 0
            for child in grandfamily.get_children():
                if child != family.father:
                    f_result.append('c %s\n' % self.person_details(child))
                    fc_width += NODE_SIZE[0][1 if child.portrait else 0]

            # add father and connect with the first genealogytree
            f_result += [
                'child {\n',
                'g[id=father1, phantom*, box={add to width=45mm,right=35mm,left=10mm}] {}\n',
                '}\n',
            ]
            fc_width += NODE_SIZE[0][1 if family.father.portrait else 0]

            ff_width, tex = self.add_ancestors(grandfather, 1)
            f_result.append(tex)
            fm_width, tex = self.add_ancestors(grandmother, 1)
            f_result.append(tex)
            f_result.append('}\n}\n')

            if ff_width + fm_width + 8 > fc_width:
                xshift = int(.5 * (ff_width + fm_width - fc_width) + 6)
            else:
                xshift = 1
            f_result = [x.replace('XSHIFT', str(-xshift)) for x in f_result]

            f_width = max(fc_width, ff_width + fm_width)
            result.extend(f_result)
        else:
            f_width = 10

        # add ancestors and siblings of mother
        # as sandclock graph with mother of the original family as proband
        if family.mother:
            grandfather = family.mother.get_father()
            grandmother = family.mother.get_mother()
            grandfamily = Family.objects.get(father=grandfather, mother=grandmother)
            m_result = [
                GENTREE_HEADER + 'set position=mother1 at mother]',
                '{ sandclock {\n',
            ]

            # add mother and connect with the first genealogytree
            mc_width = 0
            m_result += [
                'child {\n',
                'g[id=mother1, phantom*, box={add to width=45mm,right=35mm,left=10mm}] {}\n',
                '}\n',
            ]
            mc_width += NODE_SIZE[0][1 if family.mother.portrait else 0]

            # add siblings of mother (in this family) to the right
            for child in grandfamily.get_children():
                if child != family.mother:
                    m_result.append('c %s\n' % self.person_details(child))
                    mc_width += NODE_SIZE[0][1 if child.portrait else 0]

            mf_width, tex = self.add_ancestors(grandfather, 1)
            m_result.append(tex)
            mm_width, tex = self.add_ancestors(grandmother, 1)
            m_result.append(tex)
            m_result.append('}\n}\n')

            if mf_width + mm_width + 8 > mc_width:
                xshift = int(.5 * (mf_width + mm_width - mc_width) + 6)
            else:
                xshift = 1
            m_result = [x.replace('XSHIFT', str(xshift)) for x in m_result]
            m_width = max(mc_width, mf_width + mm_width)

            result.extend(m_result)
        else:
            m_width = 10


        width = int(max(.5 * width + 10, f_width) + max(.5 * width + 10, m_width)) + 20
        height = int(6.5 * (self.levels_up + min(self.levels_down, 2) + 1) +
            10 * max(0, self.levels_down-2) + 10)
        fontsize_title = 8 * (self.levels_up + self.levels_down + 1)
        vspace = int(fontsize_title * .5)

        return FTREE_HEADER % (height, width,
                               fontsize_title, fontsize_title,
                               self.title, vspace, ) +\
            ''.join(result) + FTREE_FOOTER

    def get_directory_dest(self):
        """
        Returns the directory where the final zip and pdf will be stored (and
        which is exposed to the user.).
        """

        return os.path.join(
                settings.MEDIA_ROOT,
                settings.PDF_DIRECTORY,
                self.directory)

    def get_url(self, tpe):
        if tpe not in ['pdf', 'zip', 'png', ]:
            return None
        fn = os.path.join(self.get_directory_dest(), 'ftree.' + tpe)
        if os.path.exists(fn):
            return os.path.join(
                settings.MEDIA_URL, settings.PDF_DIRECTORY,
                self.directory, 'ftree.' + tpe
            )
        return None

    def get_pdf_url(self):
        return self.get_url('pdf')

    def get_zip_url(self):
        return self.get_url('zip')

    def get_img_url(self):
        return self.get_url('png')

    def get_pdf_creation_date(self):
        if not self.get_pdf_url():
            return
        return time.ctime(os.path.getmtime(
            os.path.join(self.get_directory_dest(), 'ftree.pdf')))

    def get_absolute_url(self):
        return reverse('ft-detail', kwargs={'pk': self.pk, })

    def __str__(self):
        return '%s. Von %s' % (
                self.title,
                ', '.join([u.get_full_name() for u in self.authors.all()]))

    class Meta:
        verbose_name = 'Stammbaum'
        verbose_name_plural = 'Stammbäume'
