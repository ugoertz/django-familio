{% load partialdate_tags %}
{% load fb_versions %}

.. role:: underline
    :class: underline

===============================================================================
{{ object.get_full_name }}
===============================================================================

{% if object.portrait.image %}

.. image:: {% version object.portrait.image 'small' %}
    :class: pull-right

{% endif %}

{% if object.datebirth or object.placebirth %}geboren {{ object.datebirth|partial_date:"d.m.Y" }}{% if object.placebirth %} in `{{ object.placebirth }} <{% url "place-detail" object.placebirth.id %}>`__ {% endif %}{% endif %}{% if object.datedeath or object.placedeath %} - gestorben {{ object.datedeath|partial_date:"d.m.Y" }}{% if object.placedeath %} in `{{ object.placedeath }} <{% url "place-detail" object.placedeath.id %}>`__ {% endif %}{% endif %}

**Vater:** {% include "genealogio/person_snippet_full.rst" with person=object.get_father %}

**Mutter:** {% include "genealogio/person_snippet_full.rst" with person=object.get_mother %}

{% with allchildren=object.get_children %}
{% for partner, children, txt, family in allchildren %}

`{{ txt }} <{{ family.get_absolute_url }}>`__ {% include "genealogio/person_snippet.rst" with person=partner %}

{% if children %}
.. class:: marginleft30

    **Kinder:**

{% for child in children %}
    * {% include "genealogio/person_snippet_full.rst" with person=child %}
{% endfor %}
{% endif %}
{% endfor %}
{% endwith %}

{% if object.comments %}{{ object.comments }}{% endif %}


{% include "genealogio/events.rst" %}

{% if object.personplace_set.count %}
----
Orte
----

{% for pl in object.personplace_set.all %}
* {% if pl.start and pl.start.year != pl.end.year or pl.start.month != pl.end.month or pl.start.day != pl.end.day %}{{ pl.start|partial_date:"d.m.Y" }} - {% endif %}{{ pl.end|partial_date:"d.m.Y" }}{% if pl.start or pl.end %}: {% endif %} `{{ pl.place }} <{{ pl.place.get_absolute_url }}>`__ ({{ pl.get_typ_display }})
{% endfor %}
{% endif %}

{% include "genealogio/notes.rst" %}

