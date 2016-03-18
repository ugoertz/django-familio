{% load partialdate_tags %}

{% if event.on_current_site %}
{% if latexmode %}:ref:{% endif %}`{{ event.title }} {% if latexmode %}<{{ event.handle }}>`{% else %}<{% url "event-detail" event.id %}>`__{% endif %}
{% if event.date %}am {{ event.date|partial_date:"j.n.Y" }}{% endif %}
{% if event.place %}in `{{ event.place }} <{% url "place-detail" event.place.id %}>`__ {% endif %}

{% if not latexmode %}
.. class:: small

{{ event.description_indented }}
{% endif %}
{% else %}
{{ event.title }}
{% endif %}
