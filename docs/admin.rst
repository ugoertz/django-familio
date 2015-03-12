
==========================================
Technische Informationen über die Webseite
==========================================

Die Informationen auf dieser Seite dienen (nur) dem Administrator der Webseite
im technischen Sinne. Beschrieben werden die Einrichtung des Servers und die
Einrichtung neuer Familienbäume.


------------------------------
Anforderungen an den Webserver
------------------------------

* Apache (o.ä.)
* XSendFile-Modul (für django-transfer)
  Das Modul muss in der VirtualHost-Konfiguration eingeschaltet werden, und es
  muss ein entsprechender Pfad gesetzt werden.
* Postgres, Postgis
* pip, virtualenv
* cairo
* latex



-------------------------------------
Einrichtung eines neuen Familienbaums
-------------------------------------

* settings-Datei in ``familio/settings/`` anlegen
* wsgi-Datei in ``familio/`` anlegen
* ``SECRET_KEY`` in ``secrets.json`` hinzufügen
* Apache VirtualHost einrichten; ggfs. CORS-Header anpassen
* Unterverzeichnisse in ``media/`` anlegen, chown www-data
* Site- und SiteProfile-Objekte anlegen; ggfs. andere SiteProfile-Objekte
  anpassen
* Redakteur(e) anlegen
* Objekte von anderen Familienbäumen kopieren


