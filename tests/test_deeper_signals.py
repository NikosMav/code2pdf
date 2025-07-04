"""Tests for the deeper signals plugin."""

import json
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from github_scraper.plugins.deeper_signals import (
    collect,
    _build_graphql_query,
    _process_graphql_response,
    _get_cache_path,
    _is_cache_valid
)


@pytest.fixture
def mock_graphql_response():
    """Sample GraphQL response for testing."""
    return {
        "data": {
            "user": {
                "login": "testuser",
                "hasSponsorsListing": True,
                "sponsorshipsAsMaintainer": {
                    "totalCount": 5
                },
                "pullRequests": {
                    "totalCount": 25,
                    "nodes": [
                        {
                            "reviews": {
                                "totalCount": 3,
                                "nodes": [
                                    {"state": "APPROVED", "author": {"login": "testuser"}},
                                    {"state": "CHANGES_REQUESTED", "author": {"login": "testuser"}},
                                    {"state": "APPROVED", "author": {"login": "otheruser"}}
                                ]
                            }
                        }
                    ]
                },
                "issues": {
                    "totalCount": 15,
                    "nodes": [
                        {
                            "state": "CLOSED",
                            "author": {"login": "testuser"},
                            "comments": {
                                "totalCount": 5,
                                "nodes": [
                                    {"author": {"login": "testuser"}},
                                    {"author": {"login": "otheruser"}}
                                ]
                            }
                        },
                        {
                            "state": "OPEN",
                            "author": {"login": "testuser"},
                            "comments": {
                                "totalCount": 2,
                                "nodes": [
                                    {"author": {"login": "testuser"}}
                                ]
                            }
                        }
                    ]
                },
                "repositoryDiscussions": {
                    "totalCount": 8,
                    "nodes": [
                        {
                            "author": {"login": "testuser"},
                            "comments": {
                                "totalCount": 3,
                                "nodes": [
                                    {"author": {"login": "testuser"}},
                                    {"author": {"login": "otheruser"}}
                                ]
                            }
                        }
                    ]
                },
                "projectsV2": {
                    "totalCount": 2,
                    "nodes": [
                        {
                            "items": {
                                "totalCount": 10,
                                "nodes": [
                                    {"creator": {"login": "testuser"}},
                                    {"creator": {"login": "testuser"}},
                                    {"creator": {"login": "otheruser"}}
                                ]
                            }
                        }
                    ]
                }
            }
        }
    }


def test_build_graphql_query():
    """Test GraphQL query building."""
    query = _build_graphql_query("testuser")
    assert "query($username: String!)" in query
    assert "user(login: $username)" in query
    assert "hasSponsorsListing" in query
    assert "sponsorshipsAsMaintainer" in query
    assert "pullRequests" in query
    assert "issues" in query
    assert "repositoryDiscussions" in query
    assert "projectsV2" in query


def test_process_graphql_response(mock_graphql_response):
    """Test processing of GraphQL response."""
    result = _process_graphql_response(mock_graphql_response["data"], "testuser")
    
    # Check structure
    assert "pr_reviews" in result
    assert "issues" in result
    assert "discussions" in result
    assert "projects" in result
    assert "sponsors_enabled" in result
    
    # Check PR review data
    assert result["pr_reviews"]["total"] == 2  # Only testuser reviews
    assert result["pr_reviews"]["approvals"] == 1
    assert result["pr_reviews"]["request_changes"] == 1
    assert result["pr_reviews"]["approval_ratio"] == 0.5
    
    # Check issue data
    assert result["issues"]["opened"] == 2
    assert result["issues"]["closed_by_user"] == 1
    assert result["issues"]["comments_authored"] == 2
    
    # Check discussion data
    assert result["discussions"]["threads_started"] == 1
    assert result["discussions"]["comments_authored"] == 1
    
    # Check project data
    assert result["projects"]["items_added"] == 2
    
    # Check sponsorship
    assert result["sponsors_enabled"] is True


def test_process_empty_response():
    """Test processing of empty GraphQL response."""
    empty_response = {"user": {}}
    result = _process_graphql_response(empty_response, "testuser")
    assert result == {}


def test_process_null_response():
    """Test processing of null/None GraphQL response."""
    # Test completely null response
    result = _process_graphql_response(None, "testuser")
    assert result == {}
    
    # Test response with null user
    null_user_response = {"user": None}
    result = _process_graphql_response(null_user_response, "testuser")
    assert result == {}
    
    # Test response with null fields
    null_fields_response = {
        "user": {
            "login": "testuser",
            "hasSponsorsListing": True,
            "pullRequests": None,
            "issues": None,
            "repositoryDiscussions": None,
            "projectsV2": None
        }
    }
    result = _process_graphql_response(null_fields_response, "testuser")
    # Should return valid structure with zero values
    assert "pr_reviews" in result
    assert result["pr_reviews"]["total"] == 0
    assert result["issues"]["opened"] == 0
    assert result["discussions"]["threads_started"] == 0
    assert result["projects"]["items_added"] == 0


def test_collect_without_token():
    """Test collect function without GitHub token."""
    result = collect("testuser", token=None, verbose=True)
    assert result == {}


@patch('github_scraper.plugins.deeper_signals.httpx.Client')
def test_collect_with_token(mock_client, mock_graphql_response):
    """Test collect function with GitHub token."""
    # Mock the HTTP client
    mock_response = MagicMock()
    mock_response.json.return_value = mock_graphql_response
    mock_response.raise_for_status.return_value = None
    
    mock_client_instance = MagicMock()
    mock_client_instance.post.return_value = mock_response
    mock_client.return_value.__enter__.return_value = mock_client_instance
    
    result = collect("testuser", token="test_token", use_cache=False, verbose=True)
    
    # Verify the result structure
    assert "pr_reviews" in result
    assert "issues" in result
    assert "discussions" in result
    assert "projects" in result
    assert "sponsors_enabled" in result
    
    # Verify HTTP call was made
    mock_client_instance.post.assert_called_once()
    call_args = mock_client_instance.post.call_args
    assert call_args[0][0] == "https://api.github.com/graphql"
    assert call_args[1]["headers"]["Authorization"] == "Bearer test_token"


@patch('github_scraper.plugins.deeper_signals.httpx.Client')
def test_collect_with_graphql_error(mock_client):
    """Test collect function with GraphQL errors."""
    # Mock the HTTP client to return GraphQL errors
    mock_response = MagicMock()
    mock_response.json.return_value = {"errors": [{"message": "Field 'test' doesn't exist"}]}
    mock_response.raise_for_status.return_value = None
    
    mock_client_instance = MagicMock()
    mock_client_instance.post.return_value = mock_response
    mock_client.return_value.__enter__.return_value = mock_client_instance
    
    result = collect("testuser", token="test_token", use_cache=False, verbose=True)
    assert result == {}


@patch('github_scraper.plugins.deeper_signals.httpx.Client')
def test_collect_with_network_error(mock_client):
    """Test collect function with network error."""
    # Mock the HTTP client to raise a request error
    mock_client_instance = MagicMock()
    mock_client_instance.post.side_effect = Exception("Network error")
    mock_client.return_value.__enter__.return_value = mock_client_instance
    
    result = collect("testuser", token="test_token", use_cache=False, verbose=True)
    assert result == {}


def test_cache_path_generation():
    """Test cache path generation."""
    path = _get_cache_path("testuser", "token_hash")
    assert path.name.startswith("deeper_signals_")
    assert path.name.endswith(".json")
    assert "testuser" not in path.name  # Should be hashed
    assert "token_hash" not in path.name  # Should be hashed


def test_cache_validity():
    """Test cache validity checking."""
    # Test with non-existent file
    fake_path = Path("/non/existent/path.json")
    assert not _is_cache_valid(fake_path)
    
    # Test with valid cache would require creating actual files
    # This is tested implicitly through integration tests 