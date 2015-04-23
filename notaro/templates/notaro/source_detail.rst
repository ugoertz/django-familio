
{% load partialdate_tags %}
{% load fb_versions %}

{% if latexmode %}.. _source-{{ object.id }}:{% endif %}

{{ object.name|safe }}
=============================================================================


{{ object.description|safe }}




