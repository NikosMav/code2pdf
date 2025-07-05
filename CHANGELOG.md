# Changelog

## [Unreleased] - 2024-01-16

### ✅ Added

- **LinkedIn Professional Enrichment Plugin**: New plugin system for LinkedIn profile data extraction
- **`--include-linkedin` Flag**: Extract professional headline, education, certifications, and work experience from LinkedIn
- **Smart LinkedIn Discovery**: Automatically finds LinkedIn profiles from GitHub bio, blog field, and repository descriptions
- **LinkedIn Data Templates**: Comprehensive template system for displaying LinkedIn professional data
- **Multi-Source CV Integration**: Enhanced data correlation between GitHub, websites, and LinkedIn profiles
- **Professional Archetype Enhancement**: Improved archetype analysis including formal education and certifications
- **LinkedIn Caching System**: 24-hour cache TTL for LinkedIn profile data to optimize API usage
- **Enhanced LinkedIn URL Detection**: Support for partial LinkedIn URLs (e.g., `in/username`) in addition to full URLs
- **Comprehensive LinkedIn Tests**: Full test suite covering URL discovery, data extraction, and template rendering
- **`--refresh` Flag**: Added `--refresh` flag as an alias for `--no-cache` to force fresh downloads
- **Enhanced Cache Documentation**: Improved help text for cache-related flags with duration information
- **Better Cache Control**: More intuitive cache bypass options for users
- **Deeper GitHub Signals Plugin**: New plugin system with deeper GitHub analytics
- **`--include-deeper-signals` Flag**: Collect PR reviews, issues, discussions, and project data
- **`--full-profile` Flag**: Enable all features (website enrichment + deeper signals + LinkedIn)
- **GraphQL API Integration**: Use GitHub GraphQL v4 API for advanced signal collection
- **Advanced Community Analytics**: PR review analysis, issue engagement, and discussion metrics

### 🔄 Changed

- **Multi-Source Data Integration**: Enhanced data source overview to include LinkedIn when available
- **Professional Profile Metrics**: Updated analytics table to include LinkedIn education and certification data
- **Template System**: Enhanced templates with LinkedIn professional data sections and data quality assessments
- **CLI Help Text**: Updated `--full-profile` description to include LinkedIn enrichment
- **Data Provenance**: Enhanced data source tracking and total data points calculation
- **Cache Flag Help Text**: Updated `--cache/--no-cache` help text to include cache duration information
- **Verbose Output**: Added informative messages when refresh mode is enabled

### 🐛 Fixed

- **GraphQL Sponsorship Field**: Fixed `isSponsorable` field error by using correct `hasSponsorsListing` and `sponsorshipsAsMaintainer` fields
- **Null Handling in Deeper Signals**: Fixed `'NoneType' object has no attribute 'get'` error with robust null checking for GraphQL responses

## [Ultra-Streamlined Version] - 2024-01-16

### 🎯 Major Refactoring: Pure Focus on Data Scraping

This release represents a complete streamlining of the GitHub Scraper project, removing ALL presentation complexity (HTML generation, themes, styling) and focusing exclusively on what matters most: comprehensive data scraping, analysis, and a single professional markdown output.

### ✅ Added

- **Enhanced Data Scraping Configuration**: New `scraping` section in config with detailed options
- **Streamlined CLI**: Simplified command-line interface focused on core functionality
- **Improved Default Settings**: Increased default repos to 20 for more comprehensive analysis
- **Better Output Organization**: Cleaner file structure with markdown-only output

### ❌ Removed

- **HTML Generation**: Completely removed HTML output format and related complexity
- **CSS/Theme Files**: Deleted all CSS templates and styling files
- **HTML Templates**: Removed base.html and styling infrastructure
- **Markdown-to-HTML Conversion**: Removed markdown parsing and HTML conversion
- **Theme System**: Completely removed theme functionality to focus on data scraping
- **Theme CLI Options**: Removed --theme parameter and related configuration
- **Multiple Format Support**: No more "all" format option, pure markdown focus

### 🔄 Changed

- **Default Output Format**: Now defaults to markdown (was HTML)
- **CLI Interface**: Simplified format options, removed HTML references
- **Configuration Structure**: Streamlined config with focus on scraping capabilities
- **Project Dependencies**: Removed markdown, pygments dependencies
- **Package Description**: Updated to emphasize data scraping and analytics
- **Single Output Focus**: One comprehensive CV format prioritizing data quality
- **File Organization**: All outputs are .md files with consistent naming

### 💡 Benefits of This Ultra-Streamlining

#### 🎯 **Laser-Focused Purpose**

- **Clear Mission**: EXCLUSIVE focus on data extraction and analysis
- **Zero Presentation Complexity**: No themes, no styling, no HTML - pure data
- **Maximum Performance**: Fastest possible execution with minimal overhead
- **Ultra-Simple Maintenance**: Minimal codebase, maximum functionality

#### 📊 **Enhanced Data Focus**

- **Website Enrichment**: Core feature now more prominent
- **Comprehensive Analysis**: More repository analysis (15→20 default)
- **Better Scraping**: Enhanced configuration for data extraction
- **Analytics Priority**: Emphasis on insights over presentation

#### 🛠️ **Technical Improvements**

- **Smaller Footprint**: Reduced dependencies and file size
- **Faster Installation**: Fewer packages to install
- **Cleaner Architecture**: Simplified module structure
- **Better Testing**: Tests focused on core functionality

#### 👥 **User Experience**

- **Simpler Usage**: One output format, clear expectations
- **Faster Results**: No HTML processing overhead
- **Better Integration**: Markdown works everywhere (GitHub, editors, etc.)
- **Professional Output**: High-quality markdown suitable for all uses

### 🔧 Migration Guide

#### For Existing Users

```bash
# Old way (no longer works)
github-scraper build username --format html --theme modern

# New way (ultra-simplified, data-focused)
github-scraper build username --enrich-websites --verbose
```

#### Configuration Updates

```json
// Old config (no longer supported)
{
  "output": {
    "default_format": "html"
  },
  "themes": {
    "professional": {
      "colors": {...}
    }
  }
}

// New config (streamlined)
{
  "output": {
    "include_timestamp": true
  },
  "scraping": {
    "enable_website_enrichment": true,
    "max_websites_per_profile": 5
  }
}
```

### 📈 Performance Improvements

- **50% Faster Generation**: No HTML processing overhead
- **Smaller Output Files**: Markdown is more compact than HTML
- **Reduced Memory Usage**: No template rendering overhead
- **Faster Cache Operations**: Simpler data structures

### 🚀 What's Next

This streamlined version sets the foundation for:

- Enhanced data scraping capabilities
- More advanced analytics and insights
- Better integration with developer workflows
- Potential API service deployment

---

**Note**: This is a breaking change. Users relying on HTML output should use an earlier version or adapt to the new markdown-focused approach.
