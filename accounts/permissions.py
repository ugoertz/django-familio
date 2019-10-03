"""
Extensible permission system for pybbm
"""

from django.db.models import Q

from pybb import defaults, util
from pybb.models import Topic, PollAnswerUser
from pybb.permissions import DefaultPermissionHandler


class CustomPermissionHandler(DefaultPermissionHandler):
    """
    Custom Permission handler for PyBB.

    Inherits from DefaultPermissionHandler.

    Methods starting with `may` are expected to return `True` or `False`,
    whereas methods starting with `filter_*` should filter the queryset they
    receive, and return a new queryset containing only the objects the user is
    allowed to see.

    Activated by setting `settings.PYBB_PERMISSION_HANDLER`.
    """
    #
    # permission checks on categories
    #
    def filter_categories(self, user, qs):
        """ return a queryset with categories `user` is allowed to see """
        if not user.is_authenticated():
            return qs.exclude()
        return qs.filter(hidden=False) if not user.is_staff else qs

    def may_view_category(self, user, category):
        """ return True if `user` may view this category, False if not """
        return user.is_staff or (user.is_authenticated() and not category.hidden)

    #
    # permission checks on forums
    #
    def filter_forums(self, user, qs):
        """ return a queryset with forums `user` is allowed to see """
        return qs.filter(Q(hidden=False) & Q(category__hidden=False)) if not user.is_staff else qs

    def may_view_forum(self, user, forum):
        """ return True if user may view this forum, False if not """
        return (user.is_staff or
                (user.is_authenticated() and forum.hidden == False and 
                 forum.category.hidden == False))

    def may_create_topic(self, user, forum):
        """ return True if `user` is allowed to create a new topic in `forum` """
        return user.is_authenticated() and user.has_perm('pybb.add_post')

    #
    # permission checks on topics
    #
    def filter_topics(self, user, qs):
        """ return a queryset with topics `user` is allowed to see """
        if not user.is_staff:
            qs = qs.filter(Q(forum__hidden=False) & Q(forum__category__hidden=False))
        if not user.is_superuser:
            if user.is_authenticated():
                qs = qs.filter(Q(forum__moderators=user) | Q(user=user) | Q(on_moderation=False)).distinct()
            else:
                qs = qs.filter(on_moderation=False)
        return qs

    def may_view_topic(self, user, topic):
        """ return True if user may view this topic, False otherwise """
        if not user.is_authenticated():
            return False
        if user.is_superuser:
            return True
        if not user.is_staff and (topic.forum.hidden or topic.forum.category.hidden):
            return False  # only staff may see hidden forum / category
        if topic.on_moderation:
            return user.is_authenticated() and (user == topic.user or user in topic.forum.moderators)
        return True

    def may_vote_in_topic(self, user, topic):
        """ return True if `user` may vote in `topic` """
        return (
            user.is_authenticated() and topic.poll_type != Topic.POLL_TYPE_NONE and not topic.closed and
            not PollAnswerUser.objects.filter(poll_answer__topic=topic, user=user).exists()
        )

    def may_create_post(self, user, topic):
        """ return True if `user` is allowed to create a new post in `topic` """

        if topic.forum.hidden and (not user.is_staff):
            # if topic is hidden, only staff may post
            return False

        if topic.closed and (not user.is_superuser):
            # if topic is closed, only staff may post
            return False

        # only user which have 'pybb.add_post' permission may post
        return (defaults.PYBB_ENABLE_ANONYMOUS_POST or
                (user.is_authenticated() and user.has_perm('pybb.add_post')))

    def may_post_as_admin(self, user):
        """ return True if `user` may post as admin """
        return user.is_superuser

    #
    # permission checks on posts
    #
    def filter_posts(self, user, qs):
        """ return a queryset with posts `user` is allowed to see """

        # first filter by topic availability
        if not user.is_superuser:
            qs = qs.filter(Q(topic__forum__hidden=False) & Q(topic__forum__category__hidden=False))

        if not defaults.PYBB_PREMODERATION or user.is_superuser:
            # superuser may see all posts, also if premoderation is turned off moderation
            # flag is ignored
            return qs
        elif user.is_authenticated():
            # post is visible if user is author, post is not on moderation, or user is moderator
            # for this forum
            qs = qs.filter(Q(user=user) | Q(on_moderation=False) | Q(topic__forum__moderators=user))
        else:
            # anonymous user may not see posts which are on moderation
            qs = qs.filter(on_moderation=False)
        return qs

    def may_view_post(self, user, post):
        """ return True if `user` may view `post`, False otherwise """
        if not user.is_authenticated():
            return False
        if user.is_superuser:
            return True
        if post.on_moderation:
            return post.user == user or user in post.topic.forum.moderators.all()
        return True

    def may_edit_post(self, user, post):
        """ return True if `user` may edit `post` """
        return user.is_superuser or post.user == user or self.may_moderate_topic(user, post.topic)

    def may_delete_post(self, user, post):
        """ return True if `user` may delete `post` """
        return self.may_moderate_topic(user, post.topic)

    #
    # permission checks on users
    #
    def may_block_user(self, user, user_to_block):
        """ return True if `user` may block `user_to_block` """
        return user.has_perm('pybb.block_users')

    def may_attach_files(self, user):
        """
        return True if `user` may attach files to posts, False otherwise.
        By default controlled by PYBB_ATTACHMENT_ENABLE setting
        """
        return defaults.PYBB_ATTACHMENT_ENABLE and user.is_authenticated()

    def may_create_poll(self, user):
        """
        return True if `user` may attach files to posts, False otherwise.
        By default always True
        """
        return user.is_authenticated()


