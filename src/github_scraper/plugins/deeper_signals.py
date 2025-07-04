"""Deeper GitHub signals plugin for advanced profile analytics."""

from __future__ import annotations
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional
import httpx


# Cache configuration - reuse existing cache directory pattern
def _get_cache_path(username: str, token_hash: str = "") -> Path:
    """Generate cache file path for deeper signals data."""
    from ..github import CACHE_DIR
    cache_key = hashlib.md5(f"deeper_signals:{username}:{token_hash}".encode()).hexdigest()
    return CACHE_DIR / f"deeper_signals_{cache_key}.json"


def _is_cache_valid(cache_path: Path, max_age_hours: int = 2) -> bool:
    """Check if cache file is still valid (2h TTL)."""
    if not cache_path.exists():
        return False
    
    cache_age = datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)
    return cache_age < timedelta(hours=max_age_hours)


def _build_graphql_query(username: str) -> str:
    """Build the GraphQL query to fetch deeper signals."""
    return """
    query($username: String!) {
      user(login: $username) {
        login
        hasSponsorsListing
        sponsorshipsAsMaintainer(first: 1) {
          totalCount
        }
        pullRequests(first: 100, states: [MERGED, CLOSED]) {
          totalCount
          nodes {
            reviews(first: 50) {
              totalCount
              nodes {
                state
                author {
                  login
                }
              }
            }
          }
        }
        issues(first: 100, states: [OPEN, CLOSED]) {
          totalCount
          nodes {
            state
            author {
              login
            }
            comments(first: 50) {
              totalCount
              nodes {
                author {
                  login
                }
              }
            }
          }
        }
        repositoryDiscussions(first: 100) {
          totalCount
          nodes {
            author {
              login
            }
            comments(first: 50) {
              totalCount
              nodes {
                author {
                  login
                }
              }
            }
          }
        }
        projectsV2(first: 100) {
          totalCount
          nodes {
            items(first: 50) {
              totalCount
              nodes {
                creator {
                  login
                }
              }
            }
          }
        }
      }
    }
    """


def _process_graphql_response(data: Dict[str, Any], username: str) -> Dict[str, Any]:
    """Process GraphQL response and calculate deeper signals."""
    if not data or not isinstance(data, dict):
        return {}
        
    user_data = data.get("user", {})
    
    if not user_data or not isinstance(user_data, dict):
        return {}
    
    # Process PR reviews
    pr_reviews_total = 0
    pr_reviews_approved = 0
    pr_reviews_changes_requested = 0
    
    pull_requests = user_data.get("pullRequests", {}) or {}
    pr_nodes = pull_requests.get("nodes", []) or []
    
    for pr in pr_nodes:
        if not pr or not isinstance(pr, dict):
            continue
        reviews = pr.get("reviews", {}) or {}
        review_nodes = reviews.get("nodes", []) or []
        
        for review in review_nodes:
            if not review or not isinstance(review, dict):
                continue
            author = review.get("author", {}) or {}
            if author and author.get("login") == username:
                pr_reviews_total += 1
                if review.get("state") == "APPROVED":
                    pr_reviews_approved += 1
                elif review.get("state") == "CHANGES_REQUESTED":
                    pr_reviews_changes_requested += 1
    
    approval_ratio = pr_reviews_approved / max(pr_reviews_total, 1)
    
    # Process issues
    issues_opened = 0
    issues_closed_by_user = 0
    issue_comments_authored = 0
    
    issues = user_data.get("issues", {}) or {}
    issue_nodes = issues.get("nodes", []) or []
    
    for issue in issue_nodes:
        if not issue or not isinstance(issue, dict):
            continue
        author = issue.get("author", {}) or {}
        if author and author.get("login") == username:
            issues_opened += 1
            if issue.get("state") == "CLOSED":
                issues_closed_by_user += 1
        
        comments = issue.get("comments", {}) or {}
        comment_nodes = comments.get("nodes", []) or []
        for comment in comment_nodes:
            if not comment or not isinstance(comment, dict):
                continue
            comment_author = comment.get("author", {}) or {}
            if comment_author and comment_author.get("login") == username:
                issue_comments_authored += 1
    
    # Process discussions
    discussions_started = 0
    discussion_comments_authored = 0
    
    repo_discussions = user_data.get("repositoryDiscussions", {}) or {}
    discussion_nodes = repo_discussions.get("nodes", []) or []
    
    for discussion in discussion_nodes:
        if not discussion or not isinstance(discussion, dict):
            continue
        author = discussion.get("author", {}) or {}
        if author and author.get("login") == username:
            discussions_started += 1
            
        comments = discussion.get("comments", {}) or {}
        comment_nodes = comments.get("nodes", []) or []
        for comment in comment_nodes:
            if not comment or not isinstance(comment, dict):
                continue
            comment_author = comment.get("author", {}) or {}
            if comment_author and comment_author.get("login") == username:
                discussion_comments_authored += 1
    
    # Process projects
    projects_items_added = 0
    
    projects_v2 = user_data.get("projectsV2", {}) or {}
    project_nodes = projects_v2.get("nodes", []) or []
    
    for project in project_nodes:
        if not project or not isinstance(project, dict):
            continue
        items = project.get("items", {}) or {}
        item_nodes = items.get("nodes", []) or []
        for item in item_nodes:
            if not item or not isinstance(item, dict):
                continue
            creator = item.get("creator", {}) or {}
            if creator and creator.get("login") == username:
                projects_items_added += 1
    
    return {
        "pr_reviews": {
            "total": pr_reviews_total,
            "approvals": pr_reviews_approved,
            "request_changes": pr_reviews_changes_requested,
            "approval_ratio": round(approval_ratio, 2)
        },
        "issues": {
            "opened": issues_opened,
            "closed_by_user": issues_closed_by_user,
            "comments_authored": issue_comments_authored
        },
        "discussions": {
            "threads_started": discussions_started,
            "comments_authored": discussion_comments_authored
        },
        "projects": {
            "items_added": projects_items_added
        },
        "sponsors_enabled": user_data.get("hasSponsorsListing", False)
    }


def collect(
    username: str,
    token: Optional[str] = None,
    use_cache: bool = True,
    verbose: bool = False
) -> Dict[str, Any]:
    """
    Collect deeper GitHub signals for a user.
    
    Args:
        username: GitHub username
        token: GitHub personal access token (required for GraphQL API)
        use_cache: Whether to use cached data
        verbose: Whether to print verbose output
        
    Returns:
        Dictionary containing deeper signals data
    """
    if not token:
        if verbose:
            print("⚠️  GitHub token required for deeper signals - skipping")
        return {}
    
    # Setup cache
    token_hash = hashlib.md5(token.encode()).hexdigest()
    cache_path = _get_cache_path(username, token_hash)
    
    # Check cache first
    if use_cache and _is_cache_valid(cache_path):
        if verbose:
            print("📦 Loading deeper signals from cache...")
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass  # Fall through to fresh fetch
    
    try:
        if verbose:
            print(f"🔍 Fetching deeper signals for {username}...")
        
        # GraphQL API endpoint
        graphql_url = "https://api.github.com/graphql"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        query = _build_graphql_query(username)
        payload = {
            "query": query,
            "variables": {"username": username}
        }
        
        with httpx.Client(timeout=30.0) as client:
            response = client.post(graphql_url, headers=headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            
            if "errors" in data:
                raise RuntimeError(f"GraphQL errors: {data['errors']}")
            
            # Process the response
            deeper_signals = _process_graphql_response(data.get("data", {}), username)
            
            # Cache the results
            if use_cache and deeper_signals:
                try:
                    with open(cache_path, "w", encoding="utf-8") as f:
                        json.dump(deeper_signals, f, indent=2)
                    if verbose:
                        print("💾 Cached deeper signals for future use")
                except Exception:
                    pass  # Ignore cache write errors
            
            return deeper_signals
            
    except httpx.RequestError as e:
        if verbose:
            print(f"❌ Network error fetching deeper signals: {e}")
        return {}
    except httpx.HTTPStatusError as e:
        if verbose:
            print(f"❌ HTTP error fetching deeper signals: {e}")
        return {}
    except Exception as e:
        if verbose:
            print(f"❌ Error fetching deeper signals: {e}")
        return {} 