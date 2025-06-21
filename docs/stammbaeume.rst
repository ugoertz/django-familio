.. _stammbaeume-chapter:

=====================================
Erstellen eines Stammbaums
=====================================

Der Punkt "Stammbäume" im "Benutzermenü" (auf den Benutzernamen in der
Kopfzeile klicken) führt zur Übersichtsseite der erstellten Stammbäume.
Beim ersten Aufruf ist die Seite leer.

Mit dem Link oben kannst Du die Liste aller öffentlich verfügbaren Stammbäume
aufrufen; das sind Stammbäume, die andere Benutzer erstellt und zur Verfügung
gestellt haben. Du kannst in der Liste die entsprechende pdf-Datei
herunterladen, aber den Stammbaum nicht bearbeiten.


-------------------
Der erste Stammbaum
-------------------

Mit den folgenden Schritten kommst Du zu Deinem ersten Stammbaum, ohne die gesamte
Dokumentation lesen zu müssen:

* Wähle "Stammbäume" im Benutzermenü
* Klicke "Neuen Stammbaum anlegen" oben rechts
* Gib einen Projekttitel ein (der Titel wird oben über den Stammbaum gedruckt
  und in der Liste Deiner Stammbäume angezeigt) und wähle unter
  "Referenzobjekt" die Familie aus, auf der der Stammbaum basieren soll. Tippe
  den Familiennamen ein und wähle die Familie aus der Liste aus, die angezeigt
  wird.
* Wenn Du möchtest, kannst Du die Anzahl der Vorfahren-/Nachkommenebenen anpassen.
* Klicke "Abspeichern"
* Du landest auf der Hauptseite des Stammbaums
* Klicke "PDF erstellen". Der Button färbt sich orange. Das Erstellen der
  pdf-Datei dauert ein bisschen (normalerweise zwei oder drei Minuten).
  Aktualisiere die Seite im Browser ("Neu laden"). Wenn die pdf-Datei fertig
  ist, wird ein Link angezeigt (und der Button ist wieder blau).

Jetzt kannst Du, wenn Du möchtest, weitere Anpassungen vornehmen, abspeichern
und dann eine neue pdf-Datei erzeugen lassen.

Wenn der Stammbaum fertig ist, wird nach dem erneuten Laden der Seite auch eine
Bilddatei mit dem Stammbaum angezeigt. Durch Anklicken dieses Vorschaubilds kann
man eine Bilddatei in hoher Auflösung herunterladen.

-------------------
Weitere Optionen
-------------------

**Papierformat**
  Du kannst das Papierformat auswählen (Standard-DIN-Formate; manuell durch
  Breite und Höhe vorgegeben; oder automatisch berechnet). Die PDF-Datei hat
  dann das entsprechende Format. Wenn nicht "automatisch berechnet" angegeben
  wird, werden die Bilddateien so skaliert, dass die Auflösung zum gewählten
  Format passt.

**Breite, Höhe**
  Hier kann man die genaue Breite und Höhe angeben, die verwendet werden
  sollen, wenn als Papierformat "Manuell" ausgewählt wurde.

**Bilddateien skalieren**
  Wenn die Bilddateien zu groß sind, kann man hier einen geeigneten Wert für
  die maximale Breite in Pixeln angeben. Bei allen Papierformaten außer
  "automatisch" werden die Bilddateien aber sowieso auf eine zum Format
  passende Auflösung gebracht. (Wenn hier ein Wert angegeben wird, werden sie
  in dem Fall also zweimal "heruntergerechnet".)

**Schwarz/weiß**
  Falls ausgewählt, dann werden die Bilddateien für den Stammbaum alle in
  schwarz/weiß umgewandelt. (Die in der Chronik abgespeicherten Portraitfotos
  werden natürlich nicht verändert.)

**Verfügbar für andere Benutzer**
  Wenn dies eingeschaltet ist, dann können auch alle anderen Benutzer der
  Chronik den Stammbaum in der Liste der öffentlich verfügbaren Stammbäume
  sehen und die entsprechenden Dateien herunterladen. Sie können aber nicht die
  Einstellungen verändern.

-----------------------
TeX-Datei herunterladen
-----------------------

Um ganz individuelle Anpassungen vorzunehmen, kannst Du ein zip-Archiv mit der
TeX-Datei und den Bilddateien herunterladen. Damit kannst Du "im Prinzip"
beliebige Anpassungen machen, musst aber auf Deinem Rechner das Programmpaket
TeX installieren (das ursprünglich für mathematischen Schriftsatz erstellt
wurde, aber dann mit einer Vielzahl von Erweiterungen ergänzt wurde; die
Stammbäume werden mit `genealogytree
<https://ctan.org/pkg/genealogytree?lang=de>`__ erstellt). Die TeX-Datei kann,
wenn alles installiert ist, mit `lualatex` in eine PDF-Datei kompiliert werden.

