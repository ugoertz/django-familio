.. _familienbaeume-chapter:

=============
Familienbäume
=============

Typischerweise wird dieselbe Datenbank von mehreren Webseiten geteilt, d.h. dass
verschiedene (Groß-)Familien jeweils ihre eigene Webseite (mit eigener Adresse)
haben, und das die Objekte der Datenbank auf einer oder mehrerer dieser Seiten
zur Verfügung stehen. Die Zugehörigkeit lässt sich dabei für jedes Objekt
einzeln einstellen (und gegebenenfalls ändern). (Ausnahmen: Alle Orte
stehen immer auf allen Seiten, die mit der Datenbank arbeiten, zur Verfügung.
Kommentare von Nutzern zu einem Objekt stehen immer nur auf der Seite zur
Verfügung, auf der sie eingetragen wurden.)

Wir bezeichnen die einzelnen Webseiten/Großfamilien als *Familienbäume*.

Dass dieselbe Datenbank verwendet wird, bedeutet, dass zu einer Person
(Familie/Ereignis) auf jeder der Seiten dieselben Informationen gespeichert
sind: Es ist nicht möglich, auf einer der Seiten ein Geburtsdatum anzugeben, auf
einer anderen jedoch nicht; oder verschiedene Geburtsdaten anzugeben; Orte, die
der Person zugeordnet sind, sind automatisch auf allen Seiten, die diese Person
"kennen", zugeordnet. Wird der Datenbankeintrag der Person bearbeitet, so wirkt
sich das automatisch auf alle Seiten aus, die diese Person kennen. Es kann aber
mit einer Person (Familie/...) verknüpfte Objekte (Texte/Bilder) geben, die
nicht auf allen Seiten zur Verfügung stehen, die diese Person kennen.

Grundsätzlich erscheint es sinnvoll, die Datenbankeinträge zu *Personen*,
*Familien* und *Ereignissen* normalerweise zwischen den Seiten "benachbarter"
Familien zu teilen, wohingegen *Texte* und *Bilder* oft auf eine einzige Seite
beschränkt sein werden.

----------------
Voreinstellungen
----------------

Deshalb gibt es die folgenden Voreinstellungen:

* Texte und Bilder werden per Voreinstellung nur derjenigen Webseite zugeordnet,
  auf der sie erstellt werden.
* Zu jedem Familienbaum wird eine Liste anderer Familienbäume definiert, an die
  neue Personen, Familien und Ereignisse per Voreinstellung weitergegeben
  werden. (Im Einzelfall lässt sich die Voreinstellung verändern.)


------------------------------------------
Ändern der Zugehörigkeit zu Familienbäumen
------------------------------------------

Im Bearbeitungsformular einer Person (Familie/Ereignis) kann die Zugehörigkeit
zu Familienbäumen *nur beim Anlegen* des Objekts verändert werden.

Danach besteht die Möglichkeit

* auf der Bearbeitungsseite mit dem Button ``Entfernen`` oben das Objekt aus dem
  Familienbaum zu entfernen (gehört es auch zu anderen Familienbäumen, so
  verbleibt es in diesen)
* ein oder mehrere ausgewählte Objekte aus der Objektliste aus dem Familienbaum
  zu entfernen (Auswahl unten links),
* ein oder mehrere ausgewählte Objekte einem anderen Familienbaum hinzuzufügen
  (Auswahl unten links).

Dabei ist zu beachten: Das Hinzufügen eines Objekts zu einem anderen
Familienbaum erfordert Redakteursstatus für den anderen Familienbaum. Die
einzige Ausnahme sind die Familienbäume, die *per Voreinstellung* bei Personen,
Familien und Ereignissen hinzugefügt werden.



-------------------
Weitere Bemerkungen
-------------------

* Die Link-Adressen von Texten (``/n/personen/abcedf/``) können auch über die
  verschiedenen Seiten hinweg nur einmal vergeben werden. Dies kann zu
  unerwarteten Fehlermeldungen beim Abspeichern eines Textes führen, wenn die
  vorgesehene Adresse schon (in einem anderen Familienbaum) vergeben ist.
* Beim Anlegen eines Objektes können weitere Familienbäume (zusätzlich zu den
  per Voreinstellung gegebenen) hinzugefügt werden kann, wenn der Bearbeiter für
  die hinzuzufügenden Bäume den Redakteursstatus hat. Allerdings kann das
  Lupen-Symbol nicht zur Auswahl verwendet werden. Stattdessen sollte ein Teil
  des Familiennamens eingetippt werden und dann der gewünschte Familienbaum aus
  der Liste ausgewählt werden.


--------
Benutzer
--------

Neu angelegte Benutzer gehören zunächst nur zu einem einzigen Familienbaum. Sie
können aber für andere Familienbäume freigeschaltet werden. (Im Moment muss dies
ein *Superuser* machen.)

Es ist auch möglich, den Redakteursstatus nach Familienbaum getrennt zu
vergeben. Ein Benutzer kann also für einen Familienbaum Redakteur, und
gleichzeitig für einen anderen Baum normaler Nutzer sein.


---------------------
Getrennte Datenbanken
---------------------

Eine anderer Weg, der sich (auch nachträglich) wählen lässt, ist es, mit
getrennten Datenbanken zu arbeiten. Damit lassen sich Webseiten anlegen, die
nicht miteinander zu tun haben, so dass keinerlei "Konflikte" auftreten können,
so dass die Seiten aber auch nicht voneinander profitieren, wenn zum Beispiel
Personen hinzugefügt werden oder Fehler berichtigt werden, die auf beiden Seiten
vorkommen.

Es ist auch möglich, mit einer gemeinsamen Datenbasis zu beginnen, damit ein
Teil der schon vorhandenen Personen übernommen werden kann, und dann eine
Webseite "abzukoppeln", die dann mit einer Kopie der alten Datenbank als
eigenständiger Datenbank weiterarbeitet.

