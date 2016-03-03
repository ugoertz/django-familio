.. _personen-chapter:

======================
Personen
======================

Die Personentabelle ist der wichtigste Teil der Datenbank.


--------------------
Schnelles Hinzufügen
--------------------

In Standardfällen lassen sich Personen und Familien direkt über die Links "Kind
hinzufügen" (auf der Seite einer Familie), "Eltern hinzufügen" und "Ehepartner
hinzufügen" (auf der Seite einer Person) hinzufügen.

Der "Eltern hinzufügen"-Link kann nur verwendet werden, wenn weder Vater noch
Mutter schon in der Datenbank eingetragen sind.

Es werden für einige Felder Werte vorgeschlagen (zum Beispiel Nachname des
Vaters/Ehename der Mutter basierend auf dem Nachnamen des Kindes, dessen Eltern
hinzugefügt werden). Diese Werte können natürlich gegebenenfalls vor dem
Abspeichern geändert werden.


-------------------
Personen hinzufügen
-------------------

Wenn man den Link/Button *Person hinzufügen* klickt (analog, wenn man eine
bestehende Person editiert), wird eine Tabelle angezeigt, in der die folgenden
Informationen eingetragen werden können:

.....
Namen
.....

Im ersten Abschnitt werden die Namen der Person eingetragen. Felder für den
Vornamen, den Geburts-(Nach-)namen und den Ehenamen werden direkt angezeigt und
können einfach ausgefüllt (oder leergelassen) werden.

Mit dem Pluszeichen recht in der unteren Zeile des Namensblocks können weitere
Zeilen für Namen hinzugefügt werden.

Die Kategorien, die zurzeit für Namen zur Verfügung stehen, sind *unbekannt*,
*anderer*, *Geburtsname*, *Ehename*, *Angenommener Name*, *Vorname*, *Rufname*,
*Spitzname*, *Pseudonym*, *Familienname*, *Genanntname*, *Titel (vorangestellt)*, *Titel
(nachgestellt)*. Im Moment werden davon *Geburtsname*, *Ehename*, *Vorname*,
*Rufname*, *Spitzname* und die Titel auf der Webseite angezeigt.

Der *Rufname* muss einer der Namen des Vornamens sein und wird dann
unterstrichen dargestellt. Der *Spitzname* wird hinter dem Vornamen in Klammern
angegeben.

Bei den *Titeln* wird unterschieden zwischen Titeln, die vor dem Namen
(*vorangestellt*) geführt werden (z.B. *Sir*, *Prof.*, *Dr.*), und solchen, die
nach dem Namen geführt werden (z.B. *PhD*). Abgesehen von dieser Unterscheidung
sollten alle Titel im selben Eintrag erfasst werden.

Es lassen sich leicht weitere Kategorien hinzufügen, wenn sie benötigt werden.

Mit den Pfeilen ganz rechts lässt sich mit drag-and-drop die Reihenfolge der
Namen ändern.

..........
Geschlecht
..........

Im nächsten Abschnitt kann das Geschlecht eingetragen werden; außerdem die
Information, ob die Person (wahrscheinlich) noch lebt. Beide Informationen
werden aber im Moment nicht verwendet (gute Ideen, wie/wo/ob sie auf der
Webseite auftauchen sollten, bitte weitergeben.)


.....
Daten
.....

Im nächsten Block können Geburts- und Sterbedatum eingetragen werden, in der
Form ``2000-01-01``. Wenn der genaue Tag oder der Monat nicht bekannt sind, kann
ein Teil des Datums (zum Beispiel ``1950-03`` oder ``1900``) eingegeben werden.


................
Zugeordnete Orte
................

Orte, an denen die Person geboren/gestorben ist (voreingestellt), oder gelebt
hat. Gegebenenfalls können weitere Kategorien für Orte hinzugefügt werden.

Zur Eingabe der Orte: Es sollte ein Teil des Ortsnamens eingegeben und dann der
gesuchte Ort **aus der sich öffnenden Liste per Klick ausgewählt werden**. Auf
diese Art und Weise wird der Eintrag mit dem Eintrag des entsprechenden Orts
in der Datenbank verknüpft. Damit stehen dann die Koordinaten und weitere
Informationen zur Verfügung. Wenn einfach nur der komplette Name eingetippt
wird, wird der Ort nicht abgespeichert.

Alle Orte in Deutschland (die nicht sehr klein sind) befinden sich bereits in
der Datenbank. Für Orte, die nicht gefunden werden, muss ein neuer
Datenbankeintrag angelegt werden, siehe :ref:`ort-hinzufuegen`.


.........
Dokumente
.........

Der Person können ein

* Porträt
* Texte
* ein Kommentar

zugeordnet werden.

Das **Porträt** ist ein Bild, das auf der Seite der Person und (verkleinert) in
der Liste aller Personen angezeigt wird. Um das Portrait hinzuzufügen, muss in
der Regel ein neues Bild-Objekt angelegt werden: :ref:`bilder-hinzufuegen`. Dazu
klickt man auf die Lupe und dann rechts oben auf ``Bild hinzufügen``.

**Texte**, die der Person zugeordnet sind, sind :ref:`texte-chapter`, deren
erster Absatz auf der Seite der Person angezeigt wird. Existierende Texte
(:ref:`texte-hinzufuegen`) können hier per Autocomplete ausgewählt werden, indem
ein Teil des Titels eingegeben wird und dann der entsprechende Text aus der sich
öffnenden Liste ausgewählt wird.


Ein **Kommentar** ist eine (kurze) Notiz, für die kein eigener Text angelegt
werden soll. Diese Notiz wird auf der Seite der entsprechenden Person angezeigt,
sie wird aber nicht in der Liste aller Texte aufgeführt. Für die Funktionen des
Editors gilt dasselbe wie für Texte: :ref:`editor`. Insbesondere steht auch hier
die Möglichkeit zur Verfügung, auf andere Objekte zu verlinken, Bilder
einzufügen, ...

........
Familien
........

In diesem Block wird die Zugehörigkeit der Person als Kind einer Familie
definiert (oder, theoretisch, mehrerer Familien: Zum Beispiel einerseits durch
Geburt und andererseits durch Adoption). Die Familie kann per Autocomplete
ausgewählt werden; normalerweise kann sie durch Eingabe des Nachnamens des
Vaters oder der Mutter gefunden werden.

Wenn die entsprechende Fanilie noch nicht angelegt wurde, kann man das durch
Klick auf die Lupe und dann auf ``Familie hinzufügen`` rechts oben tun
- allerdings sollten dazu Vater und Mutter schon als Personen existieren.

Sonst besteht die Möglichkeit, dieses Feld nachträglich auszufüllen, oder die
Person auf der Seite des Familienobjekts als Kind hinzuzufügen, siehe
:ref:`familien-chapter`.

Sollte eine Person zu mehreren Familien gehören, können diese mit den Pfeilen
links per drag-and-drop angeordnet werden. Auf der Seite der Person werden im
Moment einfach der Vater und die Mutter der ersten Familie angezeigt.

..........
Ereignisse
..........

Hier können :ref:`ereignisse-chapter` mit der Person verknüpft werden. Dabei
kann angegeben werden, welche Rolle (zum Beispiel:
Braut/Bräutigam/Trauzeuge/Familienmitglied/...) die Person bei dem Ereignis
innehatte.

.......
Quellen
.......

Im letzten Abschnitt können Quellen für die Informationen zu dieser Person
benannt werden. Dies wird im Moment aber nur rudimentär unterstützt und noch
nicht auf der Webseite selbst abgebildet.


--------------------
Andere Familienbäume
--------------------

Siehe :ref:`familienbaeume-chapter`\ .





