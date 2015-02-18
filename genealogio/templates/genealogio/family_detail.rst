{% load partialdate_tags %}
{% load fb_versions %}

===============================================================================
Familie {{ object }}
===============================================================================


**Vater:** {% include "genealogio/person_snippet_full.rst" with person=object.father %}

**Mutter:** {% include "genealogio/person_snippet_full.rst" with person=object.mother %}

{% if object.person_set.count %}**Kinder:**

{% for child in object.person_set.all %}
* {% include "genealogio/person_snippet_full.rst" with person=child %}
{% endfor %}
{% endif %}


{% if object.events.count %}
----------
Ereignisse
----------

{% for event in object.events.all %}
{% include "genealogio/event_snippet.rst" with person=object %}
{% endfor %}
{% endif %}

{% if object.notes.count %}
-----
Texte
-----

{% for note in object.notes.all %}
{% include "notaro/note_trailer.rst" %}
{% endfor %}
{% endif %}

