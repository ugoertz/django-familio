{% if person.on_current_site %}
.. |{{ label }}-{{ object.id|stringformat:"04d" }}| replace::
    {% if person %}|{{ label }}-{{ object.id|stringformat:"04d"  }}link|{% if not latexmode %}_{% endif %}{% else %}*unbekannt*{% endif %}

{% if person %}
.. |{{ label }}-{{ object.id|stringformat:"04d"  }}link| replace::
    {{ person.get_primary_name_br }} |br| ({{ person.datebirth.year }} - {{ person.datedeath.year }})

{% if not latexmode %}
.. _{{ label }}-{{ object.id|stringformat:"04d"  }}link: {{ person.get_absolute_url }}
{% endif %}
{% endif %}

.. |img{{ label }}-{{ object.id|stringformat:"04d" }}| {% if latexmode %}sparklineimg{% else %}image{% endif %}:: {% url 'sparkline-person' pk=person.id fampk=object.id fr=fr to=to %}
{% endif %}

