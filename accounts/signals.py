from django.core.mail import send_mail
from django.dispatch import receiver
from django.contrib.sites.models import Site

from userena.contrib.umessages.signals import email_sent


@receiver(email_sent, dispatch_uid="send_email_notification")
def send_email_notification(sender, **kwargs):
    site = Site.objects.get_current()
    msg = kwargs['msg']
    send_mail('Neue Nachricht auf %s' % site.domain,
              msg.body,
              msg.sender.email,
              [user.email for user in msg.recipients.all()
                  if user.userprofile.email_on_message],
              fail_silently=True)

