.. _pdfexport-chapter:

=====================================
Erstellen einer Chronik im pdf-Format
=====================================

Um eine pdf-Datei aus ausgewählten Daten der Chronik zu erstellen, wähle im
"Benutzermenü" (auf den Benutzernamen in der Kopfzeile klicken) den Punkt
"Export als PDF". Du kommst auf die Seite mit der Liste deiner "Buchprojekte";
beim ersten Aufruf ist die Seite leer.

Mit dem Link oben kannst Du die Liste aller öffentlich verfügbaren Bücher
aufrufen; das sind Buchprojekte anderer Benutzer, die diese allgemein zur
Verfügung gestellt haben. Diese Bücher kannst Du als pdf-Datei herunterladen; Du
kannst ihre Inhalte aber nicht bearbeiten.


--------------
Das erste Buch
--------------

Mit den folgenden Schritten kommst Du zu Deinem ersten Buch, ohne die gesamte
Dokumentation lesen zu müssen:

* Wähle "Export als PDF" im Benutzermenü
* Klicke "Neues Buchprojekt anlegen" oben rechts
* Gib einen Projekttitel ein (unter dem das Buch in der Liste Deiner
  Buchprojekte angezeigt werden soll) und wähle unter "Objekte hinzufügen" aus,
  wie das Buch zu Beginn aus der Datenbank bestückt werden soll. Eine gute
  Möglichkeit ist hier "Vorfahren und Nachkommen von Person/Familie". Bei dieser
  Wahl muss dann im "Referenz"-Feld die Person oder Familie ausgewählt werden:
  Tippe einen Teil des Namens ein, dann bekommst Du Auswahlmöglichkeiten
  angezeigt.
* Klicke "Abspeichern"
* Du landest auf der Hauptseite des Buchs
* Klicke "PDF erstellen". Der Button färbt sich orange. Das Erstellen der
  pdf-Datei dauert ein bisschen (ein paar Minuten). Aktualisiere die Seite im
  Browser ("Neu laden"). Wenn die pdf-Datei fertig ist, wird ein Link angezeigt
  (und der Button ist wieder blau).

Nun kannst Du nach und nach "deine" Chronik individuell anpassen wie unten
beschrieben, und dann jeweils eine neue pdf-Datei erzeugen lassen.


-------------------
Aufbau eines Buches
-------------------

Alle "Bücher", die auf die hier beschriebene Art und Weise erstellt werden
können, sind vom Prinzip her folgendermaßen aufgebaut:


**Buch**
  Das Buchobjekt selbst dient hauptsächlich als "Container", das einige globale
  Informationen enthält sowie auf die eigentlichen Inhalte verweist.

  Auf der Hauptseite des Buchs befindet sich der Button, um die pdf-Datei zu
  erstellen, und es werden alle (Unter-)Kapitel und Einträge aufgelistet.

  Sämtliche Inhalte sind in "Kollektionen" organisiert, d.h. in Kapitel,
  Unterkapitel (Unterunterkapitel, ...), die jeweils gewisse Einträge und
  gegebenenfalls Unterkollektionen enthalten können.

.. _collection-title:

**Buchkapitel**
  Die Wurzel des "Kapitelbaums" bildet das Buchkapitel, das direkt dem Buch
  zugeordnet ist. Der Titel dieses Kapitels wird als Buchtitel verwendet.

  Als einziges Kapitel kann dieses Kapitel keine Einträge direkt enthalten,
  sondern nur Unterkapitel (in denen dann Einträge und/oder Unterunterkapitel
  enthalten sein können).

**Unterkapitel**
  Die Unterkapitel dienen der Gliederung des Buches. In vielen Fällen wird es
  ausreichen, unterhalb des Buchkapitels nur eine Ebene von Kapiteln
  anzulegen. Man könnte aber die Gliederung auch feiner anlegen und in diesen
  Kapiteln Unterkapitel (und Unterunterkapitel ...) anlegen.

**Einträge**
  Die Einträge enthalten den eigentlichen Inhalt des Buchs. Üblicherweise ist
  ein Eintrag einem Objekt der Datenbank zugeordnet (einer Person, Familie,
  ...). Man kann aber auch ganz "freie" Einträge hinzufügen.

Beim Editieren von (Unter-)Kapiteln und Einträgen wird eine Navigationszeile mit
den übergeordneten Kapiteln und dem Buch angezeigt. Zu jedem Kapitel wird seine
"Ebene" angezeigt: Das Buchkapitel liegt in der Ebene 0, seine direkten
Unterkapitel (die "Kapitel des Buches") in der Ebene 1, usw.

----------------
Ein Buch anlegen
----------------

**Titel**
  Der an dieser Stelle eingegebene Titel dient dazu, das Buchprojekt in der
  Liste aller Buchprojekte kenntlich zu machen. Er wird als Voreinstellung für
  den Titel des Buchkapitels verwendet, der dann als Titel im pdf selbst
  angegeben wird. Dieser lässt sich aber ändern: siehe :ref:`Titelseite
  <titelseite>`, :ref:`Buchtitel <collection-title>`.

**Kurzbeschreibung**
  Wie der Titel wird die Kurzbeschreibung in der Liste aller Buchprojekte
  angegeben, aber darüberhinaus nicht verwendet.

**Öffentlich verfügbar**
  Wenn diese Option eingestellt wird, können alle Benutzer der Webseite das Buch
  in der Liste der öffentlich verfügbaren Bücher sehen und die pdf-Datei dazu
  herunterladen (aber nicht das Buch "bearbeiten").

Der wichtigste Punkt beim Erstellen eines Buches ist die Entscheidung, welche
Objekte der Datenbank (d.h. welche Personen, Familien, ...) zu Beginn enthalten
sein sollen. (Es lassen sich nachher Einträge :ref:`hinzufügen
<einträge-hinzufügen>` oder :ref:`löschen <einträge-löschen>`, aber am
bequemsten ist es natürlich, wenn das nur in wenigen Fällen erforderlich ist.
Außerdem ist es leichter, Einträge zu löschen als welche hinzuzufügen, also
sollte man im Zweifelsfall lieber etwas zu viele Objekte zu Beginn hinzufügen.)
Für die Auswahl stehen die folgenden Möglichkeiten zur Verfügung:

.................
Gesamte Datenbank
.................

Mit dieser Option werden *alle* Texte, Personen, Familien, Ereignisse und
Quellen aus der Datenbank in das Buchprojekt einsortiert, und zwar jeweils in
ein eigenes Kapitel.

.........................................
Vorfahren/Nachkommen einer Person/Familie
.........................................

Mit diesen Optionen kann die Auswahl eingeschränkt werden auf Vorfahren und/oder
Nachkommen einer Person oder einer Familie. (Als die Vorfahren einer Familie
werden die Vorfahren des Vaters zusammen mit denjenigen der Mutter betrachtet.)

Zusätzlich werden alle Familien der jeweiligen Personen hinzugefügt (die Partner
bekommen aber keinen eigenen Personeneintrag), sowie alle Texte und Quellen, die
einer der Personen oder Familien in dieser Liste zugeordnet sind.

Bei Wahl dieser Option muss dann noch die entsprechende Person oder Familie in
dem darunterliegenden Auswahlfeld ausgewählt werden. Nach Eingabe des
Anfangsteils eines Vor- oder Nachnamens der Person bzw. einer zugehörigen Person
werden Auswahlmöglichkeiten angezeigt.

........................
Mit leerem Buch beginnen
........................

Außerdem besteht die Möglichkeit, gar keine Objekte von vorneherein einzufügen,
sondern alles per Hand zu erledigen.

.............
Einstellungen
.............

Siehe :ref:`Einstellungen <einstellungen-buch>`.

----------------------
Buchprojekt bearbeiten
----------------------

.. _einstellungen-buch:

.............
Einstellungen
.............

Wenn der Schalter "Aktiv" auf Aus gestellt wird, wird der entsprechende Eintrag
bzw. das Unterkapitel beim Erstellen der pdf-Datei nicht berücksichtigt.

Der Schalter "Eigenen Titel im pdf verwenden" bewirkt, dass der Titel des
Eintrags statt des voreingestellten Titels verwendet wird. Diese Einstellung hat
nur dann Auswirkungen, wenn das Textfeld des Eintrags leer ist. Ist Text im
Textfeld eingegeben, so muss dort auch der Titel angegeben werden
(ReStructuredText-formatiert, d.h. mit ``=`` unterstrichen; Untertitel können
durch Unterstreichen mit ``-`` markiert werden).

Die folgenden Einstellungen stehen zurzeit zur Verfügung (alle Einstellungen
haben nur Auswirkungen für Objekte einer bestimmten Art, zum Beispiel bleiben
die "Familien-Einstellungen" bei Personeneinträgen völlig unberücksichtigt):

**Familie: Zeitstrahl einbinden**
  Wenn diese Option angewählt ist, wird in Familieneinträgen der Zeitstrahl
  (wie auf den Webseiten zu Familien) eingebunden.

**Familie: Enkel auflisten**
  Füge die Liste der Enkel (wie auf der Webseite) ein.

**Person: Orte auflisten**
  Zeige die der Person zugeordneten Orte (Geburts-, Sterbeort und gegebebenfalls
  weitere zugeordnete Orte)

Diese Einstellungen können auf verschiedenen "Ebenen" gesetzt werden. Zunächst
einmal wird ein voreingestellter Wert beim Erstellen eines Buchprojekts
festgesetzt. Später können dann auch für einzelne (Unter-)Kapitel oder sogar für
einzelne Einträge abweichende Optionen festgelegt werden. Bei jedem Eintrag wird
dann die Einstellung berücksichtigt, die in der "nächstliegenden" Einheit
gesetzt wurde: Ist die Einstellung für den Eintrag selbst vorgenommen worden, so
zählt diese; sonst wird im (Unter-)Kapitel geschaut, in dem der Eintrag
eingebunden ist, dann im nächsten übergeordneten Kapitel, etc. Wenn keine
individuellen Einstellungen gemacht wurden, würde also für alle Einträge auf die
Werte zurückgegriffen, die für das Buchprojekt festgelegt sind.

Damit ist es möglich, beispielsweise die Zeitstrahlen nur für einzelne Familien
oder nur für alle Familien eines bestimmten Unterkapitels einzubinden.

...............................
Einträge/Unterkapitel sortieren
...............................

Die Liste der Einträge (bzw. der Unterkapitel) kann sortiert werden, indem die
Einträge an dem Oben/Unten-Pfeil mit der Maus noch oben oder unten gezogen
werden. *Damit die neue Reihenfolge abgespeichert wird, muss der
"Abspeichern"-Button geklickt werden.*

.. _einträge-löschen:

.............................
Einträge/Unterkapitel löschen
.............................

Mit dem "Löschen"-Button können Einträge (bzw. Unterkapitel) gelöscht werden.
*Damit der Eintrag tatsächlich gelöscht wird, muss der "Abspeichern"-Button
geklickt werden.* (Bis dahin besteht die Möglichkeit, den Eintrag durch erneutes
Laden der Seite "wiederherzustellen".)

.......................
Unterkapitel hinzufügen
.......................

Mit diesem Button kann man ein zusätzliches Unterkapitel hinzufügen. Wenn ein
Objekttyp ausgewählt wird, werden Einträge zu allen Objekten dieser Art (zum
Beispiel: allen Personen der Datenbank) von vorneherein in das Kapitel
eingefügt. (Beim späteren Bearbeiten kann man natürlich davon wieder welche
löschen; grundsätzlich ist Löschen natürlich bequemer als das Hinzufügen vieler
Personen, so dass es sich lohnen kann, erst einmal alle Personen (oder
Familien/Texte/...) hinzuzufügen.

Der **Titel** wird als Titel des Kapitels eingefügt. (Der Titel des
Buchkapitels wird als Titel des Buchs verwendet; siehe auch :ref:`Titelseite
<titelseite>`.)

.. _einträge-hinzufügen:

...................
Einträge hinzufügen
...................

Mit dem entsprechenden Button können einem Kapitel weitere Einträge hinzugefügt
werden. Dabei gibt es die folgenden beiden Möglichkeiten:

Einträge aus der Datenbank hinzufügen
.....................................

Es kann ein Objekt der Datenbank angegeben werden: Wähle zunächst die Art des
Objekts aus, und dann das konkrete Objekt, das dem Eintrag zugeordnet werden
soll. In das pdf wird dann an der entsprechenden Stelle die Information über
diese Person/Familie/... eingebunden, mehr oder weniger wie sie auf der Webseite
angezeigt wird. Das genaue Ergebnis kann durch die "Einstellungen" beeinflusst
werden, oder noch weiter angepasst werden, indem das :ref:`Textfeld <textfeld>`
benutzt wird.

Zusätzliche Einträge hinzufügen
...............................

Es können auch Einträge hinzugefügt werden, denen kein Objekt zugeordnet ist. In
solchen Einträgen kann dann im Textfeld freier Text eingegeben werden, der an
der entsprechenden Stelle eingebunden werden soll.

------------------
Eintrag bearbeiten
------------------

.. _textfeld:

........
Textfeld
........

Zu jedem Eintrag gibt es ein Textfeld.

Bei Einträgen, denen kein Objekt der Datenbank zugeordnet ist, wird in die
pdf-Datei der Text dieses Textfeldes eingebunden.

Bei Einträgen, denen ein Objekt der Datenbank zugeordnet ist, wird der Text aus
dem Textfeld eingebungen, *sofern das Textfeld nicht leer ist*. Wenn das
Textfeld leer ist, dann wird der Text aus der Datenbank generiert und entspricht
im wesentlichen dem, was auf der Webeseite zu dem entsprechenden Objekt
angezeigt wird.

Der Text im Textfeld kann/muss als :ref:`ReStructuredText <restructuredtext>`
formatiert werden. Der Titel des Eintrags muss auch im Textfeld angegeben werden
(es wird nicht automatisch ein Titel hinzugefügt): Als mit ``====``
unterstrichene Überschrift. (Untertitel im Text können dann per Unterstreichung
mit ``----`` markiert werden.

Wie in Texte können Bilder und Landkarten :ref:`eingebunden werden
<bilder-einbinden>`.

Nicht vergessen: Änderungen im Textfeld müssen *abgespeichert* werden, damit sie
endgültig sind.

............................
Text aus der Datenbank holen
............................

Mit diesem Button kann man den (ReStructuredText-formatierten) Text aus der
Datenbank in das Textfeld einspeisen. Dieser Text kann dann als Grundlage für
Veränderungen oder Ergänzungen dienen.

(Das hat natürlich auch zur Konsequenz, das Änderungen in der Datenbank zu einem
späteren Zeitpunkt dann nicht mehr berücksichtigt werden. Bei den Einträgen, wo
das Textfeld leer ist, wird die Datenbank erst zu dem Zeitpunkt abgefragt, in
dem die pdf-Datei erstellt wird.)

..........
Stammbäume
..........

Stammbäume (d.h. Vorfahren oder Nachkommen einer Person in "Baumform") können
mit den folgenden Befehlen eingebunden werden:

.. code::

  .. familytree:: <handle> pedigree

für einen Baum der Vorfahren (pedigree = Ahnentafel), und

.. code::

  .. familytree:: <handle> descendants

für einen Nachkommenbaum. Dabei ist jeweils ``handle`` durch das :ref:`Handle
<handle>` der Bezugsperson zu ersetzen. Am einfachsten ist es, wenn man einen
neuen Eintrag hinzufügt, diesen der entsprechenden Person zuordnet (dann kann
man das Handle aus dem Eintragstitel kopieren) und dort dann im Textfeld die
oben genannte Zeile einfügt. (Man kann den Stammbaum natürlich auch dem Eintrag
der jeweiligen Person hinzufügen. Dazu sollte man dort den "Text aus der
Datenbank holen" und dann den ``familytree``-Befehl an geeigneter Stelle
einfügen.

**Optionen:**

Folgende Optionen können verwendet werden (eingerückt und zwischen
Doppelpunkten, siehe die Beispiele unten):

generations
  Anzahl der Generationen, die gezeigt werden sollen (bei Vorfahren: 1 = nur die
  Person und ihre Eltern; 2 = Person, Eltern, Großeltern; usw. Voreinstellung
  ist 3; bei Nachkommen: 1 = nur die Person und ihre Kinder; 2 = Person, Kinder,
  Enkel; usw. Voreinstellung ist 2).

rotate
  Drehe den Baum um 90 Grad (Voreinstellung bei Vorfahren: Baum wird gedreht;
  mit der rotate Option kann das rückgängig gemacht werden).

height
  Höhe der Grafik

placement
  Per Voreinstellung wird der Stammbaum so im Dokument verschoben, dass die
  Seitenumbrüche gut passen. Wenn bei dieser Option ``H`` angegeben wird, wird
  der Stammbaum genau an der Stelle eingefügt, wo der ``familytree``-Befehl
  steht. Das kann den Nachteil haben, dass große Teile einer Seite frei bleiben
  müssen.

caption
  Der Untertitel des Stammbaums (Voreinstellung: *Ahnentafel für ...* bzw.
  *Nachkommen von ...*). Wird diese Option ohne Wert angegeben (wie im zweiten
  Beispiel unten), dann wird keine Bildunterschrift gegeben.

**Beispiele:**

.. code::

  .. familytree:: P_GoertzUlrich1973_57482 pedigree
    :generations: 2
    :rotate:
    :height: 15cm

  .. familytree:: P_GoertzUlrich1973_57482 descendants
    :generations: 1
    :placement: H
    :caption:

.. _titelseite:

---------------------------
Eigene Titelseite hochladen
---------------------------

Die automatisch erzeugte Titelseite der Chronik ist sehr minimalistisch. Um dem
Dokument einen individuelleren Touch zu verleihen, kann man eine pdf-Datei
als Titelseite hochladen. Die erste Seite des automatisch erzeugten
pdf-Dokuments wird dann ganz zm Schluss durch diese Datei ersetzt.
Sinnvollerweise sollte es sich um ein Dokument im Format DIN A 4 handeln.
Normalerweise wird das nur ein einseitiges Dokument sein; das ist aber nicht
zwingend.

------------
PDF erzeugen
------------

Auf der Hauptseite des Buches kann mit dem entsprechend bezeichneten blauen
Button die Erzeugung der pdf-Datei angestoßen werden. Dieser Prozess dauert ein
bisschen (ca. 1 Minute; wenn Landkarten neu erstellt werden müssen, dann kann es
auch wesentlich länger dauern).

Solange der Erstellungsprozess läuft, wird der entsprechende Button orange
angezeigt. Im Normalfall sollte der Prozess nicht erneut angestoßen werden,
solange der Button orange ist. *Die Farbe aktualisiert sich nicht von selbst;
man muss die Seite neu laden, um den aktuellen Status zu sehen.*

-----------------------
TeX-Datei herunterladen
-----------------------

Neben dem Download der endgültigen pdf-Datei wird auf der Hauptseite des
Buchprojekts auch der Download eines zip-Archives angeboten. Dieses zip-Archiv
enthält die Dateien, die für den letzten Schritt der Erstellung des pdfs
benötigt werden (allerdings nicht die pdf-Datei selbst). Dieser letzte Schritt
besteht im Aufruf des Schriftsatzsystems XeLaTeX, einer Variante von TeX.
Dementsprechend sind in dem zip-Archiv die tex-Datei, die benötigten
"Style-Dateien" und die einzubindenden Bilddateien enthalten.

Damit ist es im Prinzip möglich, durch manuelle Anpassungen der TeX-Datei
weitere Veränderungen ganz feinkörnig vorzunehmen (oder auch Fehler im Prozess
oder in den eigenen ReStructured-Text-Dateien zu suchen). Allerdings ist das
eher etwas "für Fortgeschrittene", will sagen: erfordert zusätzliche
Einarbeitung in das TeX-System und insbesondere die Installation von XeLaTeX.


-----------------------
Export als GEDCOM-Datei
-----------------------

Das `GEDCOM-Format <https://de.wikipedia.org/wiki/GEDCOM>`__ ist das
Standard-Format für den Datenaustausch zwischen Genealogie-Programmen (auch wenn
es leider schon ein bisschen veraltet ist und seine Schwachstellen hat).

Aus einem Buchprojekt wie oben beschrieben kann man eine GEDCOM-Datei
exportieren, indem man den Link *GEDCOM* in der Download-Zeile oben anklickt.

Dadurch werden alle Datenbank-Objekte (Personen, Familien, Texte; Ereignisse aus
dem Buchprojekt werden Personen bzw. Familien zugeordnet, wo das möglich ist) in
die GEDCOM-Datei exportiert. Momentan ist das so gelöst, dass für den
GEDCOM-Export die Informationen direkt aus der Datenbank ausgelesen werden,
d.h.: Während es für die pdf-Datei möglich ist, individuelle Änderungen in den
entsprechenden Textfeldern vorzunehmen oder weitere Einträge zu ergänzen,
spiegeln sich diese Änderungen/Ergänzungen in der GEDCOM-Datei nicht wieder. Die
Anbindung des GEDCOM-Exports an ein Buchprojekt dient also nur dazu, eine
Auswahl eines Teils der Datenbank zu ermöglichen.

Der GEDCOM-Export ist (ein bißchen aber) nicht sehr ausführlich getestet worden.
Es kann gut sein, dass noch Fehler drin sind, also Vorsicht, wenn exportierte
Daten mit Daten aus anderen Quellen kombiniert werden -- lieber einmal zu oft
ein Backup machen. (Für Rückmeldungen über Fehler bin ich natürlich dankbar.)

Es gibt auch noch ein paar Punkte, die man eventuell ändern sollte, zum Beispiel
werden die Texte im Moment so exportiert, wie sie für die Webseite abgespeichert
sind (also inklusive aller Formatierungen wie den Links auf Datenbankobjekte).
Wenn hier jemand konkrete Änderungswünsche hat: Bitte melden.




