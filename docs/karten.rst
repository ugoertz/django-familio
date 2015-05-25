
.. _karten-chapter:

======================
Karten
======================


*Achtung: Das Erstellen von eigenen Karten ist an einigen Stellen noch ein
bisschen provisorisch. Bitte melden, wenn etwas nicht so klappt, wie es sollte
bzw. wie es hier beschrieben ist, oder wenn die Beschreibung unverständlich
ist!*

Man kann *eigene Landkarten* erstellen, die dann in Texte eingebunden werden
können. Im Moment heißt das: man kann einen Kartenausschnitt festlegen, und dann
einzelne Punkte auf der Karte mit Buchstaben markieren.

Demnächst soll diese Funktion noch so erweitert werden, dass man zwischen
verschiedenen Stilen der Karte auswählen kann, und auch die Label stärker
individuell anpassen kann (zum Beispiel: unterschiedliche Farben).


-------------------
Anlegen einer Karte
-------------------

Zum Anlegen einer Karte (im Verwaltungsbereich, Eigene Landkarte hinzufügen)
müssen die folgenden Felder ausgefüllt werden:

**Titel**
    Der Titel der Karte

**Beschreibung**
    Eine ausführlichere Beschreibung bzw. einfach ein zusätzlicher Text. Der
    Text kann mit :ref:`ReStructuredText <restructuredtext>` formattiert werden, und
    es können Objekte der Datenbank :ref:`verlinkt <links-personen>` werden.

**Gerenderte Karte aktualisieren**
    Wenn diese Option gewählt ist, dann wird aus den eingegebenen Daten die Karte
    neu "gezeichnet", d.h., es wird eine Bilddatei erstellt (die Karte
    "gerendert"), die dann in die Webseiten und den pdf-Export eingebunden
    werden kann. *Dieser Prozess ist sehr rechenaufwendig und dauert
    typischerweise mehrere Minuten. Je nachdem, wie groß der Kartenausschnitt
    ist, kann es auch eine halbe Stunde oder mehr dauern.* Die Berechnung läuft
    im Hintergrund und stört den normalen Serverbetrieb nicht, aber es dauert
    eben, bis das Ergebnis angesehen werden kann, und es ist nicht sinnvoll,
    einen neuen Render-Prozess anzustoßen, wenn ein anderer noch läuft (es ist
    nicht garantiert, welcher der Prozesse als letzter beendet wird und damit
    das vorherige Ergebnis überschreibt).

    Deshalb empfiehlt es sich, nach Änderungen eine "Vorkontrolle" vorzunehmen.
    Auf der Detail-Seite der Karte, die man mit dem Link *Auf der Webseite
    anzeigen* erreicht, wird in jedem Fall eine interaktive Karte mit dem
    jeweiligen Ausschnitt angezeigt, auf der auch die angegebenen Markierungen
    dargestellt sind. Daran kann man schon einmal abschätzen, ob alles so
    aussieht, wie gewünscht.

    Wenn die Karte bereits gerendert wurde, und nur Änderungen vorgenommen
    wurden, die die grafische Darstellung nicht beeinflussen
    (Titel/Beschreibung/Beschreibungen der Markierungen), ist ein erneutes
    Rendern natürlich auch nicht erforderlich.

**Begrenzung**
    In diesem Feld wird festgelegt, welchen Ausschnitt die Karte zeigt: Auf der
    Karte wird ein Polygon markiert, und die Karte zeigt am Ende den kleinsten
    rechteckigen Ausschnitt, der dieses Polygon enthält.

    In der linken oberen Ecke sind die Icons (Plus/Minus), mit denen man in die
    Karte hinein- und herauszoomen kann.

    In der rechten oberen Ecke der Karte befinden sich drei Icons, mit denen der
    Editiermodus eingestellt wird: Mit dem rechten Icon (Hand) kann die Karte
    verschoben werden, ohne das markierte Polygon zu ändern. Mit dem mittleren
    Icon kann ein Polygon angelegt werden. Dazu klickt man einfach nacheinander
    mehrere Punkte an. Man schließt das Polygon, *indem man den letzten zu
    markierenden Punkt per Doppelklick anklickt.* Ist das linke Icon angewählt,
    so kann man das Polygon durch Verschieben seiner Eckpunkte verändern.

    Wenn gewünscht, so kann man mit den Link direkt unter der Karte das Polygon
    ganz wieder löschen und von vorne beginnen.

**Markierungen**
    Hier können die Punkte definiert werden, die auf der Karte besonders
    markiert werden sollen (zurzeit durch einen dicken schwarzen Punkt mit einem
    weißen Buchstaben (oder anderem Zeichen) darin). Dazu muss zunächst der Ort
    ausgewählt werden, an dem sich die Markierung befinden soll. Mit
    Autocomplete kann hier ein Ort aus der Ortsdatenbank ausgewählt werden (wie
    bei der Angabe von Geburts- und andern Orten). Die meisten ortschaften in
    Deutschland sind schon vorhanden. Es können aber nach Klick auf die Lupe
    auch neue Orte hinzugefügt werden (Link *Ort hinzufügen* oben rechts); das
    ist besonders dann notwendig, wenn die Karte einen großen Maßstab hat und
    einzelne Häuser o.ä. markiert werden sollen.

    Unter Label wird der Buchstabe angegeben, der auf der Karte an der
    entsprechenden Stelle erscheinen soll.

    Als Beschreibung kann ein kurzer Text angegeben werden, der in der Legende
    der Karte gezeigt wird. Wird hier kein Text eingegeben, so wird in die
    Legende der Titel des entsprechenden Orts aufgenommen. Wenn als Beschreibung
    einer Markierung ``-`` (nur ein Bindestrich) angegeben wird, dann wird diese
    Markierung nicht in der Legende aufgeführt.

    Wenn auf einen Ort aus der Datenbank zurückgegriffen wird, sind die
    Koordinaten (Längen-, Breitengrad) ja schon in der Datenbank vorhanden. Es
    kann aber passieren, dass der Label in der Karte trotzdem nicht perfekt
    platziert ist, zum Beispiel, wenn er den Ortsnamen teilweise verdeckt. Für
    diesen Fall kann der Label mit den Positionskorrektur-Feldern auf der Karte
    ein bisschen verschoben werden (X = Längengrad, Y = Breitengrad, jeweils als
    Fließkommazahl anzugeben). (In Nordrhein-Westfalen entspricht 1 Längengrad
    ca. 70km, 1 Breitengrad ca. 110 km.)

    Mit dem Stil-Feld wird es demnächst möglich sein, die Label-Gestaltung zu
    beinflussen (Farben, Schriftart, Größe, ...). *Im Moment funktioniert das
    leider noch nicht.*


......
Status
......

In der Liste der Karten im Verwaltungsbereich und in der Detail-Seite der Karte
wird der Bearbeitungsstatus angezeigt:

NOTRENDERED
    Für die Karte wurde bisher keine Bilddatei erstellt (die Karte wurde noch
    nicht "gerendert").

RENDERED
    Eine Bilddatei für die Karte ist fertig erstellt und steht zur Verfügung.

ID des Render-Prozesses
    Wird die Karte im Moment gerendert (das dauert, je nach Kartenausschnitt,
    mehrere Minuten), so wird die Bezeichnung des entsprechenden Prozesses
    angezeigt, zum Beispiel ``c317fadf-9514-4904-87d8-720706e32e98``.

Wenn man eine Karte mit angewählter "Aktualisieren"-Option mit "Sichern"
abspeichert, so dass man direkt zur Liste der Karten weitergeleitet wird, kann
es passieren, dass dort die Prozess-ID noch nicht vorhanden ist (sondern
NOTRENDERED oder RENDERED) angezeigt wird. Lädt man die Seite erneut, dann
sollte die Prozess-ID zu sehen sein.

-----------------------------
Einbinden von Karten in Texte
-----------------------------

Siehe das :ref:`Kapitel über Texte <karten-einbinden>`\ .


--------------------
Andere Familienbäume
--------------------

Siehe :ref:`familienbaeume-chapter`\ .


