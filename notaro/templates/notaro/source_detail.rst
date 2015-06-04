
{% load partialdate_tags %}
{% load fb_versions %}

{% if latexmode %}.. _source-{{ object.id }}:{% endif %}

{% firstof itemtitle object.name|safe %}
==========================================================================================================================================================


{{ object.description|safe }}




