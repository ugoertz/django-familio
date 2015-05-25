# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals

import json
import os
import os.path
import math
import re
import tempfile
import urllib

from celery import shared_task, chain, Celery

# wrap imports in try/except, so that we can run some of the tasks without
# having mapnik or django available, resp.
try:
    import mapnik
except ImportError:
    pass

try:
    from django.conf import settings
    from filebrowser.base import FileObject
except ImportError:
    # starting this worker outside of django instance, so import
    # settings from working directory and set up Celery.app directly

    # pylint: disable=import-error
    import settings
    app = Celery('familio')
    app.config_from_object(settings)


def xml_vars(style, v):
    """Replace ${name:default} from style with v[name] or 'default'"""
    # Scan all variables in style
    r = re.compile(r'\$\{([a-z0-9_]+)(?::([^}]*))?\}')
    rstyle = ''
    last = 0
    for m in r.finditer(style):
        if m.group(1) in v:
            value = v[m.group(1)]
        elif m.group(2) is not None:
            value = m.group(2)
        else:
            raise Exception('Found required style parameter: ' + m.group(1))
        rstyle = rstyle + style[last:m.start()] + value
        last = m.end()
    if last < len(style):
        rstyle = rstyle + style[last:]
    return rstyle


# dummy class to collect options as properties
class A(object):
    pass


@shared_task(name="maps.create_custom_map", queue="render")
def create_custom_map(geojson, bbox, style=None, ppi=300, size=(170, 0), norotate=False):

    gf, geojsonfilename = tempfile.mkstemp(suffix='.geojson', dir='/tmp')
    with open(geojsonfilename, 'w') as f:
        f.write(geojson)

    # much of the code below is adapted from Nik4
    # https://github.com/Zverik/Nik4 by Ilya Zverev

    p3857 = mapnik.Projection('+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs +over')
    p4326 = mapnik.Projection('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
    transform = mapnik.ProjTransform(p4326, p3857)

    options = A()
    options.bbox = bbox
    options.style = ('%s/%s/%s' % (
            settings.STYLE_PREFIX,
            style or settings.DEFAULT_STYLE,
            'mapnik.xml')).encode('utf-8')
    options.ppi = ppi
    options.size = size
    options.norotate = norotate
    options.vars = {
            'geojsonfilename': geojsonfilename,
            }

    dim_mm = None
    scale = None
    size = None
    bbox = None
    rotate = not options.norotate

    fmt = 'png256'

    # get image size in millimeters
    if options.size:
        dim_mm = options.size

    ppmm = options.ppi / 25.4
    scale_factor = options.ppi / 90.7

    # convert physical size to pixels
    size = [int(round(dim_mm[0] * ppmm)), int(round(dim_mm[1] * ppmm))]

    # scale = options.scale * 0.00028 / scale_factor
    # scale = scale / math.cos(math.radians((options.bbox[3] + options.bbox[1]) / 2))

    if options.bbox:
        bbox = options.bbox
    # all calculations are in EPSG:3857 projection (it's easier)
    if bbox:
        bbox = transform.forward(mapnik.Box2d(*bbox))

    # reading style xml into memory for preprocessing
    with open(options.style, 'r') as style_file:
        style_xml = style_file.read()
    style_path = os.path.dirname(options.style)
    if options.vars is not None:
        style_xml = xml_vars(style_xml, options.vars)

    # for layer processing we need to create the Map object
    m = mapnik.Map(100, 100) # temporary size, will be changed before output
    mapnik.load_map_from_string(m, style_xml, False, style_path)
    m.srs = p3857.params()

    # bbox should be specified by this point
    if not bbox:
        raise Exception('Bounding box was not specified in any way')

    # rotate image to fit bbox better
    # if rotate and size:
    #     portrait = bbox.maxy - bbox.miny > bbox.maxx - bbox.minx
    #     # take into consideration zero values, which mean they should be calculated from bbox
    #     if (size[0] == 0 or size[0] > size[1]) and portrait:
    #         size = [size[1], size[0]]

    if size[1] == 0:
        size[1] = int(round(size[0] / (bbox.maxx - bbox.minx) * (bbox.maxy - bbox.miny)))
    # print bbox.minx, bbox.maxx, bbox.miny, bbox.maxy
    # print size

    if max(size[0], size[1]) > 16384:
        raise Exception('Image size exceeds mapnik limit ({} > {}), use tiles'.format(max(size[0], size[1]), 16384))

    # if options.debug:
    #     print 'scale={}'.format(scale)
    #     print 'scale_factor={}'.format(scale_factor)
    #     print 'size={},{}'.format(size[0], size[1])
    #     print 'bbox={}'.format(bbox)
    #     print 'bbox_wgs84={}'.format(transform.backward(bbox) if bbox else None)
    #     print 'layers=' + ','.join([l.name for l in m.layers if l.active])

    # export image
    m.aspect_fix_mode = mapnik.aspect_fix_mode.GROW_BBOX;
    m.resize(size[0], size[1])
    m.zoom_to_box(bbox)

    outfile, filename = tempfile.mkstemp(
            dir=settings.MAP_DIRECTORY,
            suffix=".png")
    os.fchmod(outfile, 0644)

    im = mapnik.Image(size[0], size[1])
    mapnik.render(m, im, scale_factor)
    im.save(filename.encode('utf-8'), fmt)

    return os.path.basename(filename)


@shared_task(name="maps.save_png", ignore_result=True)
def save_png(filename, map_id):
    # download png file from renderer
    outfile, fn = tempfile.mkstemp(
            dir=os.path.join(
                settings.MEDIA_ROOT,
                settings.FILEBROWSER_DIRECTORY,
                'maps'),
            suffix='.png')
    fn = fn.encode('utf-8')
    urllib.urlretrieve('%s%s' % (settings.MAP_SERVER, filename), fn)

    # store to db

    # need to do this import here, because need to import tasks in models.py
    from .models import CustomMap

    # pylint: disable=no-member
    map = CustomMap.objects.get(id=map_id)

    map.rendered = FileObject(os.path.join(
        settings.FILEBROWSER_DIRECTORY,
        'maps',
        os.path.basename(fn)))
    map.render_status = CustomMap.RENDERED
    map.save()


@shared_task(name="maps.render_map", ignore_result=True)
def render_map(map_id):
    # need to do this import here, because need to import tasks in models.py
    from .models import CustomMap

    # pylint: disable=no-member
    map = CustomMap.objects.get(id=map_id)

    s1 = create_custom_map.s(
            geojson=map.geojson(),
            bbox=map.bbox.extent).set(queue='render')
    s2 = save_png.s(map_id=map_id)

    result = chain(s1 | s2)()
    map.render_status = result.id
    map.save()

