from __future__ import absolute_import

from django.contrib import admin

from .models import Comment


class CommentAdmin(admin.ModelAdmin):
    pass

admin.site.register(Comment, CommentAdmin)
