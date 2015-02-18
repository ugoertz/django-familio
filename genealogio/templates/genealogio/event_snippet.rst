{% load partialdate_tags %}

`{{ event.title }} <{% url "event-detail" event.id %}>`__
{% if event.date %}am {{ event.date|partial_date:"d.m.Y" }}{% endif %}
{% if event.place %}in `{{ event.place }} <{% url "place-detail" event.place.id %}>`__ {% endif %}

{{ event.description }}
