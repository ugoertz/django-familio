{% if person %}{% if person.on_current_site %}`{{ person.get_primary_name }} <{{ person.get_absolute_url }}>`__ {% else %}{{ person.get_primary_name }}{% endif %}{% else %}*unbekannt*{% endif %}
