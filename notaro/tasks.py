# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals

import os
from celery import shared_task, chain

from django.conf import settings

from .models import Video


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
    v.poster = out
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

