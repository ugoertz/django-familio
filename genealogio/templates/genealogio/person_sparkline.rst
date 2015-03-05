{% if person.on_current_site %}
.. |{{ label }}| replace::
    {% if person %}|{{ label }}link|_{% else %}*unbekannt*{% endif %}

{% if person %}
.. |{{ label }}link| replace::
    {{ person.get_primary_name_br }} |br| ({{ person.datebirth.year }} - {{ person.datedeath.year }})

.. _{{ label }}link: {{ person.get_absolute_url }}
{% endif %}

.. |img{{ label }}| image:: /gen/sparkline/{{ person.id }}/{{ fr }}/{{ to }}/
{% endif %}

