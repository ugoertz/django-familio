
`{{ note.title|safe }} <{% url "note-detail" note.id %}>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

{% if not latexmode %}
{{ note.get_trailer|safe }}
{% endif %}

