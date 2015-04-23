{% if all_sources %}
Quellenangaben
--------------

{% for s in all_sources %}

{% if s.source.on_current_site %}
{% if latexmode %}
:ref:`{{ s.source.name }} <source-{{ s.source.id }}>` {% if s.comment %}({{ s.comment }}){% endif %}
{% else %}
`{{ s.source.name }} <{% url "source-detail" s.source.id %}>`__ {% if s.comment %}({{ s.comment }}){% endif %}
{% endif %}
{% else %}
{{ s.source.name }} {% if s.comment %}({{ s.comment }}){% endif %}
{% endif %}
{% endfor %}
{% endif %}
