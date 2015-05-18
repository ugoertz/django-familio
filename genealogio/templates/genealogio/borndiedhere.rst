{% if born_close_by or died_close_by or born_here or died_here %}

Personen
--------

.. raw:: html

  <div class="row"><div class="col-md-6">

{% if born_here %}
**Hier geboren:**

{% for person in born_here %}
* {% include "genealogio/person_snippet.rst" %}
{% endfor %}
{% endif %}

.. raw:: html

  </div><div class="col-md-6">

{% if died_here %}

**Hier gestorben:**

{% for person in died_here %}
* {% include "genealogio/person_snippet.rst" %}
{% endfor %}
{% endif %}

.. raw:: html

  </div></div>
  <div class="row"><div class="col-md-6">

{% if born_close_by %}
**In der Nähe geboren:**

{% for place_id, data in born_close_by.items %}
`{{ data.place }} <{{ data.place.get_absolute_url }}>`__  ({{ data.distance.km|floatformat:"0" }} km)

{% for person in data.persons %}
* {% include "genealogio/person_snippet.rst" %}
{% endfor %}
{% endfor %}
{% endif %}

.. raw:: html

  </div><div class="col-md-6">


{% if died_close_by %}
**In der Nähe gestorben:**

{% for place_id, data in died_close_by.items %}
`{{ data.place }} <{{ data.place.get_absolute_url }}>`__  ({{ data.distance.km|floatformat:"0" }} km)

{% for person in data.persons %}
* {% include "genealogio/person_snippet.rst" %}
{% endfor %}
{% endfor %}
{% endif %}

.. raw:: html

  </div></div>

{% endif %}



