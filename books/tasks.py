# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals

import json
import os
import os.path
import tempfile

from celery import shared_task, chain, Celery

from django.conf import settings


@shared_task(name="books.create_rst_from_model", queue="pdfexport")
def create_rst(book_id):

    pass

@shared_task(name="books.create_tex_from_rst", queue="pdfexport")
def create_tex(book_id):

    pass

@shared_task(name="books.create_pdf_from_tex", queue="pdfexport")
def create_pdf(book_id):

    pass

@shared_task(name="books.compile_book", queue="pdfexport")
def compile_book(book_id):

    pass
    # chain create_rst, create_tex, create_pdf

