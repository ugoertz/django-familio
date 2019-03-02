{% if object.notes.count %}

Texte
-----

{% for note in object.notes.on_site %}
{% if note.published %}
{% include "notaro/note_trailer.rst" %}
{% endif %}
{% endfor %}
{% endif %}


