{% if object.events.count %}

Ereignisse
----------

{% for event in object.events.on_site %}
{% include "genealogio/event_snippet.rst" with person=object %}
{% endfor %}
{% endif %}


