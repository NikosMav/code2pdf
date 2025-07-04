{% if deeper_signals %}

### Deeper GitHub Signals (GraphQL API)

```json
{
  "pr_reviews": {
    "total_reviews": {{ deeper_signals.pr_reviews.total if deeper_signals.pr_reviews else 0 }},
    "approvals_given": {{ deeper_signals.pr_reviews.approvals if deeper_signals.pr_reviews else 0 }},
    "changes_requested": {{ deeper_signals.pr_reviews.request_changes if deeper_signals.pr_reviews else 0 }},
    "approval_ratio": {{ deeper_signals.pr_reviews.approval_ratio if deeper_signals.pr_reviews else 0 }}
  },
  "issue_engagement": {
    "issues_opened": {{ deeper_signals.issues.opened if deeper_signals.issues else 0 }},
    "issues_closed": {{ deeper_signals.issues.closed_by_user if deeper_signals.issues else 0 }},
    "issue_comments": {{ deeper_signals.issues.comments_authored if deeper_signals.issues else 0 }}
  },
  "discussion_activity": {
    "discussions_started": {{ deeper_signals.discussions.threads_started if deeper_signals.discussions else 0 }},
    "discussion_comments": {{ deeper_signals.discussions.comments_authored if deeper_signals.discussions else 0 }}
  },
  "project_management": {
    "project_items_added": {{ deeper_signals.projects.items_added if deeper_signals.projects else 0 }}
  },
  "sponsorship": {
    "sponsors_enabled": {{ deeper_signals.sponsors_enabled|tojson if deeper_signals.sponsors_enabled is defined else 'false' }}
  }
}
```

### Community Engagement Metrics

| Activity Type              | Count                                                                                   | Engagement Level                                                                                                                                           |
| -------------------------- | --------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **PR Reviews**             | {{ deeper_signals.pr_reviews.total if deeper_signals.pr_reviews else 0 }}               | {% if deeper_signals.pr_reviews.total >= 50 %}High{% elif deeper_signals.pr_reviews.total >= 10 %}Medium{% else %}Low{% endif %}                           |
| **Issue Discussions**      | {{ deeper_signals.issues.comments_authored if deeper_signals.issues else 0 }}           | {% if deeper_signals.issues.comments_authored >= 100 %}High{% elif deeper_signals.issues.comments_authored >= 25 %}Medium{% else %}Low{% endif %}          |
| **Repository Discussions** | {{ deeper_signals.discussions.comments_authored if deeper_signals.discussions else 0 }} | {% if deeper_signals.discussions.comments_authored >= 50 %}High{% elif deeper_signals.discussions.comments_authored >= 10 %}Medium{% else %}Low{% endif %} |
| **Project Management**     | {{ deeper_signals.projects.items_added if deeper_signals.projects else 0 }}             | {% if deeper_signals.projects.items_added >= 20 %}High{% elif deeper_signals.projects.items_added >= 5 %}Medium{% else %}Low{% endif %}                    |

### Code Review Analysis

{% if deeper_signals.pr_reviews.total > 0 %}

- **Review Thoroughness:** {{ "High" if deeper_signals.pr_reviews.approval_ratio < 0.8 else "Standard" if deeper_signals.pr_reviews.approval_ratio < 0.95 else "Highly Approving" }}
- **Review Style:** {{ "Constructive" if deeper_signals.pr_reviews.request_changes > 0 else "Supportive" }}
- **Review Volume:** {{ deeper_signals.pr_reviews.total }} total reviews given
  {% else %}
- **Review Activity:** Limited or no PR review activity detected
  {% endif %}

### Issue Management Profile

{% if deeper_signals.issues.opened > 0 %}

- **Issue Resolution Rate:** {{ "%.1f"|format((deeper_signals.issues.closed_by_user / deeper_signals.issues.opened * 100)) }}% ({{ deeper_signals.issues.closed_by_user }}/{{ deeper_signals.issues.opened }} issues closed)
- **Issue Engagement:** {{ deeper_signals.issues.comments_authored }} comments contributed to discussions
  {% else %}
- **Issue Activity:** Limited issue creation or engagement
  {% endif %}

{% endif %}
