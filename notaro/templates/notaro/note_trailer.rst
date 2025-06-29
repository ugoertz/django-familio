
{% if latexmode %}
:ref:`{{ note.title|safe }} <note-{{ note.id  }}>`
{% else %}
`{{ note.title|safe }} <{{ note.get_absolute_url }}>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

{{ note.get_trailer|safe }}
{% endif %}

