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
    """Build the enhanced GraphQL query to fetch comprehensive deeper signals."""
    return """
    query($username: String!) {
      user(login: $username) {
        login
        hasSponsorsListing
        sponsorshipsAsMaintainer(first: 1) {
          totalCount
        }
        sponsorshipsAsSponsor(first: 1) {
          totalCount
        }
        contributionsCollection {
          totalCommitContributions
          totalIssueContributions
          totalPullRequestContributions
          totalPullRequestReviewContributions
          restrictedContributionsCount
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                contributionCount
                date
              }
            }
          }
        }
        pullRequests(first: 100, states: [MERGED, CLOSED, OPEN]) {
          totalCount
          nodes {
            title
            state
            createdAt
            mergedAt
            reviews(first: 50) {
              totalCount
              nodes {
                state
                author {
                  login
                }
                createdAt
              }
            }
            reviewRequests(first: 10) {
              totalCount
              nodes {
                requestedReviewer {
                  ... on User {
                    login
                  }
                }
              }
            }
            commits(first: 1) {
              totalCount
            }
            additions
            deletions
            changedFiles
          }
        }
        issues(first: 100, states: [OPEN, CLOSED]) {
          totalCount
          nodes {
            title
            state
            createdAt
            closedAt
            author {
              login
            }
            assignees(first: 5) {
              nodes {
                login
              }
            }
            labels(first: 10) {
              nodes {
                name
              }
            }
            comments(first: 50) {
              totalCount
              nodes {
                author {
                  login
                }
                createdAt
              }
            }
          }
        }
        repositoryDiscussions(first: 100) {
          totalCount
          nodes {
            title
            createdAt
            author {
              login
            }
            category {
              name
            }
            comments(first: 50) {
              totalCount
              nodes {
                author {
                  login
                }
                createdAt
              }
            }
          }
        }
        projectsV2(first: 100) {
          totalCount
          nodes {
            title
            createdAt
            updatedAt
            items(first: 50) {
              totalCount
              nodes {
                creator {
                  login
                }
                createdAt
              }
            }
          }
        }
        followers(first: 1) {
          totalCount
        }
        following(first: 1) {
          totalCount
        }
        starredRepositories(first: 1) {
          totalCount
        }
        watching(first: 1) {
          totalCount
        }
        gists(first: 1) {
          totalCount
        }
        organizations(first: 10) {
          totalCount
          nodes {
            login
            name
            description
          }
        }
      }
    }
    """


def _process_graphql_response(data: Dict[str, Any], username: str) -> Dict[str, Any]:
    """Process comprehensive GraphQL response and calculate enhanced deeper signals."""
    if not data or not isinstance(data, dict):
        return {}
        
    user_data = data.get("user", {})
    
    if not user_data or not isinstance(user_data, dict):
        return {}
    
    # Initialize comprehensive response structure
    deeper_signals = {
        "contributions": {
            "total_commits": 0,
            "total_issues": 0,
            "total_prs": 0,
            "total_reviews": 0,
            "restricted_contributions": 0,
            "contribution_calendar": {},
            "activity_intensity": "Low",
        },
        "pull_requests": {
            "total": 0,
            "merged": 0,
            "closed": 0,
            "open": 0,
            "reviews_given": 0,
            "reviews_received": 0,
            "avg_pr_size": 0,
            "collaboration_score": 0,
        },
        "issues": {
            "opened": 0,
            "closed": 0,
            "comments_authored": 0,
            "assigned_issues": 0,
            "response_patterns": {},
        },
        "discussions": {
            "threads_started": 0,
            "comments_authored": 0,
            "categories_engaged": [],
        },
        "projects": {
            "items_added": 0,
            "projects_created": 0,
        },
        "social_metrics": {
            "followers": 0,
            "following": 0,
            "starred_repos": 0,
            "watching": 0,
            "gists": 0,
            "organizations": [],
        },
        "sponsorship": {
            "sponsors_enabled": False,
            "sponsoring_others": 0,
            "sponsored_projects": 0,
        },
        "professional_indicators": {
            "collaboration_strength": "Low",
            "community_engagement": "Low", 
            "technical_leadership": "Low",
            "consistency_score": 0,
        }
    }
    
    # Process contribution collection
    contributions = user_data.get("contributionsCollection", {}) or {}
    if contributions:
        deeper_signals["contributions"]["total_commits"] = contributions.get("totalCommitContributions", 0)
        deeper_signals["contributions"]["total_issues"] = contributions.get("totalIssueContributions", 0)
        deeper_signals["contributions"]["total_prs"] = contributions.get("totalPullRequestContributions", 0)
        deeper_signals["contributions"]["total_reviews"] = contributions.get("totalPullRequestReviewContributions", 0)
        deeper_signals["contributions"]["restricted_contributions"] = contributions.get("restrictedContributionsCount", 0)
        
        # Process contribution calendar
        calendar = contributions.get("contributionCalendar", {}) or {}
        if calendar:
            deeper_signals["contributions"]["contribution_calendar"]["total"] = calendar.get("totalContributions", 0)
            
            # Calculate activity intensity
            total_contrib = calendar.get("totalContributions", 0)
            if total_contrib > 1000:
                deeper_signals["contributions"]["activity_intensity"] = "Very High"
            elif total_contrib > 500:
                deeper_signals["contributions"]["activity_intensity"] = "High"
            elif total_contrib > 200:
                deeper_signals["contributions"]["activity_intensity"] = "Medium"
            else:
                deeper_signals["contributions"]["activity_intensity"] = "Low"
    
    # Process pull requests with enhanced metrics
    pull_requests = user_data.get("pullRequests", {}) or {}
    pr_nodes = pull_requests.get("nodes", []) or []
    deeper_signals["pull_requests"]["total"] = pull_requests.get("totalCount", 0)
    
    pr_sizes = []
    reviews_given = 0
    reviews_received_total = 0
    
    for pr in pr_nodes:
        if not pr or not isinstance(pr, dict):
            continue
            
        state = pr.get("state", "")
        if state == "MERGED":
            deeper_signals["pull_requests"]["merged"] += 1
        elif state == "CLOSED":
            deeper_signals["pull_requests"]["closed"] += 1
        elif state == "OPEN":
            deeper_signals["pull_requests"]["open"] += 1
        
        # Calculate PR size
        additions = pr.get("additions", 0) or 0
        deletions = pr.get("deletions", 0) or 0
        pr_size = additions + deletions
        if pr_size > 0:
            pr_sizes.append(pr_size)
        
        # Count reviews given by this user
        reviews = pr.get("reviews", {}) or {}
        review_nodes = reviews.get("nodes", []) or []
        reviews_received_total += len(review_nodes)
        
        for review in review_nodes:
            if not review or not isinstance(review, dict):
                continue
            author = review.get("author", {}) or {}
            if author and author.get("login") == username:
                reviews_given += 1
    
    deeper_signals["pull_requests"]["reviews_given"] = reviews_given
    deeper_signals["pull_requests"]["reviews_received"] = reviews_received_total
    deeper_signals["pull_requests"]["avg_pr_size"] = round(sum(pr_sizes) / max(len(pr_sizes), 1)) if pr_sizes else 0
    
    # Calculate collaboration score
    total_prs = deeper_signals["pull_requests"]["total"]
    if total_prs > 0:
        collaboration_score = (reviews_given + reviews_received_total) / total_prs
        deeper_signals["pull_requests"]["collaboration_score"] = round(collaboration_score, 2)
    
    # Process issues with enhanced analysis
    issues = user_data.get("issues", {}) or {}
    issue_nodes = issues.get("nodes", []) or []
    deeper_signals["issues"]["total"] = issues.get("totalCount", 0)
    
    assigned_count = 0
    comments_by_user = 0
    
    for issue in issue_nodes:
        if not issue or not isinstance(issue, dict):
            continue
            
        author = issue.get("author", {}) or {}
        if author and author.get("login") == username:
            if issue.get("state") == "CLOSED":
                deeper_signals["issues"]["closed"] += 1
            else:
                deeper_signals["issues"]["opened"] += 1
        
        # Check assignments
        assignees = issue.get("assignees", {}) or {}
        assignee_nodes = assignees.get("nodes", []) or []
        if any(assignee.get("login") == username for assignee in assignee_nodes):
            assigned_count += 1
        
        # Count comments by user
        comments = issue.get("comments", {}) or {}
        comment_nodes = comments.get("nodes", []) or []
        for comment in comment_nodes:
            if not comment or not isinstance(comment, dict):
                continue
            comment_author = comment.get("author", {}) or {}
            if comment_author and comment_author.get("login") == username:
                comments_by_user += 1
    
    deeper_signals["issues"]["assigned_issues"] = assigned_count
    deeper_signals["issues"]["comments_authored"] = comments_by_user
    
    # Process discussions
    discussions = user_data.get("repositoryDiscussions", {}) or {}
    discussion_nodes = discussions.get("nodes", []) or []
    deeper_signals["discussions"]["total"] = discussions.get("totalCount", 0)
    
    discussion_comments = 0
    categories = set()
    
    for discussion in discussion_nodes:
        if not discussion or not isinstance(discussion, dict):
            continue
            
        author = discussion.get("author", {}) or {}
        if author and author.get("login") == username:
            deeper_signals["discussions"]["threads_started"] += 1
        
        # Track categories
        category = discussion.get("category", {}) or {}
        if category and category.get("name"):
            categories.add(category["name"])
        
        # Count comments
        comments = discussion.get("comments", {}) or {}
        comment_nodes = comments.get("nodes", []) or []
        for comment in comment_nodes:
            if not comment or not isinstance(comment, dict):
                continue
            comment_author = comment.get("author", {}) or {}
            if comment_author and comment_author.get("login") == username:
                discussion_comments += 1
    
    deeper_signals["discussions"]["comments_authored"] = discussion_comments
    deeper_signals["discussions"]["categories_engaged"] = list(categories)
    
    # Process projects
    projects = user_data.get("projectsV2", {}) or {}
    project_nodes = projects.get("nodes", []) or []
    deeper_signals["projects"]["total"] = projects.get("totalCount", 0)
    
    items_added = 0
    for project in project_nodes:
        if not project or not isinstance(project, dict):
            continue
            
        deeper_signals["projects"]["projects_created"] += 1
        
        items = project.get("items", {}) or {}
        item_nodes = items.get("nodes", []) or []
        for item in item_nodes:
            if not item or not isinstance(item, dict):
                continue
            creator = item.get("creator", {}) or {}
            if creator and creator.get("login") == username:
                items_added += 1
    
    deeper_signals["projects"]["items_added"] = items_added
    
    # Process social metrics
    deeper_signals["social_metrics"]["followers"] = user_data.get("followers", {}).get("totalCount", 0)
    deeper_signals["social_metrics"]["following"] = user_data.get("following", {}).get("totalCount", 0)
    deeper_signals["social_metrics"]["starred_repos"] = user_data.get("starredRepositories", {}).get("totalCount", 0)
    deeper_signals["social_metrics"]["watching"] = user_data.get("watching", {}).get("totalCount", 0)
    deeper_signals["social_metrics"]["gists"] = user_data.get("gists", {}).get("totalCount", 0)
    
    # Process organizations
    organizations = user_data.get("organizations", {}) or {}
    org_nodes = organizations.get("nodes", []) or []
    for org in org_nodes:
        if org and isinstance(org, dict):
            deeper_signals["social_metrics"]["organizations"].append({
                "login": org.get("login"),
                "name": org.get("name"),
                "description": org.get("description"),
            })
    
    # Process sponsorship
    deeper_signals["sponsorship"]["sponsors_enabled"] = user_data.get("hasSponsorsListing", False)
    deeper_signals["sponsorship"]["sponsoring_others"] = user_data.get("sponsorshipsAsSponsor", {}).get("totalCount", 0)
    deeper_signals["sponsorship"]["sponsored_projects"] = user_data.get("sponsorshipsAsMaintainer", {}).get("totalCount", 0)
    
    # Calculate professional indicators
    # Collaboration strength
    total_interactions = (reviews_given + comments_by_user + discussion_comments)
    if total_interactions > 100:
        deeper_signals["professional_indicators"]["collaboration_strength"] = "Very High"
    elif total_interactions > 50:
        deeper_signals["professional_indicators"]["collaboration_strength"] = "High"
    elif total_interactions > 20:
        deeper_signals["professional_indicators"]["collaboration_strength"] = "Medium"
    else:
        deeper_signals["professional_indicators"]["collaboration_strength"] = "Low"
    
    # Community engagement
    community_score = (
        len(deeper_signals["social_metrics"]["organizations"]) * 3 +
        deeper_signals["discussions"]["threads_started"] * 2 +
        deeper_signals["sponsorship"]["sponsored_projects"] * 5 +
        (1 if deeper_signals["sponsorship"]["sponsors_enabled"] else 0) * 3
    )
    
    if community_score > 15:
        deeper_signals["professional_indicators"]["community_engagement"] = "Very High"
    elif community_score > 8:
        deeper_signals["professional_indicators"]["community_engagement"] = "High"
    elif community_score > 3:
        deeper_signals["professional_indicators"]["community_engagement"] = "Medium"
    else:
        deeper_signals["professional_indicators"]["community_engagement"] = "Low"
    
    # Technical leadership
    leadership_score = (
        deeper_signals["pull_requests"]["reviews_given"] * 2 +
        deeper_signals["projects"]["projects_created"] * 3 +
        assigned_count * 1 +
        deeper_signals["discussions"]["threads_started"] * 2
    )
    
    if leadership_score > 30:
        deeper_signals["professional_indicators"]["technical_leadership"] = "Very High"
    elif leadership_score > 15:
        deeper_signals["professional_indicators"]["technical_leadership"] = "High"
    elif leadership_score > 5:
        deeper_signals["professional_indicators"]["technical_leadership"] = "Medium"
    else:
        deeper_signals["professional_indicators"]["technical_leadership"] = "Low"
    
    # Consistency score (0-100)
    total_contributions = deeper_signals["contributions"]["contribution_calendar"].get("total", 0)
    if total_contributions > 0:
        consistency_score = min(100, (total_contributions / 365) * 100)
        deeper_signals["professional_indicators"]["consistency_score"] = round(consistency_score)
    
    return deeper_signals


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