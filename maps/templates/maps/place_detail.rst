{% load gen_place_tags %}
{% load partialdate_tags %}

{{ object.title }}
===============================================================================

{% for plurl in object.placeurl_set.all %}
* `{{ plurl.url.title }} <{{ plurl.url.link }}>`__
{% endfor %}


{% related_people place=object %}

{% with events=object.event_set.all %}
{% if events %}
Ereignisse
------------------------

{% for evt in object.event_set.all %}
`{{ evt.title }} <{{ evt.get_absolute_url }}>`__ {% if evt.date %}({{ evt.date|partial_date:"j.n.Y" }}){% endif %}

{% endfor %}
{% endif %}
{% endwith %}



