---
layout: default
title: Home
description: Classroom situations, useful readings and teachers' own work. Maintained by Vicharanashala, the Lab for Education Design at IIT Ropar.
---

<section class="ta-hero ta-hero-split">
  <div>
    <p class="ta-kicker">Teacharcha</p>
    <h1>Every teacher knows the "what do I do now?" moment.</h1>
    <p>Teacharcha brings you those moments, the readings that can help, and work shared by teachers like you.</p>
    <div class="ta-actions">
      <a class="ta-button ta-button-warm" href="{{ '/resources/' | relative_url }}">Try a situation</a>
      <a class="ta-button ta-button-light" href="{{ '/projects/' | relative_url }}">See teachers' projects</a>
    </div>
  </div>
  <div class="ta-bubbles" aria-hidden="true">
    <span>Was this report written by AI?</span>
    <span>Nobody answered my question today.</span>
    <span>Marks are due on Friday!</span>
    <span>How do I reach the back bench?</span>
  </div>
</section>

<section class="ta-goal">
  <p class="ta-kicker">Our goal</p>
  <h2>No teacher should have to figure it out alone.</h2>
  <div class="ta-offer-grid">
    <div class="ta-offer">
      <i class="ph ph-chats-circle" aria-hidden="true"></i>
      <div>
        <h3><a href="{{ '/resources/' | relative_url }}">Situations and readings</a></h3>
        <p>A classroom moment, your decision, and a reading that helps.</p>
      </div>
    </div>
    <div class="ta-offer">
      <i class="ph ph-chalkboard-teacher" aria-hidden="true"></i>
      <div>
        <h3><a href="{{ '/projects/' | relative_url }}">Teachers' projects</a></h3>
        <p>Resources made by teachers, ready for another teacher to try.</p>
      </div>
    </div>
    <div class="ta-offer">
      <i class="ph ph-users-three" aria-hidden="true"></i>
      <div>
        <h3><a href="{{ '/community/' | relative_url }}">Discipline networks</a></h3>
        <p>Find teachers of your subject in other colleges.</p>
      </div>
    </div>
    <div class="ta-offer">
      <i class="ph ph-microphone" aria-hidden="true"></i>
      <div>
        <h3>Podcast</h3>
        <p>Conversations about real classrooms. <span class="ta-later">Coming later</span></p>
      </div>
    </div>
  </div>
</section>

{% assign latest = site.resources | sort: "added" | reverse | first %}
{% if latest %}
<section class="ta-section">
  <h2>This week's situation</h2>
  <div class="ta-resource-list">
    {% include resource-card.html resource=latest %}
  </div>
</section>
{% endif %}

<section class="ta-section">
  <h2>Teachers' projects</h2>
  {% assign shown = site.data.projects | where: "permission_given", true %}
  {% if shown and shown.size > 0 %}
    <div class="ta-project-grid">
      {% for project in shown limit: 3 %}
        {% include project-card.html project=project %}
      {% endfor %}
    </div>
    <p><a href="{{ '/projects/' | relative_url }}">See all projects</a></p>
  {% else %}
    {% include projects-empty.html %}
  {% endif %}
</section>

{% include come-back.html %}
