{% if deeper_signals %}

## 🔍 Advanced GitHub Analytics (GraphQL API)

### Contribution Overview

```json
{
  "total_contributions": {
    "commits": {{ deeper_signals.contributions.total_commits if deeper_signals.contributions else 0 }},
    "issues": {{ deeper_signals.contributions.total_issues if deeper_signals.contributions else 0 }},
    "pull_requests": {{ deeper_signals.contributions.total_prs if deeper_signals.contributions else 0 }},
    "reviews": {{ deeper_signals.contributions.total_reviews if deeper_signals.contributions else 0 }},
    "activity_intensity": "{{ deeper_signals.contributions.activity_intensity if deeper_signals.contributions else 'Low' }}"
  },
  "professional_indicators": {
    "collaboration_strength": "{{ deeper_signals.professional_indicators.collaboration_strength if deeper_signals.professional_indicators else 'Low' }}",
    "community_engagement": "{{ deeper_signals.professional_indicators.community_engagement if deeper_signals.professional_indicators else 'Low' }}",
    "technical_leadership": "{{ deeper_signals.professional_indicators.technical_leadership if deeper_signals.professional_indicators else 'Low' }}",
    "consistency_score": {{ deeper_signals.professional_indicators.consistency_score if deeper_signals.professional_indicators else 0 }}
  }
}
```

### 🚀 Community Engagement Matrix

| Activity Category         | Volume                                                                                  | Quality Indicator                                                                                                  | Engagement Level                                                                                                                                                                     |
| ------------------------- | --------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Pull Request Reviews**  | {{ deeper_signals.pull_requests.reviews_given if deeper_signals.pull_requests else 0 }} | Collaboration Score: {{ deeper_signals.pull_requests.collaboration_score if deeper_signals.pull_requests else 0 }} | {% if (deeper_signals.pull_requests.reviews_given or 0) >= 50 %}🔥 High{% elif (deeper_signals.pull_requests.reviews_given or 0) >= 15 %}⚡ Medium{% else %}📊 Developing{% endif %} |
| **Issue Engagement**      | {{ deeper_signals.issues.comments_authored if deeper_signals.issues else 0 }}           | Issues Assigned: {{ deeper_signals.issues.assigned_issues if deeper_signals.issues else 0 }}                       | {% if (deeper_signals.issues.comments_authored or 0) >= 100 %}🔥 High{% elif (deeper_signals.issues.comments_authored or 0) >= 25 %}⚡ Medium{% else %}📊 Developing{% endif %}      |
| **Discussion Leadership** | {{ deeper_signals.discussions.threads_started if deeper_signals.discussions else 0 }}   | Discussion Comments: {{ deeper_signals.discussions.comments_authored if deeper_signals.discussions else 0 }}       | {% if (deeper_signals.discussions.threads_started or 0) >= 10 %}🔥 High{% elif (deeper_signals.discussions.threads_started or 0) >= 3 %}⚡ Medium{% else %}📊 Developing{% endif %}  |
| **Project Management**    | {{ deeper_signals.projects.projects_created if deeper_signals.projects else 0 }}        | Project Items: {{ deeper_signals.projects.items_added if deeper_signals.projects else 0 }}                         | {% if (deeper_signals.projects.projects_created or 0) >= 5 %}🔥 High{% elif (deeper_signals.projects.projects_created or 0) >= 2 %}⚡ Medium{% else %}📊 Developing{% endif %}       |

### 💻 Code Collaboration Analysis

{% if deeper_signals.pull_requests and (deeper_signals.pull_requests.total or 0) > 0 %}

**Pull Request Portfolio:**

- **Total PRs:** {{ deeper_signals.pull_requests.total }} ({{ deeper_signals.pull_requests.merged }} merged, {{ deeper_signals.pull_requests.open }} open)
- **Average PR Size:** {{ deeper_signals.pull_requests.avg_pr_size }} lines changed
- **Code Review Engagement:** {{ deeper_signals.pull_requests.reviews_given }} reviews given, {{ deeper_signals.pull_requests.reviews_received }} received
- **Collaboration Style:** {% if (deeper_signals.pull_requests.collaboration_score or 0) > 1.5 %}🤝 Highly Collaborative{% elif (deeper_signals.pull_requests.collaboration_score or 0) > 0.8 %}👥 Team Player{% else %}🔨 Independent Contributor{% endif %}

{% else %}
**Pull Request Activity:** Getting started with collaborative development
{% endif %}

### 🎯 Issue Management & Problem Solving

{% if deeper_signals.issues and (deeper_signals.issues.opened or deeper_signals.issues.closed or 0) > 0 %}

**Issue Resolution Profile:**

- **Issues Opened:** {{ deeper_signals.issues.opened }} | **Closed:** {{ deeper_signals.issues.closed }}
- **Resolution Rate:** {% if (deeper_signals.issues.opened or 0) > 0 %}{{ "%.1f"|format((deeper_signals.issues.closed or 0) / deeper_signals.issues.opened * 100) }}%{% else %}N/A{% endif %}
- **Discussion Contributions:** {{ deeper_signals.issues.comments_authored }} comments across issues
- **Responsibility Level:** {% if (deeper_signals.issues.assigned_issues or 0) > 10 %}🎯 High Ownership{% elif (deeper_signals.issues.assigned_issues or 0) > 3 %}📋 Regular Contributor{% else %}💭 Community Helper{% endif %}

{% else %}
**Issue Engagement:** Opportunity for more community problem-solving involvement
{% endif %}

### 🗣️ Community Discussion Leadership

{% if deeper_signals.discussions and ((deeper_signals.discussions.threads_started or 0) > 0 or (deeper_signals.discussions.comments_authored or 0) > 0) %}

**Discussion Engagement:**

- **Threads Initiated:** {{ deeper_signals.discussions.threads_started }} (driving community conversations)
- **Discussion Comments:** {{ deeper_signals.discussions.comments_authored }} (active participant)
- **Discussion Categories:** {% if deeper_signals.discussions.categories_engaged %}{{ deeper_signals.discussions.categories_engaged | join(', ') }}{% else %}Various topics{% endif %}
- **Community Role:** {% if (deeper_signals.discussions.threads_started or 0) >= 5 %}🌟 Discussion Leader{% elif (deeper_signals.discussions.comments_authored or 0) >= 20 %}💬 Active Contributor{% else %}👂 Engaged Listener{% endif %}

{% else %}
**Discussion Activity:** Potential for increased community discussion involvement
{% endif %}

### 🌐 Social & Network Influence

**Social Metrics:**

- **Followers:** {{ deeper_signals.social_metrics.followers if deeper_signals.social_metrics else 0 }} | **Following:** {{ deeper_signals.social_metrics.following if deeper_signals.social_metrics else 0 }}
- **Starred Repositories:** {{ deeper_signals.social_metrics.starred_repos if deeper_signals.social_metrics else 0 }} (interests & learning)
- **Watching:** {{ deeper_signals.social_metrics.watching if deeper_signals.social_metrics else 0 }} (staying informed)
- **Public Gists:** {{ deeper_signals.social_metrics.gists if deeper_signals.social_metrics else 0 }} (knowledge sharing)

{% if deeper_signals.social_metrics and deeper_signals.social_metrics.organizations %}
**Organizational Affiliations:**
{% for org in deeper_signals.social_metrics.organizations[:5] %}

- **{{ org.name or org.login }}** {% if org.description %}— {{ org.description[:80] }}{% if org.description|length > 80 %}...{% endif %}{% endif %}
  {% endfor %}
  {% endif %}

### 🎁 Sponsorship & Open Source Support

{% if deeper_signals.sponsorship %}
**Sponsorship Activity:**

- **GitHub Sponsors:** {% if deeper_signals.sponsorship.sponsors_enabled %}✅ Enabled{% else %}Not Set Up{% endif %}
- **Sponsoring Others:** {{ deeper_signals.sponsorship.sponsoring_others }} developers/projects
- **Sponsored Projects:** {{ deeper_signals.sponsorship.sponsored_projects }} receiving support

{% if deeper_signals.sponsorship.sponsors_enabled or (deeper_signals.sponsorship.sponsoring_others or 0) > 0 %}
**Open Source Philosophy:** {% if deeper_signals.sponsorship.sponsors_enabled and (deeper_signals.sponsorship.sponsoring_others or 0) > 0 %}🌟 Active Ecosystem Participant{% elif deeper_signals.sponsorship.sponsors_enabled %}💝 Open to Support{% elif (deeper_signals.sponsorship.sponsoring_others or 0) > 0 %}🤲 Supporting Others{% else %}🔄 Growing Involvement{% endif %}
{% endif %}
{% endif %}

### 📊 Professional Development Indicators

**Technical Leadership Score:** {{ deeper_signals.professional_indicators.technical_leadership if deeper_signals.professional_indicators else 'Low' }}

- Based on code reviews, project management, issue assignments, and discussion leadership

**Collaboration Strength:** {{ deeper_signals.professional_indicators.collaboration_strength if deeper_signals.professional_indicators else 'Low' }}

- Measured through peer interactions, reviews, and community engagement

**Community Engagement:** {{ deeper_signals.professional_indicators.community_engagement if deeper_signals.professional_indicators else 'Low' }}

- Reflects involvement in discussions, sponsorship, and organizational participation

**Consistency Score:** {{ deeper_signals.professional_indicators.consistency_score if deeper_signals.professional_indicators else 0 }}/100

- Annual contribution frequency and regularity patterns

---

_Advanced metrics powered by GitHub GraphQL API — providing insights into collaboration patterns, technical leadership, and community engagement beyond basic repository statistics._

{% endif %}
