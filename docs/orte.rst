.. _orte-chapter:

======================
Orte
======================

Ein Ort ist in der Datenbank durch seinen Namen und die geographischen
Koordinaten beschrieben. Zusätzlich können dem Ort Links auf externe Webseiten
zugeordnet werden (zum Beispiel die offizielle Webseite der Stadt, oder die
Wikipedia-Seite zu dem Ort).

Alle nicht ganz kleinen [#f1]_ Orte in Deutschland sind bereits in der Datenbank
angelegt.

*Um einen solchen Ort auszuwählen (zum Beispiel als Geburtsort einer Person),
muss die Autocomplete-Liste verwendet werden, d.h., man tippt den Ortsnamen oder
einen Teil davon ein, und wählt dann den entsprechenden Ort aus der sich
öffnenden Liste per Mausklick. Wenn man nur den Namen eintippt, kann die
Verknüpfung zu dem richtigen Eintrag in der Datenbank nicht hergestellt werden.*

.. [#f1] Genau genommen heißt das: Alle Orte in Deutschland, die einen Eintrag
         bei `Wikidata <http://wikidata.org>`__ haben - dies schließt auch viele
         Ortsteile ein.


.. _ort-hinzufuegen:

---------------
Orte hinzufügen
---------------

Es können leicht weitere Orte hinzugefügt werden: Man klickt auf ``Ort
hinzufügen``, gibt den Namen ein und hält durch Klick auf die Karte fest, wo
dieser Ort liegt.

(Wenn man keinen Ort auf der Karte anklickt, versucht das Programm, die
Koordinaten durch eine Abfrage bei OpenStreetMap aus dem angegebenen Namen zu
ermitteln; das funktioniert wahrscheinlich nur bei größeren Städten verlässlich
und sollte dann nachträglich kontrolliert werden.)


------------------------
Technische Informationen
------------------------


Auslesen der Information zu allen Ortschaften in Deutschland aus Wikidata:

https://wdq.wmflabs.org/api_documentation.html

``https://wdq.wmflabs.org/api?q=claim[31:(tree[486972][][279])] AND claim[17:183] AND link[dewiki]')])``


.. code::

    uri2 = 'https://www.wikidata.org/entity/Q649113.json'
    data649113 = json.load(urllib2.urlopen(uri2))

    wikidata link
    data649113['entities']['Q649113']['sitelinks']['dewiki']
    data649113['entities']['Q649113']['claims']['P625'][0]['mainsnak']['datavalue']['value']['longitude']
    data649113['entities']['Q649113']['claims']['P625'][0]['mainsnak']['datavalue']['value']['latitude']


Vergleiche auch

* https://wikipedia.readthedocs.org/en/latest/code.html#api
* http://www.geonames.org/export/wikipedia-webservice.html

