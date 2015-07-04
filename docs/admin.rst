
==========================================
Technische Informationen über die Webseite
==========================================

Die Informationen auf dieser Seite dienen (nur) dem Administrator der Webseite
im technischen Sinne. Beschrieben werden die Einrichtung des Servers und die
Einrichtung neuer Familienbäume.


------------------------------
Anforderungen an den Webserver
------------------------------

* Database (requires Postgres, Postgis)::

    root@x1n:~# aptitude install postgresql postgresql-server-dev-9.4 postgis
    root@x1n:~# aptitude install binutils libproj-dev gdal-bin
    root@x1n:~# su - postgres
    postgres@x1n:~$ createdb djfdb
    postgres@x1n:~$ createuser -P djfu

    postgres@x1n:~$ psql
    psql (9.4.1)
    Type "help" for help.

    postgres=# grant all on database djfdb to djfu;
    GRANT

    postgres@x1n:~$ psql djfdb
    psql (9.4.1)
    Type "help" for help.

    djfdb=# CREATE EXTENSION postgis;
    CREATE EXTENSION
    djfdb=# CREATE EXTENSION postgis_topology;
    CREATE EXTENSION

* pip, virtualenv
* ``aptitude install python-dev libffi-dev libcairo2``
* ``pip install -r requirements/production.txt``
* latex: ``aptitude install texlive-full``
* pandoc (zum Importieren von docx/html-Dateien), aktuelle Ubuntu-Pakete auf
  https://github.com/jgm/pandoc/releases

* Apache (o.ä.)
* XSendFile-Modul (für django-transfer)
  Das Modul muss in der VirtualHost-Konfiguration eingeschaltet werden, und es
  muss ein entsprechender Pfad gesetzt werden.

* Dateien ``base/templates/custom_impressum.html``,
  ``base/templates/base/piwik.html`` (web analytics) mit entsprechend
  individualisierten Informationen

-------------------------------------
Einrichtung eines neuen Familienbaums
-------------------------------------

* settings-Datei in ``familio/settings/`` anlegen
* wsgi-Datei in ``familio/`` anlegen
* ``SECRET_KEY`` in ``secrets.json`` hinzufügen
* Apache VirtualHost einrichten; ggfs. CORS-Header anpassen
* Unterverzeichnisse in ``media/`` anlegen (hier ist ``%d`` durch die
  ``SITE_ID`` zu ersetzen)

  * ``%d_uploads/images``
  * ``%d_uploads/documents``
  * ``%d_versions``

  Dann::

    chown -R www-data:www-data media

* Site- und SiteProfile-Objekte anlegen; ggfs. andere SiteProfile-Objekte
  anpassen
* Redakteur(e) anlegen
* Objekte von anderen Familienbäumen kopieren


