{% if linkedin_enrichment and linkedin_enrichment.profiles %}

### LinkedIn Professional Profile Data

```json
{
  "profile_url": "{{ linkedin_enrichment.profiles[0].url if linkedin_enrichment.profiles[0].url else 'unknown' }}",
  "professional_headline": {{ linkedin_enrichment.enrichment_summary.headline|tojson if linkedin_enrichment.enrichment_summary.headline else 'null' }},
  "location": {{ linkedin_enrichment.enrichment_summary.location|tojson if linkedin_enrichment.enrichment_summary.location else 'null' }},
  "industry": {{ linkedin_enrichment.enrichment_summary.industry|tojson if linkedin_enrichment.enrichment_summary.industry else 'null' }},
  "data_freshness": "{{ linkedin_enrichment.profiles[0].extracted_at if linkedin_enrichment.profiles[0].extracted_at else 'unknown' }}",
  "education_entries": {{ linkedin_enrichment.enrichment_summary.education_count if linkedin_enrichment.enrichment_summary.education_count else 0 }},
  "certifications": {{ linkedin_enrichment.enrichment_summary.certification_count if linkedin_enrichment.enrichment_summary.certification_count else 0 }},
  "experience_entries": {{ linkedin_enrichment.enrichment_summary.experience_count if linkedin_enrichment.enrichment_summary.experience_count else 0 }},
  "skills_listed": {{ linkedin_enrichment.enrichment_summary.skills_count if linkedin_enrichment.enrichment_summary.skills_count else 0 }}
}
```

{% if linkedin_enrichment.enrichment_summary.headline %}

### Professional Summary

**Professional Headline:** {{ linkedin_enrichment.enrichment_summary.headline }}

{% if linkedin_enrichment.enrichment_summary.industry %}**Industry:** {{ linkedin_enrichment.enrichment_summary.industry }}{% endif %}

{% if linkedin_enrichment.enrichment_summary.location %}**Location:** {{ linkedin_enrichment.enrichment_summary.location }}{% endif %}

{% endif %}

{% set primary_profile = linkedin_enrichment.profiles[0].profile_data %}

{% if primary_profile.education and primary_profile.education|length > 0 %}

### Education Background

{% for education in primary_profile.education %}

```json
{
  "institution": {{ education.institution|tojson if education.institution else 'null' }},
  "degree": {{ education.degree|tojson if education.degree else 'null' }},
  "field_of_study": {{ education.field_of_study|tojson if education.field_of_study else 'null' }},
  "years": {{ education.years|tojson if education.years else 'null' }},
  "description": {{ education.description|tojson if education.description else 'null' }}
}
```

{% endfor %}

#### Education Summary

| Institution | Degree | Field of Study | Years |
| ----------- | ------ | -------------- | ----- |

{% for education in primary_profile.education %}
| {{ education.institution if education.institution else 'N/A' }} | {{ education.degree if education.degree else 'N/A' }} | {{ education.field_of_study if education.field_of_study else 'N/A' }} | {{ education.years if education.years else 'N/A' }} |
{% endfor %}

{% endif %}

{% if primary_profile.certifications and primary_profile.certifications|length > 0 %}

### Professional Certifications

{% for cert in primary_profile.certifications %}

```json
{
  "certification_name": {{ cert.name|tojson if cert.name else 'null' }},
  "issuing_organization": {{ cert.issuing_organization|tojson if cert.issuing_organization else 'null' }},
  "issue_date": {{ cert.issue_date|tojson if cert.issue_date else 'null' }},
  "expiration_date": {{ cert.expiration_date|tojson if cert.expiration_date else 'null' }},
  "credential_id": {{ cert.credential_id|tojson if cert.credential_id else 'null' }},
  "credential_url": {{ cert.credential_url|tojson if cert.credential_url else 'null' }}
}
```

{% endfor %}

#### Certifications Summary

| Certification | Issuing Organization | Issue Date | Status |
| ------------- | -------------------- | ---------- | ------ |

{% for cert in primary_profile.certifications %}
| {{ cert.name if cert.name else 'N/A' }} | {{ cert.issuing_organization if cert.issuing_organization else 'N/A' }} | {{ cert.issue_date if cert.issue_date else 'N/A' }} | {% if cert.expiration_date %}Expires {{ cert.expiration_date }}{% else %}No expiration{% endif %} |
{% endfor %}

{% endif %}

{% if primary_profile.experience and primary_profile.experience|length > 0 %}

### Professional Experience (LinkedIn)

{% for exp in primary_profile.experience %}

```json
{
  "position_title": {{ exp.title|tojson if exp.title else 'null' }},
  "company": {{ exp.company|tojson if exp.company else 'null' }},
  "duration": {{ exp.duration|tojson if exp.duration else 'null' }},
  "location": {{ exp.location|tojson if exp.location else 'null' }},
  "description": {{ exp.description|tojson if exp.description else 'null' }}
}
```

{% endfor %}

#### Experience Summary

| Position | Company | Duration | Location |
| -------- | ------- | -------- | -------- |

{% for exp in primary_profile.experience %}
| {{ exp.title if exp.title else 'N/A' }} | {{ exp.company if exp.company else 'N/A' }} | {{ exp.duration if exp.duration else 'N/A' }} | {{ exp.location if exp.location else 'N/A' }} |
{% endfor %}

{% endif %}

{% if primary_profile.skills and primary_profile.skills|length > 0 %}

### LinkedIn Skills & Endorsements

```json
{
  "total_skills": {{ primary_profile.skills|length }},
  "skills_list": {{ primary_profile.skills|tojson }}
}
```

**Skills:** {{ primary_profile.skills|join(', ') }}

{% endif %}

### LinkedIn Data Quality Assessment

| Data Category             | Status                                                                       | Count                                                    |
| ------------------------- | ---------------------------------------------------------------------------- | -------------------------------------------------------- | --------------------------------- | -------------------------------------------------- |
| **Professional Headline** | {% if primary_profile.headline %}✅ Available{% else %}❌ Missing{% endif %} | {% if primary_profile.headline %}1{% else %}0{% endif %} |
| **Education**             | {% if primary_profile.education and primary_profile.education                | length > 0 %}✅ Available{% else %}❌ Missing{% endif %} | {{ primary_profile.education      | length if primary_profile.education else 0 }}      |
| **Certifications**        | {% if primary_profile.certifications and primary_profile.certifications      | length > 0 %}✅ Available{% else %}❌ Missing{% endif %} | {{ primary_profile.certifications | length if primary_profile.certifications else 0 }} |
| **Experience**            | {% if primary_profile.experience and primary_profile.experience              | length > 0 %}✅ Available{% else %}❌ Missing{% endif %} | {{ primary_profile.experience     | length if primary_profile.experience else 0 }}     |
| **Skills**                | {% if primary_profile.skills and primary_profile.skills                      | length > 0 %}✅ Available{% else %}❌ Missing{% endif %} | {{ primary_profile.skills         | length if primary_profile.skills else 0 }}         |

### LinkedIn vs GitHub Data Correlation

{% if linkedin_enrichment.enrichment_summary.headline and bio %}
**Professional Consistency:** LinkedIn headline matches GitHub bio context: {% if linkedin_enrichment.enrichment_summary.headline.lower() in bio.lower() or bio.lower() in linkedin_enrichment.enrichment_summary.headline.lower() %}✅ Consistent{% else %}⚠️ Different focus areas{% endif %}
{% endif %}

{% if linkedin_enrichment.enrichment_summary.location and location %}
**Location Consistency:** LinkedIn ({{ linkedin_enrichment.enrichment_summary.location }}) vs GitHub ({{ location }}): {% if linkedin_enrichment.enrichment_summary.location.lower() == location.lower() %}✅ Match{% else %}⚠️ Different{% endif %}
{% endif %}

**Professional Data Completeness:**

- GitHub provides: Development portfolio, technical skills, project history
- LinkedIn provides: {% if primary_profile.headline %}Professional headline, {% endif %}{% if primary_profile.education %}Education background, {% endif %}{% if primary_profile.certifications %}Certifications, {% endif %}{% if primary_profile.experience %}Work experience{% endif %}
- **Data Integration Value:** {% if linkedin_enrichment.enrichment_summary.has_professional_data %}High - LinkedIn adds significant professional context{% else %}Limited - Minimal additional data available{% endif %}

{% endif %}
