{% load gen_place_tags %}

{{ object.title }}
===============================================================================

{% for plurl in object.placeurl_set.all %}
* `{{ plurl.url.title }} <{{ plurl.url.link }}>`__
{% endfor %}


{% related_people place=object %}




