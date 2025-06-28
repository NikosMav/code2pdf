# Tests

This folder contains comprehensive test suites for the github-scraper application, including tests for the website enrichment feature.

## 📁 Test Files

### `test_github.py`

Tests for the core GitHub profile fetching and analysis functionality.

**Coverage:**

- GitHub API integration
- Profile data extraction
- Repository analysis
- Language analysis
- Contribution patterns
- Caching mechanisms

### `test_multiple_profiles.py`

Comprehensive test suite for the website enrichment feature with multiple GitHub profiles.

**Coverage:**

- Website URL discovery
- URL validation and filtering
- Enrichment with various profile types
- Graceful fallback behavior
- Error handling
- Performance validation

**Test Profiles:**

- `AngelPn` - Profile without personal websites
- `dirkbrnd` - Low-activity profile
- `WilliamEspegren` - Large repository count
- `manuhortet` - Profile with platform URLs (filtered)

## 🧪 Running Tests

### Run All Tests

```bash
# From project root
python -m pytest tests/

# With verbose output
python -m pytest tests/ -v

# With coverage
python -m pytest tests/ --cov=src/github_scraper
```

### Run Specific Tests

```bash
# GitHub functionality tests
python -m pytest tests/test_github.py

# Website enrichment tests
python -m pytest tests/test_multiple_profiles.py

# Run specific test function
python -m pytest tests/test_github.py::test_function_name -v
```

## 📊 Test Results Summary

The test suite validates:

✅ **100% Success Rate** - All profiles tested successfully
✅ **Graceful Fallback** - Handles profiles without websites
✅ **Smart Filtering** - Correctly filters non-personal websites  
✅ **Error Resilience** - No crashes across diverse profile types
✅ **Performance** - Fast processing regardless of profile size
✅ **Consistency** - High-quality output in all scenarios

## 🔧 Test Configuration

Tests use mock data and fallback mechanisms to ensure:

- No external API rate limit issues
- Consistent test results
- Fast execution
- Comprehensive coverage

## 📈 Coverage Goals

- Core functionality: >95% coverage
- Website enrichment: >90% coverage
- Error handling: >85% coverage
- Integration scenarios: 100% of main workflows

## 🔗 Related

- See `/examples` for demonstration scripts
- See `/docs` for detailed feature documentation
- See main `README.md` for installation instructions
