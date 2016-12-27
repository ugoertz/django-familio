# -*- coding: utf8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from random import randint
from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.views.generic import View
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils.html import escape
from django.core.mail import EmailMessage
from django.contrib.sites.models import Site

from .models import Comment
from .forms import CommentForm


class PostComment(LoginRequiredMixin, View):

    EMAIL_TEMPLATE = '''
Hallo %s,

%s hat Deinen Kommentar auf %s beantwortet.

----------------------------------------------------------------------------------
%s
----------------------------------------------------------------------------------


Viele Grüße,

das %s-Team
'''

    def post(self, request):
        data = request.POST.copy()

        # Look up the object we're trying to comment about
        # pylint: disable=no-member
        ctype = data.get("content_type")
        object_pk = data.get("object_pk")
        if ctype is None or object_pk is None:
            return HttpResponseBadRequest(
                    "Missing content_type or object_pk field.")
        try:
            model = apps.get_model(*ctype.split(".", 1))
            target = model._default_manager.using(None).get(pk=object_pk)
        except TypeError:
            return HttpResponseBadRequest(
                "Invalid content_type value: %r" % escape(ctype))
        except AttributeError:
            return HttpResponseBadRequest(
                "The given content-type %r does not resolve to a valid model."
                % escape(ctype))
        except ObjectDoesNotExist:
            return HttpResponseBadRequest(
                "No object matching content-type %r and object PK %r exists."
                % (escape(ctype), escape(object_pk)))
        except (ValueError, ValidationError) as e:
            return HttpResponseBadRequest(
                "Attempting go get content-type" +
                "%r and object PK %r exists raised %s" %
                (escape(ctype), escape(object_pk), e.__class__.__name__))

        # Construct the comment form
        form = CommentForm(target, data=data)

        # Otherwise create the comment
        if form.is_valid():
            comment = Comment(**form.get_comment_create_data())
            comment.author = request.user

            # compute path

            # set random path and save in order to obtain comment id
            # (and prevent violation of path being unique, in case multiple
            # comments are posted at the same time)
            comment.path = [randint(-10000, -1)]
            comment.save()
            parent = form.cleaned_data['parent']
            if parent == '':
                comment.path = [comment.id]
            else:
                node = Comment.objects.get(id=parent)
                # send notification email to author of parent comment
                # (if desired)
                if node.author.userprofile.email_on_comment_answer:
                    site = Site.objects.get_current()
                    EmailMessage(
                            '%s: Dein Kommentar wurde beantwortet'
                            % site.domain,
                            PostComment.EMAIL_TEMPLATE % (
                                node.author.first_name,
                                comment.author.get_full_name(),
                                request.META['HTTP_REFERER'],
                                comment.content,
                                site.domain),
                            settings.DEFAULT_FROM_EMAIL,
                            [node.author.email, ]).send(fail_silently=True)

                comment.path = node.path
                comment.path.append(comment.id)
            comment.save()
        else:
            return HttpResponseBadRequest("Error when posting comment.")

        return HttpResponseRedirect(data['next'])


