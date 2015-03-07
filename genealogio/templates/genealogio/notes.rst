{% if object.notes.count %}
-----
Texte
-----

{% for note in object.notes.on_site %}
{% include "notaro/note_trailer.rst" %}
{% endfor %}
{% endif %}


