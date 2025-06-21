import datetime
import os
import os.path
import shutil
import tempfile

from celery import shared_task, chain

from django.conf import settings
from django.db.models import Q

from genealogio.models import Family, Person
from .models import FamilyTree, FTREE_FOOTER, FTREE_HEADER, GENTREE_HEADER


@shared_task(
        name="familytree.create_pdf",
        queue="pdfexport",
        ignore_result=True)
def create_pdf(familytree_id):

    ft = FamilyTree.objects.get(pk=familytree_id)
    tex = ft.create_tex()

    with open(os.path.join(ft.get_directory_tmp(), 'ft.tex'), 'w') as f:
        f.write(tex)

    os.system('cd %s && lualatex ft.tex' % ft.get_directory_tmp())

    if ft.papersize != 'auto':
        os.system('cd %s && pdfcrop --margins 5 --clip ft.pdf ft1.pdf'
                  % (ft.get_directory_tmp(), )
                  )
        if ft.papersize.startswith('a'):
            resize = ft.papersize
        elif ft.papersize == 'custom':
            resize = "'custom mm %d %d'" % (ft.width, ft.height)
        os.system('cd %s && pdfScale.sh -r %s -s 0.9 ft1.pdf ftree.pdf'
                  % (ft.get_directory_tmp(), resize, )
                  )
        png_from = 'ft1'
        shutil.copy(
            os.path.join(ft.get_directory_tmp(), 'ftree.pdf'),
            ft.get_directory_dest(),
        )
    else:
        png_from = 'ft'
        shutil.copy(
            os.path.join(ft.get_directory_tmp(), 'ft.pdf'),
            os.path.join(ft.get_directory_dest(), 'ftree.pdf')
        )

    # create zip archive
    shutil.make_archive(
        os.path.join(ft.get_directory_dest(), 'ftree'), 'zip',
        root_dir=ft.get_directory_tmp(),
    )

    # create png version
    os.system('cd %s && convert -density 300 %s.pdf -resize 80%% -alpha remove ftree.png'
              % (ft.get_directory_tmp(), png_from, )
              )
    shutil.copy(
        os.path.join(ft.get_directory_tmp(), 'ftree.png'),
        ft.get_directory_dest(),
    )
    os.system('cd %s && convert ftree.png -resize 1200x ftree.png-preview.png'
              % (ft.get_directory_tmp(), )
              )
    dt = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    shutil.copy(
        os.path.join(ft.get_directory_tmp(), 'ftree.png-preview.png'),
        os.path.join(ft.get_directory_dest(), 'ftree.png-%s.png' % dt),
    )

    ft.preview_img = dt
    ft.render_status = FamilyTree.RENDERED
    ft.save()


