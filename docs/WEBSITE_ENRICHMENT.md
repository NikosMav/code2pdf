# Website Enrichment with MCP Firecrawl Integration

This document describes the comprehensive website enrichment system that enhances GitHub profiles by crawling personal websites using MCP Firecrawl tools.

## 🌟 Overview

The website enrichment system automatically discovers personal websites linked in GitHub profiles and uses Firecrawl to extract additional professional information. This creates more complete and insightful user profiles that combine GitHub activity with personal website content.

## 🚀 Key Features

### ✅ Automatic Website Discovery

- Extracts URLs from GitHub profile `blog` field
- Scans bio text for personal website links
- Discovers GitHub Pages sites from repositories
- Intelligent validation to identify personal websites

### ✅ Smart Website Filtering

- Filters out social media and platform sites
- Focuses on personal portfolios, blogs, and professional sites
- Supports common personal website patterns (GitHub Pages, Netlify, Vercel, etc.)

### ✅ Firecrawl Integration

- Uses MCP Firecrawl tools for robust website scraping
- Extracts structured data using AI-powered analysis
- Handles dynamic content with configurable wait times
- Graceful fallback when Firecrawl is unavailable

### ✅ Rich Data Extraction

- **Personal Information**: Name, title, bio, contact details
- **Professional Skills**: Technical competencies and expertise levels
- **Work Experience**: Detailed employment history and achievements
- **Education**: Academic background and certifications
- **Projects**: Notable work and portfolio pieces
- **Services**: Professional offerings and specializations

## 📋 Usage

### Basic Usage with CLI

```bash
# Generate CV with website enrichment
code2pdf build username --enrich-websites

# Verbose output to see enrichment process
code2pdf build username --enrich-websites --verbose

# Generate multiple formats with enrichment
code2pdf build username --enrich-websites --format all --theme modern
```

### Programmatic Usage

```python
from code2pdf.github import fetch_profile
from code2pdf.generator import render_markdown

# Fetch profile with website enrichment
profile = fetch_profile("username", enrich_websites=True, verbose=True)

# Generate enhanced CV
render_markdown(profile, "enhanced_cv.md", "professional")
```

## 🔧 MCP Integration

In an MCP-enabled environment, the system automatically uses Firecrawl tools:

```python
# The system will automatically detect and use MCP tools
profile = fetch_profile("username", enrich_websites=True)
```

## 📊 Performance

- **Intelligent Caching**: 24-hour website cache, 1-hour GitHub cache
- **Rate Limiting**: Maximum 3 websites per profile
- **Processing Time**: 5-15 seconds total enrichment time
- **Fallback Behavior**: Graceful handling when Firecrawl unavailable

## ✅ Flexibility Demonstrated

The system has been tested with diverse GitHub profiles and demonstrates:

- ✅ **Handles profiles WITHOUT websites** - Graceful fallback to GitHub-only data
- ✅ **Handles profiles WITH invalid websites** - Smart filtering of platform sites
- ✅ **Handles profiles WITH valid websites** - Rich data extraction and CV enhancement
- ✅ **Consistent quality** - Professional CVs regardless of enrichment status

## 📁 Examples

See the `/examples` folder for demonstration scripts showing different use cases and integration patterns.

## 🧪 Testing

See the `/tests` folder for comprehensive test suites validating the enrichment system with various GitHub profile types.
