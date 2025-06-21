# code2pdf

Generate professional CVs from GitHub profiles with comprehensive analytics and multiple output formats.

## 🚀 Features

### **Enhanced Output Formats**

- **📄 Markdown** - GitHub-compatible markdown (default)
- **🌐 HTML** - Styled HTML with responsive design
- **📋 PDF** - Print-ready PDF documents
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
- **📱 Responsive Design** - Mobile-friendly HTML/PDF outputs
- **🎯 Verbose Mode** - Detailed progress reporting

## 📦 Installation

### Basic Installation (Markdown + HTML)

```bash
# Install from PyPI (recommended)
pipx install code2pdf

# Or install with pip
pip install code2pdf
```

### Full Installation (All Features)

```bash
# Install with all optional features
pipx install "code2pdf[all]"

# Or with pip
pip install "code2pdf[all]"
```

### Optional Features

```bash
# PDF generation support (requires system libraries)
pip install "code2pdf[pdf]"

# YAML configuration support
pip install "code2pdf[yaml]"
```

### Development Installation

```bash
git clone https://github.com/nikosmav/code2pdf.git
cd code2pdf
pip install -e ".[dev,all]"
```

### System Dependencies for PDF Generation

**Ubuntu/Debian:**

```bash
sudo apt-get install libpango1.0-dev libharfbuzz-dev libffi-dev libjpeg-dev libopenjp2-7-dev
pip install "code2pdf[pdf]"
```

**macOS:**

```bash
brew install pango harfbuzz
pip install "code2pdf[pdf]"
```

**Windows:**

- PDF generation has compatibility issues on Windows
- Use HTML output with "Print to PDF" in your browser
- Or consider using WSL2 for better compatibility

## 🚀 Quick Start

### Basic Usage

```bash
# Generate markdown CV (default) - creates organized folder
code2pdf build nikosmav

# Generate PDF with modern theme in organized folder
code2pdf build nikosmav --format pdf --theme modern

# Generate all formats in organized folder
code2pdf build nikosmav --format all --theme professional
```

### With GitHub Token (Recommended)

```bash
# Higher rate limits and better data
code2pdf build nikosmav --token YOUR_GITHUB_TOKEN --format pdf --verbose
```

### Advanced Usage

```bash
# Custom output directory
code2pdf build nikosmav --output-dir my_cvs --theme modern

# Single file output (bypasses organization)
code2pdf build nikosmav --output my_resume.html --theme minimal

# Disable caching
code2pdf build nikosmav --no-cache --format html
```

### File Organization

By default, `code2pdf` creates organized folders:

```
generated_cvs/
├── nikosmav_2024-01-15/
│   ├── nikosmav_cv_professional.md
│   ├── nikosmav_cv_professional.html
│   └── nikosmav_cv_professional.pdf
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
code2pdf build nikosmav
# → generated_cvs/nikosmav_2024-01-15/nikosmav_cv_professional.md

# Custom directory
code2pdf build nikosmav --output-dir my_team_cvs
# → my_team_cvs/nikosmav_cv_professional.md

# Single file (bypasses organization)
code2pdf build nikosmav --output john_resume.pdf
# → john_resume.pdf (current directory)

# Multiple users in same directory
code2pdf build nikosmav --output-dir company_cvs
code2pdf build johndoe --output-dir company_cvs
# → company_cvs/nikosmav_cv_professional.md
# → company_cvs/johndoe_cv_professional.md
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

Create a `code2pdf.json` or `code2pdf.yaml` file in your project directory or home folder:

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
    "default_format": "pdf",
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
code2pdf build <username> [OPTIONS]

Options:
  -o, --output PATH          Output file path or directory
  -d, --output-dir PATH      Output directory for organized files
  -f, --format FORMAT        Output format: markdown|html|pdf|all
  -t, --theme THEME          Theme: professional|modern|minimal
  --token TEXT               GitHub personal access token
  -c, --config PATH          Configuration file path
  --cache/--no-cache         Enable/disable caching
  -v, --verbose              Enable verbose output
```

### `clean` - Clean Up Old Files

```bash
code2pdf clean [username] [OPTIONS]

Options:
  --days INTEGER             Remove folders older than N days (default: 7)
  -y, --yes                  Skip confirmation prompt
```

### `config` - Show Configuration Help

```bash
code2pdf config
```

### `doctor` - System Diagnostic

```bash
code2pdf doctor
```

## 🔧 Development

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=code2pdf --cov-report=html
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

## 📊 Generated CV Sections

### Profile Header

- Name, bio, and contact information
- Social links and professional status
- Account age and basic statistics

### Professional Summary

- Activity score and impact level
- Key metrics and achievements
- Years of experience and project count

### Technical Expertise

- Programming language proficiency
- Technology stack insights
- Specialization areas

### Featured Projects

- Top repositories by stars and diversity
- Project descriptions and metrics
- Activity status and licensing

### Development Insights

- Contribution patterns analysis
- Community engagement metrics
- Project maintenance indicators

### GitHub Statistics

- Comprehensive metrics table
- Industry benchmarking
- Professional indicators

## 🏆 Sample Output

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

## 📈 Comparison: Before vs After

| Feature        | Before          | After                    |
| -------------- | --------------- | ------------------------ |
| Output Formats | Markdown only   | Markdown, HTML, PDF      |
| Themes         | Single template | 3 professional themes    |
| Caching        | None            | Intelligent caching      |
| Configuration  | Hard-coded      | Fully configurable       |
| Analytics      | Basic           | Comprehensive insights   |
| Error Handling | Basic           | Detailed error messages  |
| Testing        | None            | Comprehensive test suite |
| Performance    | Slow sequential | Optimized with caching   |

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** changes: `git commit -m 'Add amazing feature'`
4. **Push** to branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **PyGithub** for GitHub API integration
- **WeasyPrint** for PDF generation
- **Jinja2** for template rendering
- **Typer** for the CLI interface

---

## 📞 Support

- **Documentation**: [Full documentation](https://github.com/nikosmav/code2pdf)
- **Issues**: [Report bugs](https://github.com/nikosmav/code2pdf/issues)
- **Discussions**: [Community discussions](https://github.com/nikosmav/code2pdf/discussions)

_Generate your professional CV in seconds with code2pdf!_ ✨
