from __future__ import absolute_import

from django.utils.encoding import smart_text
from django import template
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from ..models import Comment
from ..forms import CommentForm

register = template.Library()

# to a large extent, this is taken from the django comments app,
# see https://github.com/django/django-contrib-comments
# https://github.com/django/django-contrib-comments/blob/master/LICENSE.txt


class BaseCommentNode(template.Node):
    """
    Base helper class (abstract) for handling the get_comment_* template tags.
    Looks a bit strange, but the subclasses below should make this a bit more
    obvious.
    """

    @classmethod
    def handle_token(cls, parser, token):
        """Class method to parse get_comment_list/count/form and return
        a Node."""
        tokens = token.split_contents()
        if tokens[1] != 'for':
            raise template.TemplateSyntaxError(
                    "Second argument in %r tag must be 'for'" % tokens[0])

        # {% get_whatever for obj as varname %}
        if len(tokens) == 5:
            if tokens[3] != 'as':
                raise template.TemplateSyntaxError(
                        "Third argument in %r must be 'as'" % tokens[0])
            return cls(
                object_expr=parser.compile_filter(tokens[2]),
                as_varname=tokens[4],
            )

        # {% get_whatever for app.model pk as varname %}
        elif len(tokens) == 6:
            if tokens[4] != 'as':
                raise template.TemplateSyntaxError(
                        "Fourth argument in %r must be 'as'" % tokens[0])
            return cls(
                ctype=BaseCommentNode.lookup_content_type(
                    tokens[2],
                    tokens[0]),
                object_pk_expr=parser.compile_filter(tokens[3]),
                as_varname=tokens[5]
            )

        else:
            raise template.TemplateSyntaxError(
                    "%r tag requires 4 or 5 arguments" % tokens[0])

    @staticmethod
    def lookup_content_type(token, tagname):
        try:
            app, model = token.split('.')
            return ContentType.objects.get_by_natural_key(app, model)
        except ValueError:
            raise template.TemplateSyntaxError(
                    "Third argument in %r must be in the format 'app.model'"
                    % tagname)
        except ContentType.DoesNotExist:
            raise template.TemplateSyntaxError(
                    "%r tag has non-existant content-type: '%s.%s'"
                    % (tagname, app, model))

    def __init__(self, ctype=None, object_pk_expr=None,
                 object_expr=None, as_varname=None, comment=None):
        if ctype is None and object_expr is None:
            raise template.TemplateSyntaxError(
                "Comment nodes must be given either a" +
                "literal object or a ctype and object pk.")
        self.comment_model = Comment
        self.as_varname = as_varname
        self.ctype = ctype
        self.object_pk_expr = object_pk_expr
        self.object_expr = object_expr
        self.comment = comment

    def render(self, context):
        qs = self.get_query_set(context)
        context[self.as_varname] =\
            self.get_context_value_from_queryset(context, qs)
        return ''

    def get_query_set(self, context):
        ctype, object_pk = self.get_target_ctype_pk(context)
        if not object_pk:
            return self.comment_model.objects.none()

        qs = self.comment_model.objects.filter(
            content_type=ctype,
            object_pk=smart_text(object_pk),
            site__pk=settings.SITE_ID,
        )

        # The is_public and is_removed fields are implementation details of the
        # built-in comment model's spam filtering system, so they might not
        # be present on a custom comment model subclass. If they exist, we
        # should filter on them.
        field_names = [f.name for f in self.comment_model._meta.fields]
        if 'is_public' in field_names:
            qs = qs.filter(is_public=True)
        if getattr(settings, 'COMMENTS_HIDE_REMOVED', True)\
                and 'is_removed' in field_names:
            qs = qs.filter(is_removed=False)

        return qs

    def get_target_ctype_pk(self, context):
        if self.object_expr:
            try:
                obj = self.object_expr.resolve(context)
            except template.VariableDoesNotExist:
                return None, None
            return ContentType.objects.get_for_model(obj), obj.pk
        else:
            return self.ctype, self.object_pk_expr.resolve(
                    context,
                    ignore_failures=True)

    def get_context_value_from_queryset(self, context, qs):
        """Subclasses should override this."""
        raise NotImplementedError


class CommentFormNode(BaseCommentNode):
    """Insert a form for the comment model into the context."""

    def get_form(self, context):
        obj = self.get_object(context)
        if obj:
            return CommentForm(obj)
        else:
            return None

    def get_object(self, context):
        if self.object_expr:
            try:
                return self.object_expr.resolve(context)
            except template.VariableDoesNotExist:
                return None
        else:
            object_pk = self.object_pk_expr.resolve(context,
                                                    ignore_failures=True)
            return self.ctype.get_object_for_this_type(pk=object_pk)

    def render(self, context):
        context[self.as_varname] = self.get_form(context)
        return ''


@register.tag
def get_comment_form(parser, token):
    """
    Get a (new) form object to post a new comment.
    Syntax::
    {% get_comment_form for [object] as [varname] %}
    {% get_comment_form for [app].[model] [object_id] as [varname] %}
    """

    return CommentFormNode.handle_token(parser, token)


class CommentListNode(BaseCommentNode):
    """Insert a list of comments into the context."""

    def get_context_value_from_queryset(self, context, qs):
        return list(qs)

    def render(self, context):
        super(CommentListNode, self).render(context)
        return '<script type="text/javascript"' +\
               ' src="%sjs/comments.js"></script>' % settings.STATIC_URL


@register.tag
def get_comment_list(parser, token):
    """
    Gets the list of comments for the given params and populates the template
    context with a variable containing that value, whose name is defined by the
    'as' clause.

    Syntax::

        {% get_comment_list for [object] as [varname] %}
        {% get_comment_list for [app].[model] [object_id] as [varname] %}

    Example usage::

        {% get_comment_list for event as comment_list %}
        {% for comment in comment_list %}
            ...
        {% endfor %}
    """

    return CommentListNode.handle_token(parser, token)

