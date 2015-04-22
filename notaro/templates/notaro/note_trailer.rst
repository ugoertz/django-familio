
{% if latexmode %}
:ref:`{{ note.title|safe }} <note-{{ note.id  }}>`
{% else %}
`{{ note.title|safe }} <{% url "note-detail" note.id %}>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

{{ note.get_trailer|safe }}
{% endif %}

