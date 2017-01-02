# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals

import os
import tempfile
from celery import shared_task, chain

from django.conf import settings

from filebrowser.base import FileObject

from .models import Video, Document


@shared_task(
        name="notaro.create_poster",
        queue="video",
        ignore_result=True)
def create_poster(video_id):
    # pylint: disable=no-member
    v = Video.objects.get(id=video_id)
    out = os.path.join(
        settings.FILEBROWSER_DIRECTORY, 'videos', v.directory, 'poster.jpg')
    os.system(
            ('ffmpeg -i {infile} -ss 3 -f image2 -vframes 1 ' +
             '-y {out}').format(
                 infile=v.video.path_full,
                 out=os.path.join(settings.MEDIA_ROOT, out)))
    v.poster = FileObject(out)
    v.save()
    print 'saved poster', v.poster


@shared_task(
        name="notaro.create_video_version",
        queue="video",
        ignore_result=True)
def create_video_version(video_id, fmt):
    # pylint: disable=no-member
    v = Video.objects.get(id=video_id)
    fn = v.video.path_full
    target = os.path.join(
            settings.MEDIA_ROOT, settings.FILEBROWSER_DIRECTORY,
            'videos', v.directory, 'video')

    options = ''
    if fmt == 'ogv':
        options = '-codec:v libtheora -qscale:v 6 ' +\
                  '-codec:a libvorbis -qscale:a 4'
    elif fmt == 'webm':
        options = '-c:v libvpx -crf 6 -b:v 2M -c:a libvorbis'
    elif fmt == 'mp4':
        options = ' '.join([
            '-codec:v libx264 -profile:v main -level 3.0 -preset slow',
            '-crf 22 -movflags faststart',
            '-codec:a aac -b:a 128k',
            ])

    os.system(
            ('ffmpeg -i {fn} -filter:v "scale=min(720\, iw):-2" ' +
             '{options} -y {tgt}.{fmt}').format(
                 fn=fn, options=options, tgt=target, fmt=fmt))


@shared_task(name="notaro.compile_video", queue="video")
def compile_video(video_id):
    s0 = create_poster.si(video_id).set(queue='video')
    s1 = create_video_version.si(video_id, fmt='mp4').set(queue='video')
    s2 = create_video_version.si(video_id, fmt='ogv').set(queue='video')
    s3 = create_video_version.si(video_id, fmt='webm').set(queue='video')
    chain(s0 | s1 | s2 | s3)()


@shared_task(name="notaro.create_document_thumbnail", queue="video")
def create_document_thumbnail(document_id, page):
    # pylint: disable=no-member
    doc = Document.objects.get(pk=document_id)
    fn = doc.doc.path_full.encode('utf8')
    dir = os.path.join(
            settings.MEDIA_ROOT,
            settings.FILEBROWSER_DIRECTORY,
            'documents',
            'thumbnails')
    try:
        os.makedirs(dir)
    except OSError:
        pass

    out = tempfile.NamedTemporaryFile(dir=dir)

    success = os.system(
            b'convert -density 300 -scale x800 ' +
            b'"{fn}[{pg}]" -quality 85 -resize 800x +adjoin {out}.png'.format(
                fn=fn, out=out.name, pg=page-1))
    if success != 0 or not os.path.exists(out.name + '.png'):
        print('An error occurred')
    else:
        doc.image = FileObject(os.path.relpath(
                out.name + '.png', os.path.join(settings.MEDIA_ROOT)))
        doc.save()

