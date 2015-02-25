{% load partialdate_tags %}
{% load fb_versions %}

.. role:: marginleft30
    :class: marginleft30

.. role:: cabin
    :class: cabin

===============================================================================
Familie {{ object }}
===============================================================================

{% if object.start_date or object.end_date %}
{{ object.start_date|partial_date:"d.m.Y" }} - {{ object.end_date|partial_date:"d.m.Y" }} :marginleft30:`({{object.get_family_rel_type_display }})`
{% else %}
({{object.get_family_rel_type_display }})
{% endif %}

**Vater:** {% include "genealogio/person_snippet_full.rst" with person=object.father %}

**Mutter:** {% include "genealogio/person_snippet_full.rst" with person=object.mother %}

{% if object.person_set.count %}**Kinder:**

{% for child in object.get_children %}
* {% include "genealogio/person_snippet_full.rst" with person=child %}
{% endfor %}
{% endif %}

{% with grandchildren=object.get_grandchildren %}
{% if grandchildren.count %}**Enkel:**

{% for child in grandchildren %}
* {% include "genealogio/person_snippet_full.rst" with person=child %}
{% endfor %}
{% endif %}
{% endwith %}

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

{% ifnotequal fr 2100 %}
----------
Zeitstrahl
----------

+-------+--------------------------------+
|       | {{ fr }} |img1| {{ to }}               |
+=======+================================+
| |PF|  | |imgPF|                        |
+-------+--------------------------------+
| |PM|  | |imgPM|                        |
+-------+--------------------------------+
{% for child in object.get_children %}| |P{{ forloop.counter0 }}|  | |imgP{{ forloop.counter0  }}|                        |
+-------+--------------------------------+
{% endfor %}{{ sparkline_legend }}

.. |img1| image:: /gen/sparkline/100000/{{ fr  }}/{{ to  }}/

.. |PF| replace:: {% include "genealogio/person_snippet_full.rst" with person=object.father %}

.. |imgPF| image:: /gen/sparkline/{{ object.father.id }}/{{ fr }}/{{ to }}/

.. |PM| replace:: {% include "genealogio/person_snippet_full.rst" with person=object.mother %}

.. |imgPM| image:: /gen/sparkline/{{ object.mother.id }}/{{ fr }}/{{ to }}/

{% for child in object.get_children %}
.. |P{{ forloop.counter0 }}| replace:: {% include "genealogio/person_snippet_full.rst" with person=child %}

.. |imgP{{ forloop.counter0  }}| image:: /gen/sparkline/{{ child.id }}/{{ fr }}/{{ to }}/
{% endfor %}

{% endifnotequal %}
