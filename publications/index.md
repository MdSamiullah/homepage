---
layout: default
title: Publications
permalink: /publications/
---

Below is a curated list of my publications. For a complete list, see my Google Scholar/ResearchGate profiles.

{% assign pubs = site.data.publications | sort: "year" | reverse %}
{% assign years = pubs | map: "year" | uniq %}

{% for y in years %}
## {{ y }}

{% assign by_year = pubs | where: "year", y %}
{% for p in by_year %}
<div class="pub-card">
  <div class="pub-title">{{ p.title }}</div>
  <p class="pub-meta"><b>Authors:</b> {{ p.authors }}</p>
  <p class="pub-meta"><b>Venue:</b> {{ p.venue }}{% if p.type %} · <b>Type:</b> {{ p.type }}{% endif %}</p>

  <div class="pub-links">
    {% if p.pdf and p.pdf != "" %}<a class="pub-btn" href="{{ p.pdf }}" target="_blank" rel="noreferrer">PDF</a>{% endif %}
    {% if p.doi and p.doi != "" %}<a class="pub-btn" href="{{ p.doi }}" target="_blank" rel="noreferrer">DOI</a>{% endif %}
    {% if p.code and p.code != "" %}<a class="pub-btn" href="{{ p.code }}" target="_blank" rel="noreferrer">Code</a>{% endif %}
  </div>
</div>
{% endfor %}
{% endfor %}
