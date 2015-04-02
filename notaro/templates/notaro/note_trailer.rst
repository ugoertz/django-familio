
`{{ note.title|safe }} <{% url "note-detail" note.id %}>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

{{ note.get_trailer|safe }}

