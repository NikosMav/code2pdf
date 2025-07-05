{% if profile_readme and profile_readme.has_profile_readme %}

## 👤 Profile README

_Raw content from GitHub Profile README_

### 📄 README Content

**Content Length:** {{ profile_readme.length }} characters

{% if profile_readme.content %}

```markdown
{{ profile_readme.content }}
```

{% endif %}

---

_This section contains the raw content from the user's GitHub profile README ({{ profile_readme.length }} characters)._

{% endif %}
