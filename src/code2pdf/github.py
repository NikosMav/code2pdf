"""Enhanced GitHub profile analyzer with caching, async support, and comprehensive insights."""
from __future__ import annotations
import json
import hashlib
from datetime import datetime, timezone, timedelta
from collections import Counter
from pathlib import Path
from typing import Dict, List, Any, Optional
import asyncio
import aiohttp
import aiofiles

from github import Github
from github.GithubException import RateLimitExceededException, UnknownObjectException


# Cache configuration
CACHE_DIR = Path.home() / ".cache" / "code2pdf"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _get_cache_path(username: str, token_hash: str = "") -> Path:
    """Generate cache file path for a user."""
    cache_key = hashlib.md5(f"{username}:{token_hash}".encode()).hexdigest()
    return CACHE_DIR / f"profile_{cache_key}.json"


def _is_cache_valid(cache_path: Path, max_age_hours: int = 1) -> bool:
    """Check if cache file is still valid."""
    if not cache_path.exists():
        return False
    
    cache_age = datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)
    return cache_age < timedelta(hours=max_age_hours)


async def _save_cache(data: Dict[str, Any], cache_path: Path) -> None:
    """Save data to cache file asynchronously."""
    try:
        async with aiofiles.open(cache_path, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(data, default=str, indent=2))
    except Exception:
        pass  # Ignore cache write errors


async def _load_cache(cache_path: Path) -> Optional[Dict[str, Any]]:
    """Load data from cache file asynchronously."""
    try:
        async with aiofiles.open(cache_path, 'r', encoding='utf-8') as f:
            content = await f.read()
            return json.loads(content)
    except Exception:
        return None


def calculate_activity_score(repos: List[Dict]) -> int:
    """Calculate comprehensive activity score based on multiple factors."""
    if not repos:
        return 0
    
    total_stars = sum(repo.get('stars', 0) for repo in repos)
    total_forks = sum(repo.get('forks', 0) for repo in repos)
    total_watchers = sum(repo.get('watchers', 0) for repo in repos)
    recent_repos = sum(1 for repo in repos if repo.get('days_since_update', 365) < 90)
    
    # Enhanced scoring algorithm
    star_score = min(40, total_stars * 0.5)
    fork_score = min(25, total_forks * 0.8)
    watcher_score = min(15, total_watchers * 0.3)
    activity_score = min(20, recent_repos * 4)
    
    return min(100, int(star_score + fork_score + watcher_score + activity_score))


def analyze_languages(repos: List[Dict]) -> Dict[str, Any]:
    """Enhanced programming language analysis with trends and specializations."""
    lang_stats = Counter()
    lang_projects = Counter()
    lang_stars = Counter()
    lang_sizes = Counter()
    
    for repo in repos:
        if repo.get('language'):
            lang = repo['language']
            stars = repo.get('stars', 0)
            size = repo.get('size', 0)
            
            lang_stats[lang] += stars + 1  # Weight by popularity
            lang_projects[lang] += 1
            lang_stars[lang] += stars
            lang_sizes[lang] += size
    
    # Calculate expertise levels with more nuanced criteria
    expertise = {}
    for lang, count in lang_projects.items():
        avg_stars = lang_stars[lang] / count if count > 0 else 0
        
        if count >= 5 and avg_stars >= 10:
            expertise[lang] = "Expert"
        elif count >= 5 or avg_stars >= 5:
            expertise[lang] = "Advanced"
        elif count >= 3 or avg_stars >= 2:
            expertise[lang] = "Intermediate"
        else:
            expertise[lang] = "Beginner"
    
    return {
        'top_languages': dict(lang_stats.most_common(10)),
        'language_count': len(lang_projects),
        'expertise_levels': expertise,
        'most_used': lang_projects.most_common(1)[0] if lang_projects else ("None", 0),
        'most_popular': lang_stars.most_common(1)[0] if lang_stars else ("None", 0),
        'specializations': [lang for lang, level in expertise.items() if level in ["Expert", "Advanced"]],
    }


def analyze_contribution_patterns(repos: List[Dict], user_data: Dict) -> Dict[str, Any]:
    """Enhanced contribution and collaboration pattern analysis."""
    total_repos = len(repos)
    total_stars = sum(repo.get('stars', 0) for repo in repos)
    total_forks = sum(repo.get('forks', 0) for repo in repos)
    total_watchers = sum(repo.get('watchers', 0) for repo in repos)
    total_issues = sum(repo.get('open_issues', 0) for repo in repos)
    
    # Time-based analysis
    now = datetime.now(timezone.utc)
    recent_projects = sum(1 for repo in repos if repo.get('days_since_update', 365) < 90)
    active_projects = sum(1 for repo in repos if repo.get('days_since_update', 365) < 30)
    
    # Repository health indicators
    documented_repos = sum(1 for repo in repos if repo.get('has_wiki') or repo.get('description'))
    licensed_repos = sum(1 for repo in repos if repo.get('license'))
    
    # Calculate impact and activity levels
    impact_score = "Low"
    if total_stars > 100:
        impact_score = "High"
    elif total_stars > 25:
        impact_score = "Medium"
    
    activity_level = "Low"
    if active_projects >= 2:
        activity_level = "High"
    elif recent_projects >= 1:
        activity_level = "Medium"
    
    # Community engagement metrics
    engagement_ratio = total_forks / max(total_stars, 1) if total_stars > 0 else 0
    community_health = (documented_repos + licensed_repos) / max(total_repos, 1)
    
    return {
        'total_repositories': total_repos,
        'total_stars_earned': total_stars,
        'total_forks_received': total_forks,
        'total_watchers': total_watchers,
        'total_open_issues': total_issues,
        'recent_active_projects': recent_projects,
        'currently_active_projects': active_projects,
        'impact_score': impact_score,
        'activity_level': activity_level,
        'avg_stars_per_repo': round(total_stars / max(total_repos, 1), 1),
        'collaboration_ratio': round(engagement_ratio, 2),
        'community_health_score': round(community_health * 100, 1),
        'documentation_rate': round(documented_repos / max(total_repos, 1) * 100, 1),
        'licensing_rate': round(licensed_repos / max(total_repos, 1) * 100, 1),
    }


def analyze_repository_trends(repos: List[Dict]) -> Dict[str, Any]:
    """Analyze repository creation and update trends."""
    if not repos:
        return {}
    
    # Group by creation year
    creation_years = Counter()
    update_months = Counter()
    
    for repo in repos:
        if repo.get('created_at'):
            creation_years[repo['created_at'].year] += 1
        if repo.get('updated_at'):
            update_months[f"{repo['updated_at'].year}-{repo['updated_at'].month:02d}"] += 1
    
    return {
        'creation_trend': dict(creation_years.most_common()),
        'recent_activity': dict(list(update_months.most_common(12))),
        'most_productive_year': creation_years.most_common(1)[0] if creation_years else (None, 0),
    }


def fetch_profile(username: str, token: Optional[str] = None, use_cache: bool = True, verbose: bool = False) -> Dict[str, Any]:
    """Fetch comprehensive GitHub profile with enhanced analytics and caching."""
    
    # Setup cache
    token_hash = hashlib.md5(token.encode()).hexdigest() if token else ""
    cache_path = _get_cache_path(username, token_hash)
    
    # Check cache first
    if use_cache and _is_cache_valid(cache_path):
        if verbose:
            print("📦 Loading from cache...")
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
                # Convert date strings back to datetime objects
                for repo in cached_data.get('repos', []):
                    if repo.get('created_at'):
                        repo['created_at'] = datetime.fromisoformat(repo['created_at'].replace('Z', '+00:00'))
                    if repo.get('updated_at'):
                        repo['updated_at'] = datetime.fromisoformat(repo['updated_at'].replace('Z', '+00:00'))
                if cached_data.get('created_at'):
                    cached_data['created_at'] = datetime.fromisoformat(cached_data['created_at'].replace('Z', '+00:00'))
                return cached_data
        except Exception:
            pass  # Fall through to fresh fetch
    
    try:
        gh = Github(token) if token else Github()
        user = gh.get_user(username)

        if verbose:
            print(f"👤 Fetching profile for {user.name or user.login}...")

        # Basic profile data
        profile_data = {
            "name": user.name or user.login,
            "username": user.login,
            "bio": user.bio,
            "location": user.location,
            "company": user.company,
            "blog": user.blog,
            "twitter_username": user.twitter_username,
            "email": user.email,
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

        if verbose:
            print(f"📊 Analyzing {user.public_repos} repositories...")

        # Enhanced repository data with better rate limit management
        repo_count = 0
        max_repos = 15  # Increased but still conservative
        
        for repo in user.get_repos(sort="updated", direction="desc"):
            if repo.fork:
                continue
            
            repo_count += 1
            if repo_count > max_repos:
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
                "size": repo.size,
                "html_url": repo.html_url,
                "created_at": repo.created_at,
                "updated_at": repo.updated_at,
                "days_since_update": days_since_update,
                "topics": repo.get_topics()[:5] if hasattr(repo, 'get_topics') else [],
                "has_wiki": repo.has_wiki,
                "has_pages": repo.has_pages,
                "open_issues": repo.open_issues_count,
                "license": repo.license.name if repo.license else None,
                "default_branch": repo.default_branch,
                "archived": repo.archived,
                "disabled": repo.disabled,
            }
            profile_data["repos"].append(repo_data)
            
            if verbose and repo_count % 5 == 0:
                print(f"   📁 Processed {repo_count} repositories...")

        # Sort repositories by stars (descending)
        profile_data["repos"] = sorted(profile_data["repos"], key=lambda r: r["stars"], reverse=True)

        if verbose:
            print("🧮 Generating insights...")

        # Generate comprehensive insights
        profile_data["language_analysis"] = analyze_languages(profile_data["repos"])
        profile_data["contribution_patterns"] = analyze_contribution_patterns(profile_data["repos"], profile_data)
        profile_data["repository_trends"] = analyze_repository_trends(profile_data["repos"])
        profile_data["activity_score"] = calculate_activity_score(profile_data["repos"])
        
        # Featured repositories (top by stars, but ensure diversity)
        featured_repos = []
        seen_languages = set()
        
        for repo in profile_data["repos"]:
            if len(featured_repos) >= 8:
                break
            
            # Prioritize diversity in languages while respecting star ranking
            lang = repo.get('language', 'Other')
            if len(featured_repos) < 4 or lang not in seen_languages or len(seen_languages) < 3:
                featured_repos.append(repo)
                seen_languages.add(lang)
        
        profile_data["featured_repos"] = featured_repos
        
        # Cache the results
        if use_cache:
            try:
                with open(cache_path, 'w', encoding='utf-8') as f:
                    json.dump(profile_data, f, default=str, indent=2)
                if verbose:
                    print("💾 Cached results for future use")
            except Exception:
                pass  # Ignore cache write errors
        
        return profile_data
        
    except RateLimitExceededException:
        raise RuntimeError(
            "🚫 GitHub API rate limit exceeded!\n\n"
            "💡 To avoid rate limits:\n"
            "   1. Get a GitHub personal access token: https://github.com/settings/tokens\n"
            "   2. Run: code2pdf build username --token YOUR_TOKEN\n\n"
            "⏰ Rate limits:\n"
            "   • Without token: 60 requests/hour\n"
            "   • With token: 5,000 requests/hour\n"
            "   • Resets every hour"
        )
    except UnknownObjectException:
        raise RuntimeError(f"❌ GitHub user '{username}' not found. Please check the username.")
    except Exception as e:
        raise RuntimeError(f"💥 Error fetching GitHub profile: {str(e)}")


# Async version for future use
async def fetch_profile_async(username: str, token: Optional[str] = None, use_cache: bool = True) -> Dict[str, Any]:
    """Async version of profile fetching (placeholder for future implementation)."""
    # This would require rewriting the GitHub API calls to use aiohttp
    # For now, we'll run the sync version in a thread pool
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, fetch_profile, username, token, use_cache)