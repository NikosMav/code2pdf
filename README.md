# GitHub Scraper

Generate professional CVs from GitHub profiles with comprehensive data scraping and analytics.

## 🚀 Features

### **Core Functionality**

- **📄 Markdown Output** - Professional, GitHub-compatible markdown with rich data analysis
- **🎯 Data-Focused** - Comprehensive data scraping and insights without presentation complexity
- **📊 Activity Scoring** - Comprehensive scoring based on stars, forks, and activity
- **💻 Language Analysis** - Programming language expertise with proficiency levels
- **🚀 Project Showcase** - Smart repository selection with diversity analysis

### **Website Enrichment**

- **📝 Personal Website Integration** - Automatically discovers and analyzes personal websites
- **🔍 Smart URL Discovery** - Finds websites from GitHub profile, bio, and repositories
- **🤖 Firecrawl Integration** - Uses advanced web scraping with AI-powered extraction
- **📊 Enhanced Profiles** - Adds skills, experience, and projects from personal websites
- **🛡️ Intelligent Filtering** - Focuses on personal websites, filters out social media

### **Technical Features**

- **⚡ Intelligent Caching** - API response caching for faster subsequent runs
- **🎛️ Configurable Options** - Extensive customization via config files
- **🔄 Rate Limit Friendly** - Optimized API usage with GitHub token support
- **🔍 Deep Analysis** - Comprehensive profile and repository analysis
- **📁 Organized Output** - Automatic folder organization by user and date

## 📦 Installation

### From Source (Recommended)

```bash
git clone https://github.com/nikosmav/github-scraper.git
cd github-scraper
pip install -e ".[dev,all]"
```

### With Optional Features

```bash
# Install with YAML configuration support
pip install -e ".[yaml]"

# Install with all optional features
pip install -e ".[all]"
```

## 🚀 Quick Start

### Basic Usage

```bash
# Generate comprehensive CV with data analysis
github-scraper build username

# Generate with website enrichment (requires Firecrawl API key)
github-scraper build username --enrich-websites --verbose

# Generate with GitHub token for higher rate limits
github-scraper build username --token YOUR_GITHUB_TOKEN
```

### 🌐 Website Enrichment Setup

Website enrichment requires a Firecrawl API key:

1. **Get API Key**: Sign up at [Firecrawl](https://firecrawl.dev/) for a free API key
2. **Set Environment Variable**:

```bash
# Linux/macOS
export FIRECRAWL_API_KEY="your_firecrawl_api_key_here"

# Windows
set FIRECRAWL_API_KEY=your_firecrawl_api_key_here
```

3. **Use with enrichment**:

```bash
github-scraper build username --enrich-websites --verbose
```

### Advanced Usage

```bash
# Custom output directory
github-scraper build username --output-dir team_profiles

# Single file output (bypasses organization)
github-scraper build username --output resume.md

# Disable caching for fresh data
github-scraper build username --no-cache

# Clean up old generated files
github-scraper clean --days 7
```

## 📂 Output Organization

By default, files are organized in structured folders:

```
generated_cvs/
├── username_2024-01-15/
│   └── username_comprehensive_cv.md
└── another_user_2024-01-16/
    └── another_user_comprehensive_cv.md
```

**Organization Options:**

- **Default**: `generated_cvs/{username}_{date}/`
- **Custom directory**: `--output-dir custom_folder/`
- **Single file**: `--output filename.md` (bypasses organization)

## ⚙️ Configuration

Create a `github-scraper.json` or `github-scraper.yaml` file:

```json
{
  "github": {
    "cache_duration_hours": 2,
    "max_repos": 20,
    "include_forks": false
  },
  "cv": {
    "max_featured_repos": 12,
    "include_insights": true,
    "activity_threshold_days": 90
  },
  "output": {
    "include_timestamp": true
  },
  "scraping": {
    "enable_website_enrichment": true,
    "max_websites_per_profile": 5,
    "website_cache_duration_hours": 48
  }
}
```

## 📋 CLI Commands

### `build` - Generate CV

```bash
github-scraper build <username> [OPTIONS]

Options:
  -o, --output PATH          Output file path
  -d, --output-dir PATH      Output directory for organized files
  --enrich-websites          Enable website enrichment
  --token TEXT               GitHub personal access token
  -c, --config PATH          Configuration file path
  --cache/--no-cache         Enable/disable caching
  -v, --verbose              Enable verbose output
```

### Other Commands

```bash
# Clean up old files
github-scraper clean [username] --days 7 --yes

# Show configuration help
github-scraper config

# System diagnostic
github-scraper doctor
```

## 🔑 GitHub API Setup

**Rate Limits:**

- **Without token**: 60 requests/hour (testing only)
- **With token**: 5,000 requests/hour (recommended)

**Setup:**

1. Go to [GitHub Settings > Tokens](https://github.com/settings/tokens)
2. Generate a new token with `public_repo` scope
3. Use: `github-scraper build username --token YOUR_TOKEN`

## 🎯 Output Content

Generated CVs include:

### Data-Driven Content

- **Profile Overview**: Enhanced with website data when available
- **Technical Skills**: Programming languages with expertise levels
- **Featured Projects**: Intelligently selected repositories with metrics
- **Activity Analysis**: Contribution patterns and engagement metrics

### Analytics & Insights

- **Activity Scoring**: Based on stars, forks, and recent activity
- **Language Proficiency**: Calculated from repository data
- **Contribution Patterns**: Community engagement analysis
- **Repository Trends**: Creation and maintenance insights

## 🔧 Development

### Running Tests

```bash
pip install -e ".[dev]"
pytest
pytest --cov=github_scraper --cov-report=html
```

### Code Quality

```bash
black src/ tests/        # Format code
ruff check src/ tests/    # Lint code
mypy src/                 # Type checking
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **PyGithub** for GitHub API integration
- **Jinja2** for template rendering
- **Typer** for the CLI interface
- **Firecrawl** for website enrichment capabilities

---

_Generate professional CVs from GitHub profiles with comprehensive data analysis!_ ✨
