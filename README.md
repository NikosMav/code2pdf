# code2pdf

Generate data-driven, professional markdown CVs from GitHub profiles with comprehensive analytics and insights.

## Features

- **📊 Data-Driven Insights**: Activity scores, expertise levels, and contribution patterns
- **💻 Technical Analysis**: Programming language proficiency and technology stack insights
- **🚀 Project Showcase**: Enhanced repository details with impact metrics
- **📈 Professional Metrics**: Community engagement and development activity analysis
- **🎯 Rate-Limit Friendly**: Optimized API usage with GitHub token support

## Quick Start

```bash
pipx install code2pdf
code2pdf build nikosmav
```

For enhanced features and to avoid rate limits:

```bash
code2pdf build nikosmav --token YOUR_GITHUB_TOKEN
```

This creates a comprehensive `resume.md` file with professional insights derived from GitHub activity.

## Enhanced Output

The generated CV includes:

- Professional summary with activity scoring
- Programming language expertise analysis
- Project impact metrics (stars, forks, watchers)
- Development patterns and collaboration insights
- GitHub statistics with industry context

[View demo CV →](demo_enhanced_cv.md)
