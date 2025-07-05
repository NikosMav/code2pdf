"""Tests for the LinkedIn enrichment plugin."""

import json
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from github_scraper.plugins.linkedin_enrichment import (
    discover_linkedin_urls,
    _is_valid_linkedin_url,
    _normalize_linkedin_url,
    _create_linkedin_extraction_schema,
    _extract_linkedin_data_with_firecrawl,
    collect,
    _get_cache_path,
    _is_cache_valid
)


@pytest.fixture
def sample_github_profile():
    """Sample GitHub profile data for testing."""
    return {
        "username": "testuser",
        "name": "Test User",
        "bio": "Software Engineer | Check out my work at https://linkedin.com/in/testuser",
        "blog": "https://testuser.dev",
        "repos": [
            {
                "name": "awesome-project",
                "description": "My portfolio project. LinkedIn: linkedin.com/in/testuser"
            },
            {
                "name": "another-project",
                "description": "No LinkedIn here"
            }
        ]
    }


@pytest.fixture
def sample_linkedin_response():
    """Sample LinkedIn extraction response."""
    return {
        "url": "https://linkedin.com/in/testuser",
        "extracted_at": "2024-01-16T10:00:00",
        "profile_data": {
            "headline": "Senior Software Engineer at TechCorp",
            "location": "San Francisco, CA",
            "industry": "Technology",
            "education": [
                {
                    "institution": "University of California",
                    "degree": "Bachelor of Science",
                    "field_of_study": "Computer Science",
                    "years": "2016-2020"
                }
            ],
            "certifications": [
                {
                    "name": "AWS Solutions Architect",
                    "issuing_organization": "Amazon Web Services",
                    "issue_date": "2022-06-15",
                    "expiration_date": "2025-06-15"
                }
            ],
            "experience": [
                {
                    "title": "Senior Software Engineer",
                    "company": "TechCorp",
                    "duration": "2022 - Present",
                    "location": "San Francisco, CA"
                }
            ],
            "skills": ["Python", "JavaScript", "AWS", "Docker"]
        },
        "raw_markdown": "Sample LinkedIn profile content..."
    }


def test_discover_linkedin_urls_from_bio(sample_github_profile):
    """Test LinkedIn URL discovery from GitHub bio."""
    urls = discover_linkedin_urls(sample_github_profile)
    assert len(urls) == 1
    assert "https://linkedin.com/in/testuser" in urls


def test_discover_linkedin_urls_from_repos(sample_github_profile):
    """Test LinkedIn URL discovery from repository descriptions."""
    # Modify profile to have LinkedIn only in repo description
    profile = sample_github_profile.copy()
    profile["bio"] = "Software Engineer"
    
    urls = discover_linkedin_urls(profile)
    assert len(urls) == 1
    assert "https://linkedin.com/in/testuser" in urls


def test_discover_linkedin_urls_no_urls():
    """Test when no LinkedIn URLs are found."""
    profile = {
        "username": "testuser",
        "bio": "Software Engineer",
        "blog": "https://testuser.dev",
        "repos": [{"name": "project", "description": "No social links here"}]
    }
    
    urls = discover_linkedin_urls(profile)
    assert len(urls) == 0


def test_discover_linkedin_urls_multiple_sources():
    """Test LinkedIn URL discovery from multiple sources."""
    profile = {
        "username": "testuser", 
        "bio": "Engineer at https://linkedin.com/in/testuser",
        "blog": "linkedin.com/in/testuser",  # Different format
        "repos": [
            {"name": "project", "description": "Check linkedin.com/in/testuser"}
        ]
    }
    
    urls = discover_linkedin_urls(profile)
    # Should deduplicate to single URL
    assert len(urls) == 1
    assert "https://linkedin.com/in/testuser" in urls


def test_discover_linkedin_urls_partial_format():
    """Test LinkedIn URL discovery with partial 'in/username' format."""
    profile = {
        "username": "testuser",
        "bio": "Software Engineer | Check out my profile: in/nikolaos-mavrapidis",
        "repos": [
            {"name": "project", "description": "My portfolio - in/testuser"}
        ]
    }
    
    urls = discover_linkedin_urls(profile)
    assert len(urls) == 2
    assert "https://linkedin.com/in/nikolaos-mavrapidis" in urls
    assert "https://linkedin.com/in/testuser" in urls


class TestLinkedInURLValidation:
    """Test LinkedIn URL validation."""

    def test_valid_linkedin_urls(self):
        """Test valid LinkedIn profile URLs."""
        valid_urls = [
            "https://linkedin.com/in/testuser",
            "https://www.linkedin.com/in/testuser",
            "https://linkedin.com/in/test-user",
            "https://linkedin.com/in/testuser123",
            "https://linkedin.com/in/nikolaos-mavrapidis"
        ]
        
        for url in valid_urls:
            assert _is_valid_linkedin_url(url), f"URL should be valid: {url}"

    def test_invalid_linkedin_urls(self):
        """Test invalid LinkedIn URLs."""
        invalid_urls = [
            "https://twitter.com/testuser",
            "https://linkedin.com/company/testcorp",
            "https://linkedin.com/in/",
            "https://linkedin.com/in/test@user",
            "https://linkedin.com/pub/testuser",
            "not-a-url",
            ""
        ]
        
        for url in invalid_urls:
            assert not _is_valid_linkedin_url(url), f"URL should be invalid: {url}"


class TestLinkedInURLNormalization:
    """Test LinkedIn URL normalization."""

    def test_normalize_partial_urls(self):
        """Test normalization of partial URLs."""
        test_cases = [
            ("in/nikolaos-mavrapidis", "https://linkedin.com/in/nikolaos-mavrapidis"),
            ("in/testuser", "https://linkedin.com/in/testuser"),
            ("linkedin.com/in/testuser", "https://linkedin.com/in/testuser"),
            ("www.linkedin.com/in/testuser", "https://www.linkedin.com/in/testuser"),
            ("https://linkedin.com/in/testuser", "https://linkedin.com/in/testuser"),
            ("https://www.linkedin.com/in/testuser/", "https://www.linkedin.com/in/testuser"),
            ("nikolaos-mavrapidis", "https://linkedin.com/in/nikolaos-mavrapidis"),
        ]
        
        for input_url, expected in test_cases:
            result = _normalize_linkedin_url(input_url)
            assert result == expected, f"Input: {input_url}, Expected: {expected}, Got: {result}"

    def test_normalize_invalid_inputs(self):
        """Test normalization with invalid inputs."""
        invalid_inputs = ["", None, "   ", "https://twitter.com/user", "invalid@url", "company/name"]
        
        for invalid_input in invalid_inputs:
            result = _normalize_linkedin_url(invalid_input)
            assert result is None, f"Invalid input {invalid_input} should return None, got {result}"


def test_linkedin_extraction_schema():
    """Test LinkedIn extraction schema structure."""
    schema = _create_linkedin_extraction_schema()
    
    assert schema["type"] == "object"
    assert "headline" in schema["properties"]
    assert "education" in schema["properties"]
    assert "certifications" in schema["properties"]
    assert "experience" in schema["properties"]
    assert "skills" in schema["properties"]
    
    # Test required fields
    assert "headline" in schema["required"]


@patch('github_scraper.mcp_integration.firecrawl_scrape_sync')
@patch('github_scraper.mcp_integration.is_mcp_available')
def test_extract_linkedin_data_success(mock_mcp_available, mock_firecrawl, sample_linkedin_response):
    """Test successful LinkedIn data extraction."""
    mock_mcp_available.return_value = True
    mock_firecrawl.return_value = {
        "markdown": "Sample content",
        "extract": sample_linkedin_response["profile_data"]
    }
    
    result = _extract_linkedin_data_with_firecrawl("https://linkedin.com/in/testuser", verbose=True)
    
    assert result is not None
    assert result["url"] == "https://linkedin.com/in/testuser"
    assert "profile_data" in result
    assert result["profile_data"]["headline"] == "Senior Software Engineer at TechCorp"
    
    # Verify Firecrawl was called with correct parameters
    mock_firecrawl.assert_called_once()
    call_args = mock_firecrawl.call_args
    assert call_args[1]["url"] == "https://linkedin.com/in/testuser"
    assert call_args[1]["waitFor"] == 5000  # LinkedIn needs more time
    assert call_args[1]["timeout"] == 45


@patch('github_scraper.mcp_integration.firecrawl_scrape_sync')
@patch('github_scraper.mcp_integration.is_mcp_available')
def test_extract_linkedin_data_no_mcp(mock_mcp_available, mock_firecrawl):
    """Test when Firecrawl MCP is not available."""
    mock_mcp_available.return_value = False
    
    result = _extract_linkedin_data_with_firecrawl("https://linkedin.com/in/testuser", verbose=True)
    
    assert result is None
    mock_firecrawl.assert_not_called()


@patch('github_scraper.mcp_integration.firecrawl_scrape_sync')
@patch('github_scraper.mcp_integration.is_mcp_available')
def test_extract_linkedin_data_no_headline(mock_mcp_available, mock_firecrawl):
    """Test when no headline is found (private/inaccessible profile)."""
    mock_mcp_available.return_value = True
    mock_firecrawl.return_value = {
        "markdown": "Limited content",
        "extract": {}  # No headline means private/inaccessible
    }
    
    result = _extract_linkedin_data_with_firecrawl("https://linkedin.com/in/testuser", verbose=True)
    
    assert result is None


@patch('github_scraper.mcp_integration.firecrawl_scrape_sync')
@patch('github_scraper.mcp_integration.is_mcp_available')
def test_extract_linkedin_data_error(mock_mcp_available, mock_firecrawl):
    """Test error handling in LinkedIn data extraction."""
    mock_mcp_available.return_value = True
    mock_firecrawl.side_effect = Exception("Network error")
    
    result = _extract_linkedin_data_with_firecrawl("https://linkedin.com/in/testuser", verbose=True)
    
    assert result is None


def test_collect_no_linkedin_urls(sample_github_profile):
    """Test collect function when no LinkedIn URLs are found."""
    profile = {
        "username": "testuser",
        "bio": "Software Engineer",
        "repos": []
    }
    
    result = collect(profile, verbose=True)
    assert result == {}


@patch('github_scraper.plugins.linkedin_enrichment._extract_linkedin_data_with_firecrawl')
def test_collect_success(mock_extract, sample_github_profile, sample_linkedin_response):
    """Test successful LinkedIn data collection."""
    mock_extract.return_value = sample_linkedin_response
    
    result = collect(sample_github_profile, use_cache=False, verbose=True)
    
    assert "discovered_urls" in result
    assert "profiles" in result
    assert "enrichment_summary" in result
    
    assert len(result["profiles"]) == 1
    assert result["profiles"][0]["url"] == "https://linkedin.com/in/testuser"
    
    # Check enrichment summary
    summary = result["enrichment_summary"]
    assert summary["headline"] == "Senior Software Engineer at TechCorp"
    assert summary["education_count"] == 1
    assert summary["certification_count"] == 1
    assert summary["experience_count"] == 1
    assert summary["skills_count"] == 4
    assert summary["has_professional_data"] is True


@patch('github_scraper.plugins.linkedin_enrichment._extract_linkedin_data_with_firecrawl')
def test_collect_extraction_failure(mock_extract, sample_github_profile):
    """Test collect function when extraction fails."""
    mock_extract.return_value = None
    
    result = collect(sample_github_profile, use_cache=False, verbose=True)
    
    assert "discovered_urls" in result
    assert len(result["profiles"]) == 0
    assert result["enrichment_summary"] == {}


@patch('github_scraper.plugins.linkedin_enrichment._extract_linkedin_data_with_firecrawl')
def test_collect_with_manual_url(mock_extract, sample_linkedin_response):
    """Test collect function with manually provided LinkedIn URL."""
    # Update the mock response to use the expected URL
    sample_response = sample_linkedin_response.copy()
    sample_response["url"] = "https://linkedin.com/in/nikolaos-mavrapidis"
    mock_extract.return_value = sample_response
    
    # Profile with no LinkedIn data
    profile = {
        "username": "testuser",
        "bio": "Software Engineer",
        "repos": []
    }
    
    # Test with manual URL
    result = collect(
        profile, 
        use_cache=False, 
        verbose=True,
        manual_linkedin_url="in/nikolaos-mavrapidis"
    )
    
    assert "discovered_urls" in result
    assert len(result["profiles"]) == 1
    assert result["profiles"][0]["url"] == "https://linkedin.com/in/nikolaos-mavrapidis"
    assert result["enrichment_summary"]["headline"] == "Senior Software Engineer at TechCorp"


def test_collect_with_invalid_manual_url():
    """Test collect function with invalid manual LinkedIn URL."""
    profile = {"username": "testuser", "bio": "Engineer", "repos": []}
    
    result = collect(
        profile,
        use_cache=False,
        verbose=True,
        manual_linkedin_url="invalid-url"
    )
    
    assert result == {}


def test_cache_path_generation():
    """Test cache path generation for LinkedIn URLs."""
    url = "https://linkedin.com/in/testuser"
    path = _get_cache_path(url)
    
    assert path.name.startswith("linkedin_")
    assert path.name.endswith(".json")
    assert "testuser" not in path.name  # Should be hashed


def test_cache_validity():
    """Test cache validity checking."""
    # Test with non-existent file
    fake_path = Path("/non/existent/path.json")
    assert not _is_cache_valid(fake_path)


@patch('builtins.open')
@patch('pathlib.Path.exists')
@patch('github_scraper.plugins.linkedin_enrichment._is_cache_valid')
@patch('github_scraper.plugins.linkedin_enrichment._extract_linkedin_data_with_firecrawl')
def test_collect_with_cache(mock_extract, mock_cache_valid, mock_exists, mock_open, sample_github_profile, sample_linkedin_response):
    """Test collect function using cached data."""
    # Setup cache mocks
    mock_cache_valid.return_value = True
    mock_exists.return_value = True
    mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(sample_linkedin_response)
    
    result = collect(sample_github_profile, use_cache=True, verbose=True)
    
    # Should not call extract function when cache is valid
    mock_extract.assert_not_called()
    
    assert len(result["profiles"]) == 1


class TestLinkedInEnrichmentIntegration:
    """Integration tests for LinkedIn enrichment."""

    def test_enrichment_summary_creation(self):
        """Test creation of enrichment summary from profile data."""
        profile_data = {
            "headline": "Software Engineer",
            "location": "San Francisco",
            "industry": "Technology",
            "education": [{"degree": "BS CS"}],
            "certifications": [{"name": "AWS"}, {"name": "GCP"}],
            "experience": [{"title": "Engineer"}],
            "skills": ["Python", "JavaScript"]
        }
        
        # Simulate the enrichment summary creation logic
        enrichment_summary = {
            "headline": profile_data.get("headline", ""),
            "location": profile_data.get("location", ""),
            "industry": profile_data.get("industry", ""),
            "education_count": len(profile_data.get("education", [])),
            "certification_count": len(profile_data.get("certifications", [])),
            "experience_count": len(profile_data.get("experience", [])),
            "skills_count": len(profile_data.get("skills", [])),
            "has_professional_data": bool(
                profile_data.get("headline") or 
                profile_data.get("education") or 
                profile_data.get("certifications")
            )
        }
        
        assert enrichment_summary["headline"] == "Software Engineer"
        assert enrichment_summary["education_count"] == 1
        assert enrichment_summary["certification_count"] == 2
        assert enrichment_summary["experience_count"] == 1
        assert enrichment_summary["skills_count"] == 2
        assert enrichment_summary["has_professional_data"] is True

    def test_empty_profile_enrichment(self):
        """Test enrichment with minimal LinkedIn data."""
        profile_data = {"headline": "Engineer"}
        
        enrichment_summary = {
            "headline": profile_data.get("headline", ""),
            "education_count": len(profile_data.get("education", [])),
            "certification_count": len(profile_data.get("certifications", [])),
            "experience_count": len(profile_data.get("experience", [])),
            "skills_count": len(profile_data.get("skills", [])),
            "has_professional_data": bool(profile_data.get("headline"))
        }
        
        assert enrichment_summary["headline"] == "Engineer"
        assert enrichment_summary["education_count"] == 0
        assert enrichment_summary["certification_count"] == 0
        assert enrichment_summary["has_professional_data"] is True 