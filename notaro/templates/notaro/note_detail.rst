{% load partialdate_tags %}
{% load fb_versions %}


{{ object.title|safe }}
=============================================================================


{{ object.text|safe }}

Autor{% if object.authors.count > 1 %}en{% endif %}: {% for u in object.authors.all %}{{ u.get_full_name }}{% if forloop.last %}.{% else %}, {% endif %}{% endfor %}

{% for pic in object.get_pictures %}
{% if latexmode %}
.. image:: /../media/{{ pic.image }}
    :width: 10cm
{% else %}
.. image:: {% version pic.image 'medium' %}
{% endif %}

{{ pic.get_caption|safe }}

{% endfor %}



