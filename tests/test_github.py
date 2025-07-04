"""Tests for GitHub module functionality with focus on data scraping and analysis."""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timezone

from github_scraper.github import (
    calculate_activity_score,
    analyze_languages,
    analyze_contribution_patterns,
    analyze_repository_trends,
)


class TestActivityScore:
    """Test activity score calculation."""

    def test_empty_repos(self):
        """Test activity score with no repositories."""
        assert calculate_activity_score([]) == 0

    def test_single_repo_basic(self):
        """Test activity score with a single basic repository."""
        repos = [{"stars": 10, "forks": 5, "watchers": 8, "days_since_update": 30}]
        score = calculate_activity_score(repos)
        assert 0 <= score <= 100
        assert score > 0

    def test_high_activity_repo(self):
        """Test activity score with highly active repository."""
        repos = [{"stars": 100, "forks": 50, "watchers": 75, "days_since_update": 5}]
        score = calculate_activity_score(repos)
        assert score > 50


class TestLanguageAnalysis:
    """Test programming language analysis."""

    def test_empty_repos(self):
        """Test language analysis with no repositories."""
        result = analyze_languages([])
        assert result["language_count"] == 0
        assert result["most_used"] == ("None", 0)

    def test_single_language(self):
        """Test analysis with repositories in single language."""
        repos = [
            {"language": "Python", "stars": 10, "size": 1000},
            {"language": "Python", "stars": 5, "size": 500},
        ]
        result = analyze_languages(repos)
        assert result["language_count"] == 1
        assert result["most_used"][0] == "Python"
        assert result["most_used"][1] == 2
        assert "Python" in result["expertise_levels"]

    def test_multiple_languages(self):
        """Test analysis with multiple programming languages."""
        repos = [
            {"language": "Python", "stars": 20, "size": 2000},
            {"language": "JavaScript", "stars": 15, "size": 1500},
            {"language": "Python", "stars": 10, "size": 1000},
        ]
        result = analyze_languages(repos)
        assert result["language_count"] == 2
        assert "Python" in result["top_languages"]
        assert "JavaScript" in result["top_languages"]

    def test_expertise_levels(self):
        """Test expertise level calculation."""
        repos = [
            {"language": "Python", "stars": 50, "size": 5000},  # High stars
            {"language": "Python", "stars": 30, "size": 3000},
            {"language": "Python", "stars": 20, "size": 2000},
            {"language": "Python", "stars": 15, "size": 1500},
            {
                "language": "Python",
                "stars": 10,
                "size": 1000,
            },  # 5 repos with good stars = Expert
            {
                "language": "JavaScript",
                "stars": 1,
                "size": 200,
            },  # Very low stars, few repos = Beginner
        ]
        result = analyze_languages(repos)
        assert result["expertise_levels"]["Python"] == "Expert"
        assert result["expertise_levels"]["JavaScript"] == "Beginner"


class TestContributionPatterns:
    """Test contribution pattern analysis."""

    def test_basic_patterns(self):
        """Test basic contribution pattern calculation."""
        repos = [
            {
                "stars": 20,
                "forks": 5,
                "watchers": 15,
                "open_issues": 3,
                "days_since_update": 30,
                "has_wiki": True,
                "description": "Test repo",
                "license": "MIT",
            },
            {
                "stars": 10,
                "forks": 2,
                "watchers": 8,
                "open_issues": 1,
                "days_since_update": 60,
                "has_wiki": False,
                "description": None,
                "license": None,
            },
        ]
        user_data = {"followers": 50, "following": 25}

        result = analyze_contribution_patterns(repos, user_data)

        assert result["total_repositories"] == 2
        assert result["total_stars_earned"] == 30
        assert result["total_forks_received"] == 7
        assert result["total_watchers"] == 23
        assert result["total_open_issues"] == 4
        assert 0 <= result["collaboration_ratio"] <= 1
        assert 0 <= result["community_health_score"] <= 100

    def test_impact_scores(self):
        """Test impact score classification."""
        # High impact
        high_impact_repos = [
            {
                "stars": 150,
                "forks": 30,
                "watchers": 100,
                "open_issues": 5,
                "days_since_update": 10,
            }
        ]
        result = analyze_contribution_patterns(high_impact_repos, {})
        assert result["impact_score"] == "High"

        # Medium impact
        medium_impact_repos = [
            {
                "stars": 50,
                "forks": 10,
                "watchers": 30,
                "open_issues": 2,
                "days_since_update": 20,
            }
        ]
        result = analyze_contribution_patterns(medium_impact_repos, {})
        assert result["impact_score"] == "Medium"

        # Low impact
        low_impact_repos = [
            {
                "stars": 5,
                "forks": 1,
                "watchers": 3,
                "open_issues": 0,
                "days_since_update": 100,
            }
        ]
        result = analyze_contribution_patterns(low_impact_repos, {})
        assert result["impact_score"] == "Low"


class TestRepositoryTrends:
    """Test repository trend analysis."""

    def test_empty_repos(self):
        """Test trend analysis with no repositories."""
        result = analyze_repository_trends([])
        assert result == {}

    def test_creation_trends(self):
        """Test repository creation trend analysis."""
        repos = [
            {"created_at": datetime(2023, 1, 15, tzinfo=timezone.utc)},
            {"created_at": datetime(2023, 3, 20, tzinfo=timezone.utc)},
            {"created_at": datetime(2022, 12, 10, tzinfo=timezone.utc)},
        ]
        result = analyze_repository_trends(repos)

        assert "creation_trend" in result
        assert 2023 in result["creation_trend"]
        assert 2022 in result["creation_trend"]
        assert result["creation_trend"][2023] == 2
        assert result["creation_trend"][2022] == 1


@patch("github_scraper.github.Github")
class TestFetchProfile:
    """Test profile fetching functionality."""

    def test_profile_fetch_basic(self, mock_github_class):
        """Test basic profile fetching."""
        # Mock the GitHub API response
        mock_github = Mock()
        mock_user = Mock()
        mock_github_class.return_value = mock_github
        mock_github.get_user.return_value = mock_user

        # Setup user mock
        mock_user.name = "Test User"
        mock_user.login = "testuser"
        mock_user.bio = "Test bio"
        mock_user.location = "Test Location"
        mock_user.company = "Test Company"
        mock_user.blog = "https://test.com"
        mock_user.twitter_username = "testuser"
        mock_user.email = "test@example.com"
        mock_user.public_repos = 10
        mock_user.followers = 50
        mock_user.following = 25
        mock_user.created_at = datetime(2020, 1, 1, tzinfo=timezone.utc)
        mock_user.hireable = True

        # Mock repositories
        mock_repo = Mock()
        mock_repo.fork = False
        mock_repo.name = "test-repo"
        mock_repo.description = "Test repository"
        mock_repo.language = "Python"
        mock_repo.stargazers_count = 10
        mock_repo.forks_count = 5
        mock_repo.watchers_count = 8
        mock_repo.size = 1000
        mock_repo.html_url = "https://github.com/testuser/test-repo"
        mock_repo.created_at = datetime(2023, 1, 1, tzinfo=timezone.utc)
        mock_repo.updated_at = datetime(2023, 12, 1, tzinfo=timezone.utc)
        mock_repo.get_topics.return_value = ["python", "testing"]
        mock_repo.has_wiki = True
        mock_repo.has_pages = False
        mock_repo.open_issues_count = 2
        mock_repo.license = Mock()
        mock_repo.license.name = "MIT"
        mock_repo.default_branch = "main"
        mock_repo.archived = False
        mock_repo.disabled = False

        mock_user.get_repos.return_value = [mock_repo]

        # Import and test the function (avoiding cache for testing)
        from github_scraper.github import fetch_profile

        result = fetch_profile("testuser", use_cache=False)

        # Verify basic profile data
        assert result["name"] == "Test User"
        assert result["username"] == "testuser"
        assert result["bio"] == "Test bio"
        assert result["location"] == "Test Location"
        assert result["company"] == "Test Company"
        assert len(result["repos"]) == 1

        # Verify analytics were generated
        assert "language_analysis" in result
        assert "contribution_patterns" in result
        assert "activity_score" in result
        assert "featured_repos" in result


if __name__ == "__main__":
    pytest.main([__file__])
