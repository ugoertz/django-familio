{% load partialdate_tags %}


{% firstof itemtitle object.title|safe %}
-----------------------------------------------------------------------------------------------------------------------------------------------------

{{ object.start_date|partial_date:"j.n.Y" }}{% if object.end_date %} - {{ object.end_date|partial_date:"j.n.Y" }}{% endif %}


{{ object.description|safe }}


