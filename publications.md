---
layout: page
title: Publications
---

{% assign pubs = site.data.publications.items %}

Last updated: {{ site.data.publications.generated_at }}

{% if pubs == nil or pubs.size == 0 %}
No publications found. (Check ORCID visibility / API fetch)
{% else %}

<ul>
{% for p in pubs %}
  <li>
    {% if p.year %}<strong>{{ p.year }}</strong> — {% endif %}
    {{ p.title }}
    {% if p.journal %}<em> ({{ p.journal }})</em>{% endif %}
    {% if p.doi %}
      — <a href="https://doi.org/{{ p.doi }}">DOI</a>
    {% elsif p.url %}
      — <a href="{{ p.url }}">Link</a>
    {% endif %}
  </li>
{% endfor %}
</ul>

{% endif %}
