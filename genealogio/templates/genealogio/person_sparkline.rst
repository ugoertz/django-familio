{% if person.on_current_site %}
.. |{{ label }}-{{ object.id|stringformat:"04d" }}| replace::
    {% if person %}|{{ label }}-{{ object.id|stringformat:"04d"  }}link|_{% else %}*unbekannt*{% endif %}

{% if person %}
.. |{{ label }}-{{ object.id|stringformat:"04d"  }}link| replace::
    {{ person.get_primary_name_br }} |br| ({{ person.datebirth.year }} - {{ person.datedeath.year }})

.. _{{ label }}-{{ object.id|stringformat:"04d"  }}link: {% if latexmode %}http://localhost:8000{% endif %}{{ person.get_absolute_url }}
{% endif %}

.. |img{{ label }}-{{ object.id|stringformat:"04d" }}| {% if latexmode %}sparklineimg{% else %}image{% endif %}:: {% url 'sparkline-person' pk=person.id fampk=object.id fr=fr to=to %}
{% endif %}

