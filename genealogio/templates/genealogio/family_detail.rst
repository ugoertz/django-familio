{% load partialdate_tags %}
{% load fb_versions %}
{% load base_tags %}

.. role:: marginleft30
    :class: marginleft30

.. role:: cabin
    :class: cabin

{% if not latexmode %}
.. |br| raw:: html

   <br />
{% endif %}

{% if latexmode %}.. _{{ object.handle }}:{% endif %}

{% if itemtitle %}{{ itemtitle }}{% else %}Familie {{ object }}{% endif %}
======================================================================================================================================================================================

{% if object.start_date or object.end_date %}
{{ object.start_date|partial_date:"d.m.Y" }} - {{ object.end_date|partial_date:"d.m.Y" }} :marginleft30:`({{object.get_family_rel_type_display }})`
{% else %}
({{object.get_family_rel_type_display }})
{% endif %}

{% include "genealogio/person_snippet_full.rst" with person=object.father label="**Vater:** " %}

{% include "genealogio/person_snippet_full.rst" with person=object.mother label="**Mutter:** " %}

{% if object.person_set.count %}**Kinder:**

{% for child in object.get_children_as_personfamily %}
* {% include "genealogio/person_snippet_full.rst" with person=child.person show_child_type=child.get_child_type %}
{% endfor %}
{% endif %}

{% with grandchildren=object.get_grandchildren %}
{% if grandchildren.count and not hide_grandchildren %}**Enkel:**

{% for child in grandchildren %}
* {% include "genealogio/person_snippet_full.rst" with person=child %}
{% endfor %}
{% endif %}
{% endwith %}

{% include "genealogio/events.rst" %}

{% include "genealogio/notes.rst" %}

{% if display_timeline %}

Zeitstrahl
----------

{% gapless %}
+---------------+--------------------------------+
| |frto-{{ object.id|stringformat:"04d" }}|   |      |head-{{ object.id|stringformat:"04d"  }}|               |
+===============+================================+
{% if object.father.on_current_site %}| |PF-{{ object.id|stringformat:"04d" }}|     | |imgPF-{{ object.id|stringformat:"04d"  }}|                   |
+---------------+--------------------------------+{% endif %}
{% if object.mother.on_current_site %}| |PM-{{ object.id|stringformat:"04d" }}|     | |imgPM-{{ object.id|stringformat:"04d" }}|                   |
+---------------+--------------------------------+{% endif %}
{% for child in object.get_children %}{% if child.on_current_site %}| |{{ forloop.counter0|stringformat:"02d" }}-{{ object.id|stringformat:"04d"  }}|     | |img{{ forloop.counter0|stringformat:"02d" }}-{{ object.id|stringformat:"04d" }}|                   |
+---------------+--------------------------------+{% endif %}
{% endfor %}
{{ sparkline_legend }}
{% endgapless %}

{{ sparkline_legend_ref }}

.. |frto-{{ object.id|stringformat:"04d" }}| replace:: {{ fr }} - {{ to }}

.. |head-{{ object.id|stringformat:"04d" }}| {% if latexmode %}sparklineimg{% else %}image{% endif %}:: {% url 'sparkline-head' fampk=object.id fr=fr to=to %}

{% include "genealogio/person_sparkline.rst" with person=object.father label="PF" %}

{% include "genealogio/person_sparkline.rst" with person=object.mother label="PM" %}

{% for child in object.get_children %}
{% include "genealogio/person_sparkline.rst" with person=child label=forloop.counter0|stringformat:"02d" %}

{% endfor %}

{% endif %}

{% include "notaro/sources.rst" with all_sources=object.familysource_set.all %}

