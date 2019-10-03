# -*- coding: utf8 -*-

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver

from pybb.models import Post
from userena.contrib.umessages.models import Message
from userena.contrib.umessages.signals import email_sent


@receiver(email_sent, dispatch_uid="send_email_notification")
def send_email_notification(sender, **kwargs):
    site = Site.objects.get_current()
    msg = kwargs['msg']
    EmailMessage(
            'Neue Nachricht auf %s' % site.domain,
            msg.body,
            '%s/%s <%s>' % (
                msg.sender.get_full_name(),
                site.domain,
                settings.DEFAULT_FROM_EMAIL),
            [user.email for user in msg.recipients.all()
                if user.userprofile.email_on_message],
            reply_to=[msg.sender.email, ]).send(fail_silently=True)


@receiver(post_save, sender=Post)
def notify_topic_subscribers(instance, **kwargs):
    post = instance
    topic = post.topic
    if post != topic.head:
        User = get_user_model()
        admin = User.objects.get(username=settings.ADMIN_USERNAME)
        for user in topic.subscribers.exclude(pk=post.user.pk):
            # get site of the poster
            site = Site.objects.get_current()

            # Is user active at this site? If not, replace by one of the sites
            # of the user
            if site not in user.userprofile.sites.all():
                site = user.userprofile.sites.all()[0]

            # could improve this by using a template instead of a hard-coded
            # message text
            message =\
                'Hallo %s, im Forum ist im Thema %s ' % (user.first_name,
                                                         topic.name) +\
                'von %s ' % post.user.get_full_name() +\
                'ein neuer Beitrag veröffentlicht worden.\n\n' +\
                'Anschauen: https://%s%s\n\nAbo löschen: http://%s%s' % (
                   site.domain,
                   reverse('pybb:topic', kwargs={'pk': topic.pk}) +
                   '?first-unread=1',
                   site.domain,
                   reverse('pybb:delete_subscription', args=[post.topic.id]))
            Message.objects.send_message(admin, [user, ], message)
