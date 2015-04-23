{% load partialdate_tags %}
{% load fb_versions %}

{% if latexmode %}.. _{{ object.handle }}:{% endif %}

{{ object.title }}
===============================================================================

{% if object.date %}am {{ object.date|partial_date:"d.m.Y" }}{% endif %}
{% if object.place %}in `{{ object.place }} <{% url "place-detail" object.place.id %}>`__ {% endif %}

{{ object.description }}

{% for pe in object.personevent_set.all %}

{{ pe.get_role_display }}: 
{% include "genealogio/person_snippet.rst" with person=pe.person %}

{% endfor %}

{% include "genealogio/notes.rst" %}

{% include "notaro/sources.rst" with all_sources=object.eventsource_set.all %}

