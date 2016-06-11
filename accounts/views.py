# -*- coding: utf8 -*-

from __future__ import unicode_literals

from django.views.generic import View
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.core.mail import EmailMessage
from django.contrib.sites.models import Site
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.hashers import make_password
from braces.views import LoginRequiredMixin
from userena.models import UserenaSignup
from userena.contrib.umessages.models import Message

from .forms import InviteForm, AcceptInviteForm


INVITATION_EMAIL = '''\
Hallo,

wir sind dabei, eine Familienchronik unserer (Groß)-Familie anzulegen.
Vielleicht hast Du Lust, es Dir mal anzuschauen oder sogar mitzumachen?

Die Chronik befindet sich auf der Webseite
https://%s

Damit die Inhalte nicht öffentlich zugänglich sind, muss man einen
Benutzeraccount anlegen, um auf die Seite zugreifen zu können. Wenn Du auf den
folgenden Link klickst, kannst Du Dich registrieren:

https://%s/accounts/register/%s/

Dieser Link ist für Dich personalisiert. Du kannst aber gerne weitere Personen
einladen, nachdem Du Dich selbst angemeldet hast. Gehe dazu nach Deiner
Anmeldung auf
https://%s/accounts/invite/


Viele Grüße

%s
'''


WELCOME_MESSAGE = '''\
Hallo %s,

schön, dass Du Dich hier angemeldet hast. Am besten ist es sicher, wenn Du Dir
einfach die Webseite mal anschaust: Neben den Links auf der Hauptseite findest
Du auch in der Menüzeile oben einige Links, die Du ausprobieren kannst, und die
Suchfunktion.

Besonders freuen wir uns über Kommentare zu den Einträgen auf der Webseite
- vielleicht fällt Dir ja zu der einen oder anderen Person oder Familie eine
Erinnerung/Anekdote/Geschichte ein, die Du gerne teilen magst.

Wenn Dir Fehler auffallen, oder Du Daten und Informationen ergänzen kannst, sei
es zu Personen, die schon einen Eintrag haben, oder zu solchen, die noch gar
nicht eingetragen sind, dann nutze doch bitte auch die Kommentarfunktion, oder
schreibe eine Direktnachricht oder eine Email an einen der Redakteure, siehe
http://%s/impressum/

Du kannst gerne auch noch weitere Familienmitglieder auf die Webseite einladen.
Gehe dazu einfach auf
https://%s/accounts/invite/

Wenn Du noch Fragen hast oder es Probleme gibt, kannst Du einfach auf diese
Nachricht antworten oder mir eine Email schreiben.

Viele Grüße

%s (%s)
'''


class InviteView(LoginRequiredMixin, View):

    def get(self, request):
        site = Site.objects.get_current()
        form = InviteForm(initial={
            'message': INVITATION_EMAIL % (
                site.domain,
                site.domain,
                'AKTIVIERUNGCODE',
                site.domain,
                request.user.first_name
                ),
            })
        return render(request, "accounts/invite.html",
                      {'form': form, })

    def post(self, request):
        form = InviteForm(request.POST)
        if form.is_valid():
            # create UserenaSignup object (this automatically
            # creates a new User)

            # for now, install unusable password
            password = make_password(None)
            new_user = UserenaSignup.objects.create_user(
                    # as a start, use email as username
                    form.cleaned_data['email'],
                    form.cleaned_data['email'],
                    password,
                    active=False,
                    send_email=False)
            new_user.first_name = form.cleaned_data['first_name']
            new_user.last_name = form.cleaned_data['last_name']
            new_user.save()

            # send out invitation email
            # pylint: disable=no-member
            site = Site.objects.get_current()
            email_text = form.cleaned_data['message'].replace(
                    'AKTIVIERUNGCODE',
                    UserenaSignup.objects.get(user=new_user).activation_key, )
            EmailMessage(
                    'Einladung von %s' % site.domain,
                    email_text,
                    '%s/%s <%s>' % (
                        request.user.get_full_name(),
                        site.domain,
                        settings.DEFAULT_FROM_EMAIL),
                    [form.cleaned_data['email'], ],
                    reply_to=[request.user.email, ]).send(fail_silently=True)

            messages.success(request,
                             "Die Einladungsemail wurde verschickt." +
                             " Du kannst nun noch jemanden einladen.")

            return HttpResponseRedirect(reverse("send-invitation"))
        else:
            return render(request, "accounts/invite.html",
                          {'form': form, })


class AcceptInvitationView(View):

    def get(self, request, key):
        # check activation key
        # pylint: disable=no-member
        try:
            us = UserenaSignup.objects.get(activation_key=key)
        except:
            messages.error(request, 'Es ist ein Fehler aufgetreten.')
            return HttpResponseRedirect('/')

        form = AcceptInviteForm(initial={
            'email': us.user.email,
            'first_name': us.user.first_name,
            'last_name': us.user.last_name,
            })
        return render(request, "accounts/accept.html",
                      {'form': form, })

    def post(self, request, key):
        form = AcceptInviteForm(request.POST)
        if not form.is_valid():
            return render(request, "accounts/accept.html",
                          {'form': form, })

        # pylint: disable=no-member
        try:
            user = UserenaSignup.objects.activate_user(key)
            if user:
                user.username = form.cleaned_data['username']
                user.email = form.cleaned_data['email']
                user.password = make_password(form.cleaned_data['password1'])
                user.first_name = form.cleaned_data['first_name']
                user.last_name = form.cleaned_data['last_name']
                user.save()

                #  send welcome message
                User = get_user_model()
                admin = User.objects.get(username=settings.ADMIN_USERNAME)
                site = Site.objects.get_current()
                Message.objects.send_message(
                        admin,
                        [user, ],
                        WELCOME_MESSAGE % (
                            user.first_name,
                            site.domain,
                            site.domain,
                            admin.first_name,
                            admin.email))

                # log out old user
                if request.user.is_authenticated():
                    logout(request)

                # Sign the user in.
                auth_user = authenticate(identification=user.email,
                                         check_password=False)
                login(request, auth_user)
                messages.success(request,
                                 "Dein Account wurde aktiviert und " +
                                 "Du bist angemeldet worden.")
                return HttpResponseRedirect('/')

        except:
            messages.error(request, 'Es ist ein Fehler aufgetreten.')
            return HttpResponseRedirect('/')


