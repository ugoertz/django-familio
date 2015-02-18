======================
Orte
======================

explain how things work

- autocomplete
- adding new places





internals ...


https://wdq.wmflabs.org/api_documentation.html
uri = 'https://wdq.wmflabs.org/api?'
uri += urlencode([('q', 'claim[31:(tree[486972][][279])] AND claim[17:183] AND link[dewiki]')])


uri2 = 'https://www.wikidata.org/entity/Q649113.json'
data649113 = json.load(urllib2.urlopen(uri2))

wikidata link
data649113['entities']['Q649113']['sitelinks']['dewiki']
data649113['entities']['Q649113']['claims']['P625'][0]['mainsnak']['datavalue']['value']['longitude'], data649113['entities']['Q649113']['claims']['P625'][0]['mainsnak']['datavalue']['value']['latitude']


also interesting:
https://wikipedia.readthedocs.org/en/latest/code.html#api
http://www.geonames.org/export/wikipedia-webservice.html

