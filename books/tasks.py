# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals

from celery import shared_task, chain

from .models import Book


@shared_task(
        name="books.create_rst_from_model",
        queue="pdfexport",
        ignore_result=True)
def create_rst(book_id):
    b = Book.objects.get(id=book_id)
    b.setup_sphinx()
    b.create_rst()


@shared_task(
        name="books.create_tex_from_rst",
        queue="pdfexport",
        ignore_result=True)
def create_tex(book_id):
    b = Book.objects.get(id=book_id)
    b.create_tex()


@shared_task(
        name="books.create_pdf_from_tex",
        queue="pdfexport",
        ignore_result=True)
def create_pdf(book_id):
    b = Book.objects.get(id=book_id)
    b.create_pdf()
    b = Book.objects.get(id=book_id)
    b.render_status = Book.RENDERED
    b.save()


@shared_task(name="books.compile_book", queue="pdfexport")
def compile_book(book_id):
    b = Book.objects.get(id=book_id)
    s1 = create_rst.si(book_id).set(queue='pdfexport')
    s2 = create_tex.si(book_id).set(queue='pdfexport')
    s3 = create_pdf.si(book_id).set(queue='pdfexport')
    result = chain(s1 | s2 | s3)()
    b.render_status = result.id
    b.save()

