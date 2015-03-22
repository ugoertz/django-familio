.. _pdfexport-chapter

=====================================
Erstellen einer Chronik im pdf-Format
=====================================

*Im Moment wird zum Erstellen einer pdf-Datei direkter Zugriff auf den Server benötigt. Diese Notizen sind nur eine Gedächtnisstütze für den Administrator.  Später soll es den Redakteuren (oder allen Nutzern) ermöglicht werden, nach einigen Vorgaben pdf-Dateien aus dem Datenbestand zu erzeugen.*

-------------------------
Erstellen der rst-Dateien
-------------------------

In ``genealogio.views`` gibt es die Funktion ``create_rst``, die aus einer Liste
von Texten und Datenbank-Objekten (Personen, Familien, Ereignissen) Dateien im
ReStructuredText-Format erzeugt, die von Sphinx dann in LaTeX-Dateien übersetzt
werden können.

Per Voreinstellung werden alle Personen, Familien und Ereignisse des aktuellen
Familienbaums verwendet.

Die Funktion muss im Moment in einer Shell (``./manage.py shell --settings=...``) aufgerufen werden.


---------------------------
Erstellen der LateX-Dateien
---------------------------

Zum Einbinden der Bilddateien benötigt Sphinx Zugriff auf die Django-Datenbank.
Die entsprechende Settings-Datei muss in der Shell (oder durch Eintrag in der
Datei ``pdfexport/conf.py``) angegeben werden::

    export DJANGO_SETTINGS_MODULE=familio.settings.myfamily

Danach wird in ``pdfexport`` Sphinx aufgerufen::

    make latex

Dadurch werden im Verzeichnis ``pdfexport/_build/latex`` die Datei
``chronicle.tex`` erstellt und die benötigen Bilddateien abgelegt.

-----------------------
Erstellen der pdf-Datei
-----------------------

Bevor die LateX-Datei kompiliert werden kann, müssen noch die Bilddateien
vorbereitet werden: Damit sie von xelatex korrekt skaliert werden, müssen mit::

    mogrify -strip *.jpg

die EXIF-Daten gelöscht werden (dafür muss ImageMagick installiert sein).
Außerdem benötigen wir eine modifizierte ``sphinx.sty`-Datei``::

    cp ../../sphinx.sty .

Nun kann mit (gegebenenfalls mehrfachen) Ausführen von::

    xelatex chronicle.tex

die gewünschte pdf-Datei erstellt werden. (Es müssen XeLaTeX und die
Vollkorn-Schrift installiert sein; Ubuntu-Paket ``fonts-vollkorn``.)

