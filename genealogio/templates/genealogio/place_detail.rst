
{{ object.title }}
===============================================================================

{% for plurl in object.placeurl_set.all %}
* `{{ plurl.url.title }} <{{ plurl.url.link }}>`__
{% endfor %}


{% with object.born_here as born_here %}
{% if born_here %}
Personen, die hier geboren sind
-------------------------------

{% for person in born_here %}
* {% include "genealogio/person_snippet.rst" %}
{% endfor %}
{% endif %}
{% endwith %}

{% with object.died_here as died_here %}
{% if died_here %}

Personen, die hier gestorben sind
---------------------------------

{% for person in died_here %}
* {% include "genealogio/person_snippet.rst" %}
{% endfor %}
{% endif %}
{% endwith %}





