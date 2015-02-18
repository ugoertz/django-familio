{% if person %}`{{ person.get_primary_name }} <{{ person.get_absolute_url }}>`__ ({{ person.datebirth.year }} - {{ person.datedeath.year }}){% else %}*unbekannt*{% endif %}
