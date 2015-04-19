{% load partialdate_tags %}


{{ object.title|safe }}
-----------------------------------------------------------------------------------------------------------------------------------------------------

{{ object.start_date|partial_date:"d.m.Y" }}{% if object.end_date %} - {{ object.end_date|partial_date:"d.m.Y" }}{% endif %}


{{ object.description|safe }}


