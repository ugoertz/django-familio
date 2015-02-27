from __future__ import unicode_literals
from __future__ import absolute_import

from random import randint
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.views.generic import View
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.utils.html import escape
from braces.views import LoginRequiredMixin

from .models import Comment
from .forms import CommentForm


class PostComment(LoginRequiredMixin, View):

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
            model = models.get_model(*ctype.split(".", 1))
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
                comment.path = node.path
                comment.path.append(comment.id)
            comment.save()
        else:
            return HttpResponseBadRequest("Error when posting comment.")

        return HttpResponseRedirect(data['next'])

