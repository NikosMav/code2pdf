# GitHub Scraper

Generate professional HTML CVs from GitHub profiles with comprehensive analytics.

## 🚀 Features

### **Enhanced Output Formats**

- **📄 Markdown** - GitHub-compatible markdown
- **🌐 HTML** - Styled HTML with responsive design (default)
- **🎨 Multiple Themes** - Professional, Modern, and Minimal designs

### **Data-Driven Insights**

- **📊 Activity Scoring** - Comprehensive scoring based on stars, forks, and activity
- **💻 Language Analysis** - Programming language expertise with proficiency levels
- **🚀 Project Showcase** - Smart repository selection with diversity
- **📈 Contribution Patterns** - Community engagement and development activity
- **🔍 Repository Trends** - Creation patterns and maintenance insights

### **Advanced Features**

- **⚡ Intelligent Caching** - API response caching for faster subsequent runs
- **🎛️ Configurable Options** - Extensive customization via config files
- **🔄 Rate Limit Friendly** - Optimized API usage with GitHub token support
- **📱 Responsive Design** - Mobile-friendly HTML outputs
- **🎯 Verbose Mode** - Detailed progress reporting

### **🌐 Website Enrichment (New!)**

- **📝 Personal Website Integration** - Automatically discovers and analyzes personal websites
- **🔍 Smart URL Discovery** - Finds websites from GitHub profile, bio, and repositories
- **🤖 MCP Firecrawl Integration** - Uses advanced web scraping with AI-powered extraction
- **📊 Enhanced Profiles** - Adds skills, experience, and projects from personal websites
- **🛡️ Intelligent Filtering** - Focuses on personal websites, filters out social media
- **🔄 Graceful Fallback** - Works perfectly even when no websites are found

## 📦 Installation

### Basic Installation (Markdown + HTML)

```bash
# Install from PyPI (recommended)
pipx install github-scraper

# Or install with pip
pip install github-scraper
```

### Full Installation (All Features)

```bash
# Install with all optional features
pipx install "github-scraper[all]"

# Or with pip
pip install "github-scraper[all]"
```

### Optional Features

```bash
# YAML configuration support
pip install "github-scraper[yaml]"
```

### Development Installation

```bash
git clone https://github.com/nikosmav/github-scraper.git
cd github-scraper
pip install -e ".[dev,all]"
```

## 🚀 Quick Start

### Basic Usage

```bash
# Generate HTML CV (default) - creates organized folder
github-scraper build nikosmav

# Generate markdown with modern theme in organized folder
github-scraper build nikosmav --format markdown --theme modern

# Generate all formats in organized folder
github-scraper build nikosmav --format all --theme professional
```

### With GitHub Token (Recommended)

```bash
# Higher rate limits and better data
github-scraper build nikosmav --token YOUR_GITHUB_TOKEN --format html --verbose
```

### Advanced Usage

```bash
# Custom output directory
github-scraper build nikosmav --output-dir my_cvs --theme modern

# Single file output (bypasses organization)
github-scraper build nikosmav --output my_resume.html --theme minimal

# Disable caching
github-scraper build nikosmav --no-cache --format html
```

### 🌐 Website Enrichment

**Setup Required:**
For website enrichment to work, you need to set up your Firecrawl API key:

```bash
# Set your Firecrawl API key as an environment variable
export FIRECRAWL_API_KEY="your_firecrawl_api_key_here"

# On Windows:
set FIRECRAWL_API_KEY=your_firecrawl_api_key_here
```

Get your free API key from [Firecrawl](https://firecrawl.dev/).

**Usage:**

```bash
# Generate CV with website enrichment (analyzes personal websites)
github-scraper build nikosmav --enrich-websites --verbose

# Enhanced CV with all formats
github-scraper build nikosmav --enrich-websites --format all --theme modern

# Website enrichment with custom output
github-scraper build nikosmav --enrich-websites --output-dir enhanced_cvs
```

### File Organization

By default, `github-scraper` creates organized folders:

```
generated_cvs/
├── nikosmav_2024-01-15/
│   ├── nikosmav_cv_professional.md
│   └── nikosmav_cv_professional.html
└── johndoe_2024-01-16/
    ├── johndoe_cv_modern.md
    └── johndoe_cv_modern.html
```

**Folder Structure:**

- `generated_cvs/{username}_{date}/` - Organized by user and date
- Each folder contains all generated formats for that user
- Clean separation prevents file conflicts
- Easy to find and manage multiple CV versions

**Organization Options:**

```bash
# Default: organized folder with date
github-scraper build nikosmav
# → generated_cvs/nikosmav_2024-01-15/nikosmav_cv_professional.html

# Custom directory
github-scraper build nikosmav --output-dir my_team_cvs
# → my_team_cvs/nikosmav_cv_professional.html

# Single file (bypasses organization)
github-scraper build nikosmav --output john_resume.html
# → john_resume.html (current directory)

# Multiple users in same directory
github-scraper build nikosmav --output-dir company_cvs
github-scraper build johndoe --output-dir company_cvs
# → company_cvs/nikosmav_cv_professional.html
# → company_cvs/johndoe_cv_professional.html
```

## 🎨 Themes

### Professional (Default)

- Clean, corporate design
- Blue color scheme
- Perfect for traditional industries

### Modern

- Contemporary design with gradients
- Purple and orange accents
- Great for tech and creative fields

### Minimal

- Simple, text-focused layout
- Serif typography
- Ideal for academic and research roles

## ⚙️ Configuration

Create a `github-scraper.json` or `github-scraper.yaml` file in your project directory or home folder:

```json
{
  "github": {
    "cache_duration_hours": 2,
    "max_repos": 15,
    "include_forks": false
  },
  "cv": {
    "max_featured_repos": 10,
    "include_insights": true,
    "activity_threshold_days": 90
  },
  "output": {
    "default_format": "html",
    "include_timestamp": true
  },
  "themes": {
    "professional": {
      "colors": {
        "primary": "#2563eb",
        "accent": "#059669"
      }
    }
  }
}
```

## 📋 CLI Commands

### `build` - Generate CV

```bash
github-scraper build <username> [OPTIONS]

Options:
  -o, --output PATH          Output file path or directory
  -d, --output-dir PATH      Output directory for organized files
  -f, --format FORMAT        Output format: markdown|html|all
  -t, --theme THEME          Theme: professional|modern|minimal
  --enrich-websites          Enable website enrichment with MCP Firecrawl
  --token TEXT               GitHub personal access token
  -c, --config PATH          Configuration file path
  --cache/--no-cache         Enable/disable caching
  -v, --verbose              Enable verbose output
```

### `clean` - Clean Up Old Files

```bash
github-scraper clean [username] [OPTIONS]

Options:
  --days INTEGER             Remove folders older than N days (default: 7)
  -y, --yes                  Skip confirmation prompt
```

### `config` - Show Configuration Help

```bash
github-scraper config
```

### `doctor` - System Diagnostic

```bash
github-scraper doctor
```

## 🔧 Development

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=github_scraper --cov-report=html
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/
```

Your generated CV will include:

```markdown
# John Developer

_Python Developer with 5.2 years on GitHub_

**Tech Corp** 📍 San Francisco, CA

## 📊 Professional Summary

**Activity Score:** 78/100 | **Impact Level:** High | **Recent Activity:** High

- **5.2 years** of experience on GitHub since 2019
- **25 original repositories** with **342 total stars** earned
- **8 programming languages** in portfolio
- **12 projects** actively maintained
- Average **13.7 stars per repository**
```

## 🚫 Rate Limits

| Authentication | Requests/Hour | Recommended Usage  |
| -------------- | ------------- | ------------------ |
| No Token       | 60            | Light testing only |
| Personal Token | 5,000         | Production use     |

Get your token at: https://github.com/settings/tokens

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** changes: `git commit -m 'Add amazing feature'`
4. **Push** to branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **PyGithub** for GitHub API integration
- **Jinja2** for template rendering
- **Typer** for the CLI interface

---

## 📞 Support

- **Documentation**: [Full documentation](https://github.com/nikosmav/github-scraper)
- **Issues**: [Report bugs](https://github.com/nikosmav/github-scraper/issues)
- **Discussions**: [Community discussions](https://github.com/nikosmav/github-scraper/discussions)

_Generate your professional CV in seconds with GitHub Scraper!_ ✨
