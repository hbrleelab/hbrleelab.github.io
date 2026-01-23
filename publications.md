---
title: Publications
permalink: /publications/
layout: single
---

# Publications

Last updated: {{ site.data.publications.generated_at }}

{% assign pubs = site.data.publications.items %}

{% if pubs and pubs.size > 0 %}
{% assign current_year = nil %}

{% for p in pubs %}
{% if p.year != current_year %}
## {{ p.year }}
{% assign current_year = p.year %}
{% endif %}

- {{ p.title }}{% if p.journal %} (*{{ p.journal }}*){% endif %}{% if p.doi %} — [DOI](https://doi.org/{{ p.doi }}){% endif %}
{% endfor %}

{% else %}
No publications found.
{% endif %}
