"""Enhanced GitHub profile analyzer with data-driven insights."""
from __future__ import annotations
from datetime import datetime, timezone
from collections import Counter
from typing import Dict, List, Any

from github import Github
from github.GithubException import RateLimitExceededException


def calculate_activity_score(repos: List[Dict]) -> int:
    """Calculate activity score based on stars, forks, and recent updates."""
    if not repos:
        return 0
    
    total_stars = sum(repo.get('stars', 0) for repo in repos)
    total_forks = sum(repo.get('forks', 0) for repo in repos)
    recent_repos = sum(1 for repo in repos if repo.get('days_since_update', 365) < 90)
    
    return min(100, (total_stars * 2) + (total_forks * 3) + (recent_repos * 5))


def analyze_languages(repos: List[Dict]) -> Dict[str, Any]:
    """Analyze programming language usage and expertise."""
    lang_stats = Counter()
    lang_projects = Counter()
    
    for repo in repos:
        if repo.get('language'):
            lang_stats[repo['language']] += repo.get('stars', 0) + 1  # Weight by popularity
            lang_projects[repo['language']] += 1
    
    # Calculate expertise levels
    expertise = {}
    for lang, count in lang_projects.items():
        if count >= 5:
            expertise[lang] = "Expert"
        elif count >= 3:
            expertise[lang] = "Advanced"
        elif count >= 2:
            expertise[lang] = "Intermediate"
        else:
            expertise[lang] = "Beginner"
    
    return {
        'top_languages': dict(lang_stats.most_common(8)),
        'language_count': len(lang_projects),
        'expertise_levels': expertise,
        'most_used': lang_projects.most_common(1)[0] if lang_projects else ("None", 0)
    }


def analyze_contribution_patterns(repos: List[Dict], user_data: Dict) -> Dict[str, Any]:
    """Analyze contribution and collaboration patterns."""
    total_repos = len(repos)
    total_stars = sum(repo.get('stars', 0) for repo in repos)
    total_forks = sum(repo.get('forks', 0) for repo in repos)
    
    # Calculate project impact
    impact_score = "Low"
    if total_stars > 50:
        impact_score = "High"
    elif total_stars > 10:
        impact_score = "Medium"
    
    # Recent activity analysis
    recent_projects = sum(1 for repo in repos if repo.get('days_since_update', 365) < 90)
    activity_level = "Low"
    if recent_projects >= 3:
        activity_level = "High"
    elif recent_projects >= 1:
        activity_level = "Medium"
    
    return {
        'total_repositories': total_repos,
        'total_stars_earned': total_stars,
        'total_forks_received': total_forks,
        'recent_active_projects': recent_projects,
        'impact_score': impact_score,
        'activity_level': activity_level,
        'avg_stars_per_repo': round(total_stars / max(total_repos, 1), 1),
        'collaboration_ratio': round(total_forks / max(total_stars, 1), 2) if total_stars > 0 else 0
    }


def fetch_profile(username: str, token: str | None = None) -> dict:
    """Fetch comprehensive GitHub profile with enhanced analytics."""
    try:
        gh = Github(token) if token else Github()
        user = gh.get_user(username)

        # Basic profile data
        profile_data = {
            "name": user.name or user.login,
            "username": user.login,
            "bio": user.bio,
            "location": user.location,
            "company": user.company,
            "blog": user.blog,
            "twitter_username": user.twitter_username,
            "public_repos": user.public_repos,
            "followers": user.followers,
            "following": user.following,
            "created_at": user.created_at,
            "hireable": user.hireable,
            "repos": [],
        }

        # Calculate account age
        account_age = (datetime.now(timezone.utc) - user.created_at).days
        profile_data["account_age_years"] = round(account_age / 365.25, 1)

        # Enhanced repository data (rate-limit friendly)
        repo_count = 0
        for repo in user.get_repos():
            if repo.fork:
                continue
            
            repo_count += 1
            if repo_count > 10:  # Further reduced to be more conservative
                break
                
            # Calculate days since last update
            days_since_update = (datetime.now(timezone.utc) - repo.updated_at).days
            
            repo_data = {
                "name": repo.name,
                "description": repo.description,
                "language": repo.language,
                "stars": repo.stargazers_count,
                "forks": repo.forks_count,
                "watchers": repo.watchers_count,
                "size": repo.size,  # KB
                "html_url": repo.html_url,
                "created_at": repo.created_at,
                "updated_at": repo.updated_at,
                "days_since_update": days_since_update,
                "topics": [],  # Skip topics to avoid rate limiting
                "has_wiki": repo.has_wiki,
                "has_pages": repo.has_pages,
                "open_issues": repo.open_issues_count,
                "license": repo.license.name if repo.license else None,
            }
            profile_data["repos"].append(repo_data)

        # Sort repositories by stars (descending)
        profile_data["repos"] = sorted(profile_data["repos"], key=lambda r: r["stars"], reverse=True)

        # Generate insights
        profile_data["language_analysis"] = analyze_languages(profile_data["repos"])
        profile_data["contribution_patterns"] = analyze_contribution_patterns(profile_data["repos"], profile_data)
        profile_data["activity_score"] = calculate_activity_score(profile_data["repos"])
        
        # Featured repositories (top 8 by stars)
        profile_data["featured_repos"] = profile_data["repos"][:8]
        
        return profile_data
        
    except RateLimitExceededException:
        raise RuntimeError(
            "GitHub API rate limit exceeded!\n\n"
            "To avoid rate limits:\n"
            "1. Get a GitHub personal access token from: https://github.com/settings/tokens\n"
            "2. Run: code2pdf NikosMav --token YOUR_TOKEN\n\n"
            "Rate limits reset hourly for unauthenticated requests (60 requests/hour)\n"
            "With a token, you get 5000 requests/hour."
        )
    except Exception as e:
        raise RuntimeError(f"Error fetching GitHub profile: {str(e)}")