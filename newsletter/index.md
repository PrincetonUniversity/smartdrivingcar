---
layout: default
title: Newsletter Archive
permalink: /newsletter/
---

<h1>SmartDrivingCars Newsletter</h1>

<p class="newsletter-actions">
  <a class="btn manage-subscription" href="https://kornhauser.princeton.edu/newsletter">Manage Subscription</a>
</p>

<h2>Browse by Year</h2>
<ul>
{% assign years_seen = "" %}
{% assign issues = site.newsletters | sort: 'date' | reverse %}
{% for issue in issues %}
  {% assign issue_year = issue.date | date: '%Y' %}
  {% unless years_seen contains issue_year %}
    {% assign years_seen = years_seen | append: issue_year | append: "," %}
  <li><a href="/newsletter/{{ issue_year }}/">{{ issue_year }}</a></li>
  {% endunless %}
{% endfor %}
</ul>

<h2>Recent Issues</h2>
<ul class="newsletter-archive">
{% for issue in issues %}
  <li>
    <a href="{{ issue.url }}"><time datetime="{{ issue.date | date_to_xmlschema }}">{{ issue.date | date: '%Y-%m-%d' }}</time> – {% if issue.display_name %}{{ issue.display_name }}{% else %}{{ issue.title }}{% endif %}</a>
  </li>
{% endfor %}
</ul>
