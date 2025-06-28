# Documentation

This folder contains comprehensive documentation for the code2pdf project and its website enrichment features.

## 📚 Documents

### `WEBSITE_ENRICHMENT.md`

Complete documentation for the website enrichment feature that uses MCP Firecrawl integration to enhance GitHub profiles with personal website data.

**Contents:**

- Feature overview and capabilities
- Usage instructions (CLI and programmatic)
- MCP integration details
- Performance and caching information
- Examples and use cases
- Testing and validation results

### `MULTI_PROFILE_TEST_RESULTS.md`

Detailed test results and validation report for the website enrichment system across multiple diverse GitHub profiles.

**Contents:**

- Test methodology and profiles tested
- Success metrics and performance data
- Edge case handling validation
- Before/after comparisons
- Quality assurance results

## 🚀 Quick Navigation

**For Users:**

- Start with `WEBSITE_ENRICHMENT.md` for feature overview
- Check usage examples in `/examples` folder
- Run tests from `/tests` folder

**For Developers:**

- Review `MULTI_PROFILE_TEST_RESULTS.md` for validation data
- Check implementation in `/src/code2pdf/`
- See test suites in `/tests/`

## 🔗 Related Resources

- **Main README**: Project overview and installation
- **Examples**: Demonstration scripts in `/examples`
- **Tests**: Comprehensive test suites in `/tests`
- **Source Code**: Implementation in `/src/code2pdf/`

## 📖 Architecture Overview

The website enrichment system consists of:

1. **URL Discovery** (`website_enrichment.py`) - Finds personal websites from GitHub profiles
2. **MCP Integration** (`mcp_integration.py`) - Interfaces with Firecrawl MCP tools
3. **GitHub Enhancement** (`github.py`) - Integrates enrichment into profile fetching
4. **CLI Interface** (`cli.py`) - Provides user-friendly command-line access

## ✅ Validation Status

- ✅ **Feature Complete** - All planned functionality implemented
- ✅ **Production Ready** - Robust error handling and fallbacks
- ✅ **Well Tested** - Comprehensive test coverage across profile types
- ✅ **Documented** - Complete usage and implementation documentation
