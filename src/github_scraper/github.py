"""Enhanced GitHub profile analyzer with caching, async support, and comprehensive insights."""

from __future__ import annotations
import json
import hashlib
import re
from datetime import datetime, timezone, timedelta
from collections import Counter
from pathlib import Path
from typing import Dict, List, Any, Optional
from github import Github
from github.GithubException import RateLimitExceededException, UnknownObjectException


# Cache configuration
CACHE_DIR = Path.home() / ".cache" / "github-scraper"
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


def calculate_activity_score(repos: List[Dict]) -> int:
    """Calculate comprehensive activity score based on multiple factors."""
    if not repos:
        return 0

    total_stars = sum(repo.get("stars", 0) for repo in repos)
    total_forks = sum(repo.get("forks", 0) for repo in repos)
    total_watchers = sum(repo.get("watchers", 0) for repo in repos)
    recent_repos = sum(1 for repo in repos if repo.get("days_since_update", 365) < 90)

    # Enhanced scoring algorithm
    star_score = min(40, total_stars * 0.5)
    fork_score = min(25, total_forks * 0.8)
    watcher_score = min(15, total_watchers * 0.3)
    activity_score = min(20, recent_repos * 4)

    return min(100, int(star_score + fork_score + watcher_score + activity_score))


def get_language_stats(repos: List[Dict]) -> Dict[str, Any]:
    """Get basic programming language statistics."""
    lang_projects: Counter[str] = Counter()
    lang_stars: Counter[str] = Counter()

    for repo in repos:
        if repo.get("language"):
            lang = repo["language"]
            stars = repo.get("stars", 0)
            lang_projects[lang] += 1
            lang_stars[lang] += stars

    return {
        "languages_by_project_count": dict(lang_projects.most_common()),
        "languages_by_stars": dict(lang_stars.most_common()),
        "language_count": len(lang_projects),
        "most_used": lang_projects.most_common(1)[0] if lang_projects else ("None", 0),
    }


def get_contribution_stats(repos: List[Dict], user_data: Dict) -> Dict[str, Any]:
    """Get basic contribution statistics."""
    total_repos = len(repos)
    total_stars = sum(repo.get("stars", 0) for repo in repos)
    total_forks = sum(repo.get("forks", 0) for repo in repos)
    total_watchers = sum(repo.get("watchers", 0) for repo in repos)
    total_issues = sum(repo.get("open_issues", 0) for repo in repos)

    # Time-based counts
    recent_projects = sum(
        1 for repo in repos if repo.get("days_since_update", 365) < 90
    )
    active_projects = sum(
        1 for repo in repos if repo.get("days_since_update", 365) < 30
    )

    # Repository counts
    documented_repos = sum(
        1 for repo in repos if repo.get("has_wiki") or repo.get("description")
    )
    licensed_repos = sum(1 for repo in repos if repo.get("license"))

    return {
        "total_repositories": total_repos,
        "total_stars_earned": total_stars,
        "total_forks_received": total_forks,
        "total_watchers": total_watchers,
        "total_open_issues": total_issues,
        "recent_active_projects": recent_projects,
        "currently_active_projects": active_projects,
        "avg_stars_per_repo": round(total_stars / max(total_repos, 1), 1),
        "documented_repos": documented_repos,
        "licensed_repos": licensed_repos,
    }





def fetch_profile(
    username: str,
    token: Optional[str] = None,
    use_cache: bool = True,
    verbose: bool = False,
    enrich_websites: bool = False,
    config_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Fetch comprehensive GitHub profile with enhanced analytics and caching."""
    
    # Use provided config or import default
    if config_data is None:
        from .config import DEFAULT_CONFIG
        config_data = DEFAULT_CONFIG

    # Setup cache
    token_hash = hashlib.md5(token.encode()).hexdigest() if token else ""
    cache_path = _get_cache_path(username, token_hash)

    # Check cache first
    if use_cache and _is_cache_valid(cache_path):
        if verbose:
            print("📦 Loading from cache...")

        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                cached_data = json.load(f)
                # Convert date strings back to datetime objects
                for repo in cached_data.get("repos", []):
                    if repo.get("created_at"):
                        repo["created_at"] = datetime.fromisoformat(
                            repo["created_at"].replace("Z", "+00:00")
                        )
                    if repo.get("updated_at"):
                        repo["updated_at"] = datetime.fromisoformat(
                            repo["updated_at"].replace("Z", "+00:00")
                        )
                if cached_data.get("created_at"):
                    cached_data["created_at"] = datetime.fromisoformat(
                        cached_data["created_at"].replace("Z", "+00:00")
                    )
                return cached_data
        except Exception:
            pass  # Fall through to fresh fetch

    try:
        gh = Github(token) if token else Github()
        user = gh.get_user(username)

        if verbose:
            print(f"👤 Fetching profile for {user.name or user.login}...")

        # Basic profile data
        profile_data: Dict[str, Any] = {
            "name": user.name or user.login,
            "username": user.login,
            "bio": user.bio,
            "location": user.location,
            "company": user.company,
            "blog": user.blog,
            "twitter_username": getattr(user, "twitter_username", None),
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

        # Fetch extended user data (organizations, gists, social accounts)
        if verbose:
            print("🔍 Fetching extended user data...")
        extended_user_data = fetch_extended_user_data(user, gh, config_data, verbose)
        profile_data["extended_user"] = extended_user_data

        # Fetch and analyze profile README (username/username repository)
        if verbose:
            print("📋 Analyzing profile README...")
        profile_readme_data = fetch_profile_readme(gh, username, verbose)
        profile_data["profile_readme"] = profile_readme_data

        if verbose:
            print(f"📊 Analyzing {user.public_repos} repositories...")

        # Enhanced repository data with better rate limit management
        repo_count = 0
        max_repos = config_data.get("github", {}).get("max_repos", 100)

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
                "topics": repo.get_topics()[:5] if hasattr(repo, "get_topics") else [],
                "has_wiki": repo.has_wiki,
                "has_pages": repo.has_pages,
                "open_issues": repo.open_issues_count,
                "license": repo.license.name if repo.license else None,
                "default_branch": repo.default_branch,
                "archived": repo.archived,
                "disabled": repo.disabled,
            }
            
            # Fetch README content if enabled
            if config_data.get("github", {}).get("fetch_readme", True):
                readme_data = fetch_readme_content(repo, verbose)
                repo_data["readme"] = readme_data
                
            # Fetch extended data (contributors, releases, etc.)
            extended_data = fetch_extended_repo_data(repo, config_data, verbose)
            repo_data["extended"] = extended_data
            
            profile_data["repos"].append(repo_data)

            if verbose and repo_count % 5 == 0:
                print(f"   📁 Processed {repo_count} repositories...")

        # Sort repositories by stars (descending)
        profile_data["repos"] = sorted(
            profile_data["repos"], key=lambda r: r["stars"], reverse=True
        )

        if verbose:
            print("🧮 Generating insights...")

        # Generate basic statistics (raw data only)
        profile_data["language_analysis"] = get_language_stats(profile_data["repos"])
        profile_data["contribution_patterns"] = get_contribution_stats(
            profile_data["repos"], profile_data
        )
        profile_data["activity_score"] = calculate_activity_score(profile_data["repos"])

        # Featured repositories (top by stars)
        max_featured = config_data.get("cv", {}).get("max_featured_repos", 15)
        profile_data["featured_repos"] = profile_data["repos"][:max_featured]

        # Website enrichment if requested
        if enrich_websites:
            if verbose:
                print("🌐 Starting website enrichment...")

            # Initialize default website enrichment structure
            profile_data["website_enrichment"] = {
                "crawled_websites": [],
                "enrichment_summary": {
                    "combined_insights": {}
                }
            }

            # Import and use website enrichment
            try:
                from .website_enrichment import sync_enrich_profile_with_websites
                from .mcp_integration import create_firecrawl_wrapper

                # Get the real Firecrawl wrapper function
                firecrawl_scrape_wrapper = create_firecrawl_wrapper()

                # Enrich the profile with website data
                profile_data = sync_enrich_profile_with_websites(
                    profile_data,
                    use_cache=use_cache,
                    verbose=verbose,
                    firecrawl_scrape_func=firecrawl_scrape_wrapper,
                )

                if verbose:
                    enrichment = profile_data.get("website_enrichment", {})
                    if enrichment.get("crawled_websites"):
                        print(
                            f"✅ Enriched profile with {len(enrichment['crawled_websites'])} website(s)"
                        )
                    else:
                        print("ℹ️  No additional website data found")

            except ImportError as e:
                if verbose:
                    print(f"⚠️  Website enrichment module not available: {e}")
            except Exception as e:
                if verbose:
                    print(f"⚠️  Website enrichment failed: {e}")

        # Cache the results
        if use_cache:
            try:
                with open(cache_path, "w", encoding="utf-8") as f:
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
            "   2. Run: github-scraper build username --token YOUR_TOKEN\n\n"
            "⏰ Rate limits:\n"
            "   • Without token: 60 requests/hour\n"
            "   • With token: 5,000 requests/hour\n"
            "   • Resets every hour"
        )
    except UnknownObjectException:
        raise RuntimeError(
            f"❌ GitHub user '{username}' not found. Please check the username."
        )
    except Exception as e:
        raise RuntimeError(f"💥 Error fetching GitHub profile: {str(e)}")


def fetch_readme_content(repo, verbose: bool = False) -> Dict[str, Any]:
    """
    Fetch README content from a repository.
    
    Args:
        repo: GitHub repository object
        verbose: Whether to print verbose output
        
    Returns:
        Dictionary containing README content:
        {
            "has_readme": <bool>,
            "content": <str>,     # UTF-8 decoded markdown
            "length": <int>       # number of characters
        }
    """
    readme_data = {
        "has_readme": False,
        "content": "",
        "length": 0,
    }
    
    try:
        # Try common README file names
        readme_files = ["README.md", "readme.md", "README.txt", "README.rst", "README"]
        readme_content = None
        
        for filename in readme_files:
            try:
                readme_file = repo.get_contents(filename)
                if readme_file and hasattr(readme_file, 'decoded_content'):
                    readme_content = readme_file.decoded_content.decode('utf-8')
                    readme_data["has_readme"] = True
                    break
            except Exception:
                continue
                
        if readme_content:
            readme_data["content"] = readme_content
            readme_data["length"] = len(readme_content)
            
            if verbose:
                print(f"   📖 README found: {readme_data['length']} chars")
                
    except Exception as e:
        if verbose:
            print(f"   ⚠️  Could not fetch README: {str(e)}")
    
    return readme_data





def fetch_extended_repo_data(repo, config_data: Dict[str, Any], verbose: bool = False) -> Dict[str, Any]:
    """
    Fetch extended repository data including contributors, releases, languages, etc.
    
    Args:
        repo: GitHub repository object
        config_data: Configuration dictionary
        verbose: Whether to print verbose output
        
    Returns:
        Dictionary containing extended repository data
    """
    github_config = config_data.get("github", {})
    extended_data = {
        "contributors": [],
        "releases": [],
        "languages": {},
        "workflows": [],
        "security": {
            "has_security_policy": False,
            "vulnerability_alerts": False,
        }
    }
    
    try:
        # Fetch contributors if enabled
        if github_config.get("fetch_contributors", True):
            max_contributors = github_config.get("max_contributors_per_repo", 10)
            contributors = []
            try:
                for contributor in repo.get_contributors()[:max_contributors]:
                    contributors.append({
                        "login": contributor.login,
                        "contributions": contributor.contributions,
                        "avatar_url": contributor.avatar_url,
                    })
                extended_data["contributors"] = contributors
                if verbose and contributors:
                    print(f"   👥 Found {len(contributors)} contributors")
            except Exception as e:
                if verbose:
                    print(f"   ⚠️  Could not fetch contributors: {str(e)}")
        
        # Fetch releases if enabled
        if github_config.get("fetch_releases", True):
            max_releases = github_config.get("max_releases_per_repo", 5)
            releases = []
            try:
                for release in repo.get_releases()[:max_releases]:
                    releases.append({
                        "tag_name": release.tag_name,
                        "name": release.title or release.tag_name,
                        "published_at": release.published_at,
                        "prerelease": release.prerelease,
                        "draft": release.draft,
                        "download_count": sum(asset.download_count for asset in release.get_assets()),
                    })
                extended_data["releases"] = releases
                if verbose and releases:
                    print(f"   🏷️  Found {len(releases)} releases")
            except Exception as e:
                if verbose:
                    print(f"   ⚠️  Could not fetch releases: {str(e)}")
        
        # Fetch language breakdown if enabled
        if github_config.get("fetch_languages", True):
            try:
                languages = repo.get_languages()
                extended_data["languages"] = dict(languages)
                if verbose and languages:
                    print(f"   💬 Languages: {', '.join(list(languages.keys())[:3])}")
            except Exception as e:
                if verbose:
                    print(f"   ⚠️  Could not fetch languages: {str(e)}")
        
        # Fetch workflows if enabled
        if github_config.get("fetch_workflows", True):
            workflows = []
            try:
                for workflow in repo.get_workflows():
                    workflows.append({
                        "name": workflow.name,
                        "state": workflow.state,
                        "path": workflow.path,
                        "created_at": workflow.created_at,
                        "updated_at": workflow.updated_at,
                    })
                extended_data["workflows"] = workflows
                if verbose and workflows:
                    print(f"   ⚙️  Found {len(workflows)} workflows")
            except Exception as e:
                if verbose:
                    print(f"   ⚠️  Could not fetch workflows: {str(e)}")
        
        # Check for security features
        try:
            # Check for security policy
            try:
                repo.get_contents("SECURITY.md")
                extended_data["security"]["has_security_policy"] = True
            except:
                try:
                    repo.get_contents(".github/SECURITY.md")
                    extended_data["security"]["has_security_policy"] = True
                except:
                    pass
            
            # Note: Vulnerability alerts require special permissions to access
            # extended_data["security"]["vulnerability_alerts"] = repo.get_vulnerability_alert()
            
        except Exception:
            pass  # Security features might not be accessible
            
    except Exception as e:
        if verbose:
            print(f"   ❌ Error fetching extended repo data: {str(e)}")
    
    return extended_data


def fetch_extended_user_data(user, gh, config_data: Dict[str, Any], verbose: bool = False) -> Dict[str, Any]:
    """
    Fetch extended user data including organizations, gists, social accounts.
    
    Args:
        user: GitHub user object
        gh: GitHub API client
        config_data: Configuration dictionary
        verbose: Whether to print verbose output
        
    Returns:
        Dictionary containing extended user data
    """
    user_config = config_data.get("user_data", {})
    extended_data = {
        "organizations": [],
        "gists": [],
        "social_accounts": [],
        "achievements": [],
        "stats": {
            "total_commits": 0,
            "total_issues": 0,
            "total_pull_requests": 0,
        }
    }
    
    try:
        # Fetch organizations if enabled
        if user_config.get("fetch_organizations", True):
            max_orgs = user_config.get("max_organizations", 10)
            organizations = []
            try:
                for org in user.get_orgs()[:max_orgs]:
                    org_data = {
                        "login": org.login,
                        "name": org.name,
                        "description": org.description,
                        "public_repos": org.public_repos,
                        "followers": org.followers,
                        "avatar_url": org.avatar_url,
                        "blog": org.blog,
                        "location": org.location,
                    }
                    organizations.append(org_data)
                extended_data["organizations"] = organizations
                if verbose and organizations:
                    print(f"   🏢 Found {len(organizations)} organizations")
            except Exception as e:
                if verbose:
                    print(f"   ⚠️  Could not fetch organizations: {str(e)}")
        
        # Fetch gists if enabled
        if user_config.get("fetch_gists", True):
            max_gists = user_config.get("max_gists", 20)
            gists = []
            try:
                for gist in user.get_gists()[:max_gists]:
                    gist_data = {
                        "id": gist.id,
                        "description": gist.description,
                        "public": gist.public,
                        "files_count": len(gist.files),
                        "created_at": gist.created_at,
                        "updated_at": gist.updated_at,
                        "comments": gist.comments,
                        "html_url": gist.html_url,
                    }
                    # Get file types from gist
                    file_types = []
                    for filename, file_obj in gist.files.items():
                        if hasattr(file_obj, 'language') and file_obj.language:
                            file_types.append(file_obj.language)
                    gist_data["languages"] = list(set(file_types))
                    gists.append(gist_data)
                extended_data["gists"] = gists
                if verbose and gists:
                    print(f"   📝 Found {len(gists)} gists")
            except Exception as e:
                if verbose:
                    print(f"   ⚠️  Could not fetch gists: {str(e)}")
        
        # Fetch social accounts if enabled  
        if user_config.get("fetch_social_accounts", True):
            social_accounts = []
            try:
                # Extract social information from available fields
                if user.twitter_username:
                    social_accounts.append({
                        "platform": "Twitter",
                        "username": user.twitter_username,
                        "url": f"https://twitter.com/{user.twitter_username}"
                    })
                    
                # Check blog field for social links
                if user.blog:
                    blog_url = user.blog.strip()
                    if blog_url:
                        # Detect social platforms from blog URL
                        social_patterns = {
                            "LinkedIn": r"linkedin\.com/in/([^/]+)",
                            "Twitter": r"twitter\.com/([^/]+)",
                            "Medium": r"medium\.com/@?([^/]+)",
                            "Dev.to": r"dev\.to/([^/]+)",
                            "Personal Website": r".*"  # Fallback for other URLs
                        }
                        
                        for platform, pattern in social_patterns.items():
                            if platform == "Personal Website":
                                # Only add as personal website if it doesn't match other patterns
                                if not any(re.search(p, blog_url, re.IGNORECASE) for p in list(social_patterns.values())[:-1]):
                                    social_accounts.append({
                                        "platform": platform,
                                        "url": blog_url
                                    })
                                break
                            else:
                                match = re.search(pattern, blog_url, re.IGNORECASE)
                                if match:
                                    username = match.group(1) if match.groups() else None
                                    social_accounts.append({
                                        "platform": platform,
                                        "username": username,
                                        "url": blog_url
                                    })
                                    break
                                    
                extended_data["social_accounts"] = social_accounts
                if verbose and social_accounts:
                    print(f"   🌐 Found {len(social_accounts)} social accounts")
            except Exception as e:
                if verbose:
                    print(f"   ⚠️  Could not process social accounts: {str(e)}")
        
        # Note: GitHub achievements/badges are not accessible via API
        # They would require scraping the profile page
        
    except Exception as e:
        if verbose:
            print(f"   ❌ Error fetching extended user data: {str(e)}")
    
    return extended_data











def fetch_profile_readme(gh, username: str, verbose: bool = False) -> Dict[str, Any]:
    """
    Fetch GitHub profile README from username/username repository.
    
    Args:
        gh: GitHub API client
        username: GitHub username
        verbose: Whether to print verbose output
        
    Returns:
        Dictionary containing profile README content:
        {
            "has_profile_readme": <bool>,
            "content": <str>,     # UTF-8 decoded markdown
            "length": <int>       # number of characters
        }
    """
    profile_readme_data = {
        "has_profile_readme": False,
        "content": "",
        "length": 0,
    }
    
    # Try different variations of the profile repository name
    repo_variations = [
        f"{username}/{username}",  # Exact case match
        f"{username}/{username.lower()}",  # Lowercase repo name
        f"{username.lower()}/{username.lower()}",  # Both lowercase
    ]
    
    profile_repo = None
    repo_name_used = None
    
    for repo_name in repo_variations:
        try:
            profile_repo = gh.get_repo(repo_name)
            repo_name_used = repo_name
            if verbose:
                print(f"   📋 Found profile repository: {repo_name}")
            break
        except Exception:
            continue
    
    if not profile_repo:
        if verbose:
            print(f"   ℹ️  No profile README repository found (tried {', '.join(repo_variations)})")
        return profile_readme_data
    
    try:
        # Try to get README from profile repository
        readme_files = ["README.md", "readme.md", "README.txt", "README.rst", "README"]
        readme_content = None
        
        for filename in readme_files:
            try:
                readme_file = profile_repo.get_contents(filename)
                if readme_file and hasattr(readme_file, 'decoded_content'):
                    readme_content = readme_file.decoded_content.decode('utf-8')
                    profile_readme_data["has_profile_readme"] = True
                    break
            except Exception:
                continue
                
        if readme_content:
            profile_readme_data["content"] = readme_content
            profile_readme_data["length"] = len(readme_content)
            
            if verbose:
                print(f"   📖 Profile README analyzed: {profile_readme_data['length']} chars")
        else:
            if verbose:
                print(f"   ℹ️  Profile repository {repo_name_used} found but no README detected")
                
    except Exception as e:
        if verbose:
            print(f"   ⚠️  Error reading profile README: {str(e)}")
    
    return profile_readme_data






