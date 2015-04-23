{% load partialdate_tags %}
{% load fb_versions %}

{% if latexmode %}.. _note-{{ object.id }}:{% endif %}

{{ object.title|safe }}
=============================================================================


{{ object.text|safe }}

Autor{% if object.authors.count > 1 %}en{% endif %}: {% for u in object.authors.all %}{{ u.get_full_name }}{% if forloop.last %}.{% else %}, {% endif %}{% endfor %}

{% include "notaro/sources.rst" with all_sources=object.notesource_set.all %}

{% for pic in object.get_pictures %}
{% if latexmode %}
.. image:: /../media/{{ pic.image }}
    :width: 10cm
{% else %}
.. image:: {% version pic.image 'medium' %}
    :target: {{ pic.get_absolute_url }}
{% endif %}

{{ pic.get_caption|safe }}

{% endfor %}



