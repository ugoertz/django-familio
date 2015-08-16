{% load partialdate_tags %}
{% load fb_versions %}

.. role:: underline
    :class: underline

{% if latexmode %}.. _{{ object.handle }}:{% endif %}

{% firstof itemtitle object.get_full_name %}
==============================================================================================================================================================

{% if object.portrait.image %}
{% if latexmode %}
{% if current_site in object.portrait.sites.all %}
.. raw:: latex

    \begin{minipage}[t]{11cm}\vspace{0pt}
{% endif %}
{% else %}
{% if request.site in object.portrait.sites.all %}
.. image:: {% version object.portrait.image 'small' %}
    :class: pull-right
{% endif %}
{% endif %}
{% endif %}

{% if object.datebirth or object.placebirth %}geboren {{ object.datebirth|partial_date:"d.m.Y" }}{% if object.placebirth %} in `{{ object.placebirth }} <{% url "place-detail" object.placebirth.id %}>`__ {% endif %}{% if object.datedeath or object.placedeath %} - {% endif %}{% endif %}{% if object.datedeath or object.placedeath %}gestorben {{ object.datedeath|partial_date:"d.m.Y" }}{% if object.placedeath %} in `{{ object.placedeath }} <{% url "place-detail" object.placedeath.id %}>`__ {% endif %}{% endif %}

{% include "genealogio/person_snippet_full.rst" with person=object.get_father label="**Vater:** " %}

{% include "genealogio/person_snippet_full.rst" with person=object.get_mother label="**Mutter:** " %}

{% with allchildren=object.get_children %}
{% for partner, children, family in allchildren %}

{{ family.get_relation_text }} {% include "genealogio/person_snippet.rst" with person=partner %}{% if latexmode %}. :ref:`Familie {% firstof family.name family %} <{{family.handle}}>`{% else %}— `Familie {% firstof family.name family.father.last_name person.last_name %} <{{ family.get_absolute_url }}>`__{% endif %}

{% if children %}
.. container:: marginleft30

    **Kinder:**

{% for child in children %}
    * {% include "genealogio/person_snippet_full.rst" with person=child %}
{% endfor %}
{% endif %}
{% endfor %}
{% endwith %}

{% if latexmode and object.portrait.image %}
{% if current_site in object.portrait.sites.all %}
.. raw:: latex

    \end{minipage}\hfill
    \begin{minipage}[t]{4cm}\vspace{0pt}

.. image:: /../../../..{% version object.portrait.image 'medium' %}
    :width: 4cm

.. raw:: latex

    \end{minipage}
{% endif %}
{% endif %}

{{ object.comments|safe }}


{% include "genealogio/events.rst" %}

{% if object.personplace_set.count and not hide_places %}

Orte
----

{% for pl in object.personplace_set.all %}
* {% if pl.start and pl.start != pl.end %}{{ pl.start|partial_date:"d.m.Y" }}{% endif %}{% if pl.start and pl.end and pl.start != pl.end %} - {% endif %}{{ pl.end|partial_date:"d.m.Y" }}{% if pl.start or pl.end %}: {% endif %} `{{ pl.place }} <{{ pl.place.get_absolute_url }}>`__ ({{ pl.get_typ_display }})
{% endfor %}
{% endif %}

{% include "genealogio/notes.rst" %}

{% include "notaro/sources.rst" with all_sources=object.personsource_set.all %}
