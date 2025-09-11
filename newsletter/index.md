---
layout: default
title: Newsletter Archive
permalink: /newsletter/
---

<h1>SmartDrivingCars Newsletter</h1>

<ul class="newsletter-archive">
{% assign issues = site.newsletters | sort: 'date' | reverse %}
{% for issue in issues %}
  <li>
    <a href="{{ issue.url }}"><time datetime="{{ issue.date | date_to_xmlschema }}">{{ issue.date | date: '%Y-%m-%d' }}</time> – {{ issue.title }}</a>
  </li>
{% endfor %}
</ul>
