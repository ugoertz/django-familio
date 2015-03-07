{% load partialdate_tags %}
{% load fb_versions %}

===============================================================================
{{ object.title }}
===============================================================================

{% if event.date %}am {{ event.date|partial_date:"d.m.Y" }}{% endif %}
{% if event.place %}in `{{ event.place }} <{% url "place-detail" event.place.id %}>`__ {% endif %}

{{ event.description }}


{% if object.portrait.image %}

.. image:: {% version object.portrait.image 'small' %}
    :class: pull-right

{% endif %}

{% for pe in event.personevent_set.all %}

{{ pe.get_role_display }}: 
{% include "genealogio/person_snippet.rst" with person=pe.person %}

{% endfor %}

{% include "genealogio/notes.rst" %}

