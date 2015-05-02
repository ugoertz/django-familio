.. _texte-chapter:

=====
Texte
=====


.. _texte-hinzufuegen:

----------------
Texte hinzufügen
----------------

Wenn ein Text hinzugefügt wird, können die folgenden Felder ausgefüllt werden:

* Titel: Die Überschrift des Textes
* Link: Die Adresse, unter der der Text aufgerufen werden kann. Wird hier
  ``/personen/ulrichgoertz/`` eingetragen, so ist der Text dann unter
  ``http://...unserefamilie.net/n/personen/ulrichgoertz/`` zu finden.
* Text: Der Text selbst, siehe :ref:`editor` für weitere Informationen zum
  Format.
* Veröffentlicht: Der Text ist nur für Redakteure sichtbar, wenn diese Option
  nicht angekreuzt ist. Damit kann man unfertige Texte abspeichern (und selbst
  anschauen, wie diese aussehen würden - Link ``Auf der Webseite anzeigen`` bei
  abgespeicherten Texten), ohne dass die "normalen" Benutzer den Text schon
  sehen könnten.
* Autor(en): Der/die Redakteur/e, die an dem Text maßgeblich mitgearbeitet
  haben. Auswahl per Autocomplete über den Benutzernamen.

.. _bilder:

* Bilder: Hier lassen sich Bilder hinzufügen, die nicht direkt in den Text
  eingebunden sind. Die hier aufgelisteten Bilder werden unter dem Text
  verkleinert angezeigt.

  Dieses Feld lässt sich auch verwenden, um die ID-Nummern von Bildern zu
  finden, die man in den Text selbst einbinden will; siehe
  :ref:`bilder-einbinden`.
* (Quellen): Quellen für diesen Text; bisher nicht wirklich unterstützt.


Es können auch Microsoft-Word-Dateien (im **docx**-Format) und HTML-Dateien
importiert werden: :ref:`Dateien importieren <text_importieren>`


.. _editor:

----------
Editor
----------

Die Texte werden im ReStructuredText-Format formatiert. Dies ist ein relativ gut
lesbares Format, aus dem leicht sowohl Webseiten generiert werden können, als
auch Quelldateien für das Schriftsatzprogramm LaTeX erzeugt werden, die dann in
pdf-Dateien übersetzt werden können.

Außerdem können ohne großen Aufwand :ref:`Links auf Objekte der
Familiendatenbank <links-personen>` (und natürlich :ref:`auf andere Texte
<links-texte>` und auch :ref:`auf externe Webseiten <links-extern>`) eingefügt
werden.

................
ReStructuredText
................

So könnte eine ReStructuredText-formatierte Datei aussehen:

.. code::

  Der Fließtext wird als einfacher Text geschrieben. Absätze
  werden durch Leerzeilen voneinander getrennt. Aufgepasst:
  Zeilen sollten nicht eingerückt werden. (Dies hat eine
  Sonderbedeutung: Mit dem Einrücken kennzeichnet man Zitate;
  ist das gewünscht, so sollte man natürlich Einrücken.)

  Einzelne (oder mehrere) Worte können *kursiv* oder **fett**
  gesetzt werden [#f1]_, oder ``in einer nicht-proportionalen
  Schrift`` (in erster Linie Befehle einer Programmiersprache).

  .. [#f1] Dies ist eine Fußnote.

  * Nicht-nummerierte Listen
  * werden durch ``*`` am Beginn der Zeile
  * formatiert,

  #. Nummerierte Listen erhält man
  #. analog mit ``#.``

     #) durch einrücken und mit einem anderen Symbol
     #) nach dem ``#`` bekommt man
     #) untergeordnete Listen

  #. hier geht die äußere Liste weiter

  .. note::

    Eine Notiz, die besonders vom Text abgesetzt wird, leitet
    man mit ``..  note::`` ein. Der Text, der zur Notiz gehört,
    muss dann eingerückt werden.

  Um Zitate zu setzen, werden die entsprechenden Texte
  einfach eingerückt:

    Dies ist ein Zitat.

    Das gehört auch noch dazu.


Dieser Text liefert dann das folgende Ergebnis (hier in einer anderen
Schriftart):


-----------------------------------------------------------------------

Der Fließtext wird als einfacher Text geschrieben. Absätze werden durch
Leerzeilen voneinander getrennt. Aufgepasst: Zeilen sollten nicht eingerückt
werden. (Dies hat eine Sonderbedeutung: Mit dem Einrücken kennzeichnet man
Zitate; ist das gewünscht, so sollte man natürlich Einrücken.)

Einzelne (oder mehrere) Worte können *kursiv* oder **fett** gesetzt werden
[#f1]_, oder ``in einer nicht-proportionalen Schrift`` (in erster Linie
Befehle einer Programmiersprache).

.. [#f1] Dies ist eine Fußnote.

* Nicht-nummerierte Listen
* werden durch ``*`` am Beginn der Zeile
* formatiert,

#. Nummerierte Listen erhält man
#. analog mit ``#.``

   a. durch Einrücken und mit einem anderen Symbol
   #. nach dem ``#`` bekommt man
   #. untergeordnete Listen

#. hier geht die äußere Liste weiter

.. note::

  Eine Bemerkung, die besonders vom Text abgesetzt wird, leitet man mit ``..
  note::`` ein. Der Text, der zur Bemerkung gehört, muss dann eingerückt werden.

Um Zitate zu setzen, werden die entsprechenden Texte einfach eingerückt:

  Dies ist ein Zitat.

  Das gehört auch noch dazu.

-----------------------------------------------------------------------

.. _gliederung:

**Gliederung**

Der Text kann in Abschnitte gegliedert werden, die jeweils eine Überschrift
haben. Jeder Abschnitt kann in Unterabschnitte gegliedert werden (auch jeweils
mit einer eigenen Überschrift, die dann etwas kleiner gesetzt wird als die
Abschnittsüberschrift). Unterabschnitte können dann noch weiter in
Unterunterabschnitte unterteilt werden, usw.

Der Beginn eines Abschnitts (Unterabschnitts, ...) wird einfach durch seine
Überschrift gekennzeichnet. Die Überschriften von Abschnitten (Unterabschnitten,
etc.) werden "unterstrichen"::

  Dies ist ein neuer Abschnitt
  ----------------------------

Die Unterstreichung muss mindestens ebenso lang sein, wie die Überschrift. Je
nachdem, ob es sich um eine Abschnittsüberschrift, Unterabschnittsüberschrift,
..., handelt, wird ein unterschiedliches Symbol zum Unterstreichen verwendet.
Damit die Texte auch direkt für den pdf-Export verwendet werden können, müssen
für die einzelnen Gliederungsschritte die folgenden Symbole (in derselben
Reihenfolge) verwendet werden::

  Abschnittsüberschrift
  ---------------------

  Unterabschnittsüberschrift
  ~~~~~~~~~~~~~~~~~~~~~~~~~~

  Unterunterabschnittsüberschrift
  ```````````````````````````````

Gegebenenfalls können noch feinere Unterteilungen benutzt werden; die als
nächstes zu verwendenden Symbole zum Unterstreichen wären dann ``.`` und ``:``.

Weitere Informationen:

* http://rest-sphinx-memo.readthedocs.org/en/latest/ReST.html
* http://sphinx-doc.org/rest.html


.. _links-personen:

...............................................
Links zu Personen, Ereignissen, Familien, Orten
...............................................

Objekte aus der Familiendatenbank können über ihr :ref:`handle <handle>`
verlinkt werden. Die allgemeine Form des Links ist dabei (für Personen)

.. code::

  :p:`Linktext handle`

zum Beispiel konkret

.. code::

  :p:`Ulrich P_GoertzUlrich1973_12345`

Der Linktext (*Ulrich* im Beispiel) ist der Text, der auf der Webseite angezeigt
wird und verlinkt ist. Er kann auch aus mehreren Wörtern bestehen (aber keine
Satzzeichen). Am Schluss muss das entsprechende handle angegeben werden. Der
Link verweist dann auf die zugehörige Seite.

Mit ``:p:`` wird ein Link auf eine Personenseite angelegt, mit ``:f:`` auf eine
Familienseite, mit ``:l:`` auf eine Ortsseite (``l`` für *location*), mit ``:e:``
auf eine Ereignisseite. Für Personen gibt es zusätzlich zu ``:p:`` noch die
Variante ``:pd:``, mit der nach dem angegebenen Text in Klammern das Geburts-
und Sterbejahr der Person angefügt werden.

Um das handle des entsprechenden Objekts herauszufinden, kann man entweder auf
der Seite dieser Person etc. schauen - in der Box in der rechten Spalte wird das
handle angezeigt. Es wird auch in der Liste aller Personen (Familien, ...) auf
der Admin-Seite angezeigt. Am einfachsten ist es aber in der Regel, das handle
mit der :ref:`autocomplete-Funktion <autocomplete-editor>` einzufügen.

.. _links-texte:

......................
Links auf andere Texte
......................

Andere Texte können durch Angabe des *relativen Links* verlinkt werden, zum
Beispiel:

.. code::

  siehe auch den Text über `Xyy Zzz </n/personen/xyyzzz/>`__


.. _links-extern:

...........................
Links auf externe Webseiten
...........................

Bei Links auf externe Webseiten gibt man einfach die vollständige URL an:

.. code::

  siehe auch `Xyy Zzz <http://de.wikipedia.org/wiki/xyyzzz/>`__


.. _bilder-einbinden:

................
Bilder einbinden
................

Bilder können folgendermaßen eingebunden werden: ``:i:`id```. Dabei ist ``id``
die Zahl, die dem Bild in der Datenbank zugeordnet ist. Dies ist die Zahl, die
in der Liste der Bilder im Admin-Bereich in eckigen Klammern angezeigt wird. Die
Zahl wird auch für die Bilder angezeigt, die einem Text zugeordnet sind (:ref:`siehe
oben <bilder>`).

Mit ``:i:`` wird das Bild in mittlerer Größe eingebunden. Stattdessen kann man
auch die folgenden Größen verwenden:

* ``:it:`` Thumbnail
* ``:is:`` Small
* ``:im:`` Medium
* ``:ib:`` Big
* ``:il:`` Large


.. _autocomplete-editor:

............
Autocomplete
............

Für :ref:`Links zu Objekten der Familiendatenbank <links-personen>` gibt es eine
autocomplete-Funktion. Dafür gibt man den ersten Teil des Links ein, zum
Beispiel ``:p:\`Ulrich`` und drückt dann ``Ctrl-Space``. Es wird dann eine Liste
von passenden Objekten angezeigt, und durch Klick wird das entsprechende handle
am Ende eingefügt.


.. _text_importieren:

-----------------
Texte importieren
-----------------

Für das Neuerstellen eines Textes kann man eine Datei im docx- (etwa aus
Microsoft Word oder OpenOffice/LibreOffice) oder im HTML-Format importieren.
*Achtung:* Das doc-Format kann nicht verarbeitet werden!

Dazu ruft man die Seite::

  http://www.....unserefamilie.net/admin/notaro/note/import/

auf, gibt den Titel des zu erstellenden Textes und das Format ein, und lädt die
entsprechende Datei vom eigenen Rechner hoch.

In aller Regel wird es notwendig sein, den Text noch einmal durchzuschauen und
nachzubearbeiten, *insbesondere was die* :ref:`Gliederung <gliederung>` *angeht*.

Damit nicht versehentlich eine unfertige Version auf der Webseite erscheint, ist
das *Veröffentlicht?*-Kästchen nach dem Import zunächst einmal nicht angekreuzt.
Wenn man sich sicher ist, dass alles stimmt, kann/muss man das natürlich
ankreuzen und (erneut) abspeichern. (Als Redakteur kann man aber auch
abgespeicherte Texte schon einmal anschauen, wenn die *Veröffentlicht?*-Option
nicht ausgewählt ist. Dazu verwendet man den Link *Auf der Webseite anschauen*
oben rechts. Das kann man sozusagen als Voranschau nutzen, um zu überprüfen, ob
alles richtig formatiert ist.)


--------------------
Andere Familienbäume
--------------------

Siehe :ref:`familienbaeume-chapter`\ .


