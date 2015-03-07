{% load partialdate_tags %}
{% load fb_versions %}
{% load base_tags %}

.. role:: marginleft30
    :class: marginleft30

.. role:: cabin
    :class: cabin

.. role:: alignleft
    :class: alignleft

.. role:: alignright
    :class: alignright

.. |br| raw:: html

   <br />

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

{% include "genealogio/events.rst" %}

{% include "genealogio/notes.rst" %}

{% ifnotequal fr 2100 %}
----------
Zeitstrahl
----------

{% gapless %}
+--------+--------------------------------+
|        | |fr| |head| |to|               |
+========+================================+
{% if object.father.on_current_site %}| |PF|   | |imgPF|                        |
+--------+--------------------------------+{% endif %}
{% if object.mother.on_current_site %}| |PM|   | |imgPM|                        |
+--------+--------------------------------+{% endif %}
{% for child in object.get_children %}{% if child.on_current_site %}| |{{ forloop.counter0 }}|    | |img{{ forloop.counter0  }}|                         |
+--------+--------------------------------+{% endif %}
{% endfor %}
{{ sparkline_legend }}
{% endgapless %}

{{ sparkline_legend_ref }}

.. |head| image:: /gen/sparkline/100000/{{ fr  }}/{{ to  }}/

.. |fr| replace::
    :alignleft:`{{ fr }}`

.. |to| replace::
    :alignright:`{{ to }}`

{% include "genealogio/person_sparkline.rst" with person=object.father label="PF" %}

{% include "genealogio/person_sparkline.rst" with person=object.mother label="PM" %}

{% for child in object.get_children %}
{% include "genealogio/person_sparkline.rst" with person=child label=forloop.counter0 %}

{% endfor %}


{% endifnotequal %}
