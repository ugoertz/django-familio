======================
Einleitung
======================

Auf der ``unserefamilie.net``-Webseite werden Daten und Informationen rund um
eine (Groß-)Familie gesammelt: Personen, Familienzugehörigkeiten/Abstammung,
Orte usw., und dazu natürlich Texte mit detaillierteren Informationen,
Geschichten und Anekdoten, die sicher den interessantesten Teil der Seite
ausmachen.


Die Webseite besteht grob gesprochen aus zwei Teilen, die miteinander
vernetzt sind, die "Familiendatenbank" und die "Texte/Notizen":

#. Familiendatenbank

  Die "harten Fakten", also die eigentlichen Daten (Namen, Abstammung,
  Geburts-/Sterbedaten, Orte, Ereignisse ...) werden in dieser Datenbank
  gesammelt, und zwar in den folgenden Kategorien:

  * :ref:`personen-chapter` (die wichtigsten Daten zu einer Person:
    Name(n), Geburtsdatum, Geburtsort, ...)
  * :ref:`familien-chapter` (hier werden auch die Abstammungsverhältnisse
    abgebildet)
  * :ref:`orte-chapter`
  * :ref:`ereignisse-chapter` (Zusatzinformationen: Ereignisse im engeren
    (Hochzeit, ...) und im weiteren (Beruf, ...) Sinne)

.. _handle:

Allen diese Objekten (Personen, Familien, Orten, Ereignissen) wird beim Anlegen
ein *handle* zugeordnet, mit dem sie eindeutig identifiziert werden können. Zum
Beispiel hat *Ulrich Görtz* auf ``www.goertz.unserefamilie.net`` das handle
``P_GoertzUlrich1973_57482``.

Personenhandles beginnen mit ``P_``, Familienhandles mit ``F_``, Ereignishandles
mit ``E_`` und Ortshandles mit ``L_`` (*location*).

Das handle wird aus den Informationen (Namen/Daten/...) zusammengebaut, die beim
Anlegen des Objektes schon verfügbar sind. (Wenn Informationen, die eigentlich
verwendet würden, erst später nachgetragen werden, wird das handle aber nicht
noch einmal geändert.)

Wie das handle genau aussieht, ist auch nicht weiter relevant. Wichtig ist nur,
dass jedes Objekt mit seinem handle eindeutig identifzierbar ist. Der "normale"
Besucher der Webseite bekommt das handle nie zu Gesicht.


#. Texte/Notizen

  * :ref:`texte-chapter`
  * :ref:`bilder-chapter`


---------------
Die Admin-Seite
---------------

Die Verwaltungsseite der Webseite, wo neue Objekte angelegt/Objekte geändert und
gelöscht und Texte angelegt und redigiert werden können, erreicht man unter
``http://...unserefamilie.net/admin/``. Um sich dort anzumelden, benötigt man
den *Status als Redakteur* (der von einem *Superuser* freigeschaltet werden kann).

Bei existierenden Objekten befindet sich auch in der Box in der rechten Spalte
(die nur für Redakteure angezeigt wird) ein Link, um direkt das enstprechende
Objekt editieren zu können.


----------------------
Quelltext der Webseite
----------------------

Das zugrundeliegende "Programm" der Webseite wird mit dem
Versionsverwaltungsprogramm Git verwaltet, es kann unter
http://github.com/ugoertz/django-familio/ eingesehen werden (und natürlich
sind auch konkrete Code-Änderungen von Python- und/oder Webentwicklungskundigen
willkommen). Das Programm steht unter einer open-source-Lizenz.

