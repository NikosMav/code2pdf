"""Website enrichment module for extracting valuable information from personal websites."""
from __future__ import annotations
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import asyncio
from urllib.parse import urlparse

# Check for aiofiles availability
try:
    import aiofiles
    AIOFILES_AVAILABLE = True
except ImportError:
    AIOFILES_AVAILABLE = False
    aiofiles = None

# Cache configuration
WEBSITE_CACHE_DIR = Path.home() / ".cache" / "code2pdf" / "websites"
WEBSITE_CACHE_DIR.mkdir(parents=True, exist_ok=True)

def _get_website_cache_path(url: str) -> Path:
    """Generate cache file path for a website URL."""
    url_hash = hashlib.md5(url.encode()).hexdigest()
    return WEBSITE_CACHE_DIR / f"website_{url_hash}.json"

def _is_website_cache_valid(cache_path: Path, max_age_hours: int = 24) -> bool:
    """Check if website cache file is still valid."""
    if not cache_path.exists():
        return False
    
    cache_age = datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)
    return cache_age < timedelta(hours=max_age_hours)

async def _save_website_cache(data: Dict[str, Any], cache_path: Path) -> None:
    """Save website data to cache file asynchronously."""
    try:
        if AIOFILES_AVAILABLE:
            async with aiofiles.open(cache_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(data, default=str, indent=2))
        else:
            # Fallback to synchronous write
            cache_path.write_text(json.dumps(data, default=str, indent=2), encoding='utf-8')
    except Exception:
        pass  # Ignore cache write errors

async def _load_website_cache(cache_path: Path) -> Optional[Dict[str, Any]]:
    """Load website data from cache file asynchronously."""
    try:
        if AIOFILES_AVAILABLE:
            async with aiofiles.open(cache_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                return json.loads(content)
        else:
            # Fallback to synchronous read
            content = cache_path.read_text(encoding='utf-8')
            return json.loads(content)
    except Exception:
        return None

def extract_urls_from_profile(profile_data: Dict[str, Any]) -> List[str]:
    """Extract potential website URLs from GitHub profile data."""
    urls = []
    
    # Primary website from blog field
    if profile_data.get('blog'):
        blog_url = profile_data['blog'].strip()
        if blog_url and not blog_url.startswith('http'):
            blog_url = f"https://{blog_url}"
        if blog_url and is_valid_personal_website(blog_url):
            urls.append(blog_url)
    
    # Look for URLs in bio
    if profile_data.get('bio'):
        bio_urls = extract_urls_from_text(profile_data['bio'])
        urls.extend([url for url in bio_urls if is_valid_personal_website(url)])
    
    # Look for URLs in repository descriptions
    for repo in profile_data.get('repos', []):
        if repo.get('description'):
            desc_urls = extract_urls_from_text(repo['description'])
            urls.extend([url for url in desc_urls if is_valid_personal_website(url)])
        
        # Check if repository has GitHub Pages
        if repo.get('has_pages') and repo.get('name'):
            username = profile_data.get('username', '')
            pages_url = f"https://{username}.github.io/{repo['name']}"
            if is_valid_personal_website(pages_url):
                urls.append(pages_url)
    
    # Remove duplicates while preserving order
    return list(dict.fromkeys(urls))

def extract_urls_from_text(text: str) -> List[str]:
    """Extract URLs from text using simple pattern matching."""
    import re
    
    # Pattern to match URLs
    url_pattern = r'https?://[^\s<>"\']+|www\.[^\s<>"\']+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s<>"\']*)?'
    
    urls = re.findall(url_pattern, text)
    processed_urls = []
    
    for url in urls:
        if not url.startswith('http'):
            if url.startswith('www.'):
                url = f"https://{url}"
            elif '.' in url:
                url = f"https://{url}"
        
        if url.startswith('http'):
            processed_urls.append(url)
    
    return processed_urls

def is_valid_personal_website(url: str) -> bool:
    """Check if URL appears to be a personal website worth crawling."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Skip common non-personal sites
        skip_domains = {
            'github.com', 'gitlab.com', 'bitbucket.org',
            'linkedin.com', 'twitter.com', 'x.com', 'facebook.com',
            'instagram.com', 'youtube.com', 'tiktok.com',
            'stackoverflow.com', 'stackexchange.com',
            'medium.com', 'dev.to', 'hashnode.com',
            'discord.gg', 'discord.com', 'slack.com',
            'google.com', 'amazon.com', 'microsoft.com',
            'apple.com', 'npmjs.com', 'pypi.org'
        }
        
        # Check if domain is in skip list
        for skip_domain in skip_domains:
            if domain == skip_domain or domain.endswith(f'.{skip_domain}'):
                return False
        
        # Accept common personal website patterns
        personal_patterns = [
            r'^[a-zA-Z0-9.-]+\.github\.io$',  # GitHub Pages
            r'^[a-zA-Z0-9.-]+\.netlify\.app$',  # Netlify
            r'^[a-zA-Z0-9.-]+\.vercel\.app$',  # Vercel
            r'^[a-zA-Z0-9.-]+\.herokuapp\.com$',  # Heroku
            r'^[a-zA-Z0-9.-]+\.(com|org|net|io|dev|me|personal)$',  # Personal domains
        ]
        
        import re
        for pattern in personal_patterns:
            if re.match(pattern, domain):
                return True
        
        # If it's not a known skip domain and has a reasonable TLD, consider it personal
        common_tlds = ['.com', '.org', '.net', '.io', '.dev', '.me', '.personal', '.tech', '.co']
        return any(domain.endswith(tld) for tld in common_tlds)
        
    except Exception:
        return False

def crawl_website_with_firecrawl(url: str, verbose: bool = False, firecrawl_scrape_func=None) -> Optional[Dict[str, Any]]:
    """
    Crawl a website using Firecrawl and extract valuable information.
    
    Args:
        url: The URL to crawl
        verbose: Whether to print verbose output
        firecrawl_scrape_func: Function to handle Firecrawl scraping (injected dependency)
    """
    try:
        if not firecrawl_scrape_func:
            if verbose:
                print(f"⚠️  Firecrawl not available, falling back to basic URL analysis for {url}")
            return create_basic_website_data(url)
        
        if verbose:
            print(f"🕷️  Crawling website: {url}")
        
        # Configure scraping options for personal websites
        # First extract general information
        scrape_result = firecrawl_scrape_func(
            url=url,
            formats=["markdown", "extract"],
            onlyMainContent=True,
            waitFor=5000,  # Wait for dynamic content (increased for MUI components)
            extract={
                "prompt": "Extract personal and professional information including: name, title/role, skills, experience, education, projects, contact information, about/bio sections, and any other relevant career or personal details. For skills, focus on soft skills, methodologies, and practices (not technical tools).",
                "schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Person's full name"},
                        "title": {"type": "string", "description": "Professional title or role"},
                        "bio": {"type": "string", "description": "About/bio section content"},
                        "skills": {"type": "array", "items": {"type": "string"}, "description": "Soft skills, methodologies, practices, and competencies (e.g., Problem Solving, Team Leadership, Agile Development, UX Design, Project Management)"},
                        "experience": {"type": "array", "items": {"type": "string"}, "description": "Work experience and roles"},
                        "education": {"type": "array", "items": {"type": "string"}, "description": "Educational background"},
                        "projects": {"type": "array", "items": {"type": "string"}, "description": "Notable projects or work"},
                        "services": {"type": "array", "items": {"type": "string"}, "description": "Services offered or areas of expertise"},
                        "contact": {"type": "object", "description": "Contact information"},
                        "social": {"type": "object", "description": "Social media links"},
                        "achievements": {"type": "array", "items": {"type": "string"}, "description": "Awards, certifications, or notable achievements"}
                    }
                }
            }
        )
        
        # Then extract technologies with focused approach
        if scrape_result:
            tech_result = firecrawl_scrape_func(
                url=url,
                formats=["extract"],
                onlyMainContent=True,
                waitFor=5000,
                extract={
                    "prompt": "Extract all technologies, programming languages, frameworks, tools, libraries, and platforms mentioned on this website. Look for technology sections, chips, badges, tech stacks, and any technical tools. Include content from interactive elements like buttons and badges.",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "technologies": {
                                "type": "array", 
                                "items": {"type": "string"}, 
                                "description": "All technologies, programming languages, frameworks, tools, libraries, and platforms found"
                            }
                        }
                    }
                }
            )
            
            # Merge the technology data into the main result
            if tech_result and 'extract' in tech_result:
                tech_data = tech_result['extract']
                if 'technologies' in tech_data and 'extract' in scrape_result:
                    scrape_result['extract']['technologies'] = tech_data['technologies']
        
        if scrape_result and 'data' in scrape_result:
            return process_scraped_data(scrape_result['data'], url, verbose)
        elif scrape_result:
            return process_scraped_data(scrape_result, url, verbose)
        
    except Exception as e:
        if verbose:
            print(f"❌ Error crawling {url}: {str(e)}")
        return create_basic_website_data(url)
    
    return None

def create_basic_website_data(url: str) -> Dict[str, Any]:
    """Create basic website data when Firecrawl is not available."""
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    
    return {
        "url": url,
        "scraped_at": datetime.now().isoformat(),
        "content": {
            "raw_markdown": f"# {domain}\n\nPersonal website: {url}",
            "extracted_data": {
                "name": "",
                "title": "",
                "bio": f"Personal website at {domain}",
                "skills": [],
                "experience": [],
                "projects": [],
                "contact": {"website": url}
            },
        },
        "insights": {
            "personal_info": {
                "name": "",
                "title": "",
                "bio": f"Personal website at {domain}",
                "contact": {"website": url},
                "social": {}
            },
            "professional": {
                "skills": [],
                "experience": [],
                "education": [],
                "projects": [],
                "services": [],
                "achievements": []
            },
            "website_type": "personal_portfolio",
            "technologies_mentioned": []
        }
    }

def process_scraped_data(scraped_data: Dict[str, Any], url: str, verbose: bool = False) -> Dict[str, Any]:
    """Process and normalize scraped website data."""
    processed = {
        "url": url,
        "scraped_at": datetime.now().isoformat(),
        "content": {
            "raw_markdown": scraped_data.get('markdown', ''),
            "extracted_data": scraped_data.get('extract', {}),
        },
        "insights": {}
    }
    
    # Extract structured information
    extracted = scraped_data.get('extract', {})
    
    if extracted:
        processed["insights"] = {
            "personal_info": {
                "name": extracted.get('name', ''),
                "title": extracted.get('title', ''),
                "bio": extracted.get('bio', ''),
                "contact": extracted.get('contact', {}),
                "social": extracted.get('social', {})
            },
            "professional": {
                "skills": extracted.get('skills', []),
                "technologies": extracted.get('technologies', []),
                "experience": extracted.get('experience', []),
                "education": extracted.get('education', []),
                "projects": extracted.get('projects', []),
                "services": extracted.get('services', []),
                "achievements": extracted.get('achievements', [])
            }
        }
    
    # Analyze content for additional insights
    markdown_content = scraped_data.get('markdown', '').lower()
    
    # Detect website type
    if any(keyword in markdown_content for keyword in ['portfolio', 'resume', 'cv', 'about me']):
        processed["insights"]["website_type"] = "personal_portfolio"
    elif any(keyword in markdown_content for keyword in ['blog', 'articles', 'posts']):
        processed["insights"]["website_type"] = "blog"
    elif any(keyword in markdown_content for keyword in ['freelance', 'services', 'hire', 'consulting']):
        processed["insights"]["website_type"] = "professional_services"
    else:
        processed["insights"]["website_type"] = "general"
    
    # Extract key technologies mentioned
    tech_keywords = [
        'python', 'javascript', 'typescript', 'react', 'vue', 'angular', 'node',
        'java', 'kotlin', 'swift', 'golang', 'rust', 'c++', 'c#',
        'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'terraform',
        'mongodb', 'postgresql', 'mysql', 'redis',
        'machine learning', 'ai', 'data science', 'blockchain'
    ]
    
    found_technologies = [tech for tech in tech_keywords if tech in markdown_content]
    if found_technologies:
        processed["insights"]["technologies_mentioned"] = found_technologies
    
    if verbose:
        print(f"✅ Processed website data from {url}")
        if extracted.get('name'):
            print(f"   Found: {extracted['name']}")
        if extracted.get('title'):
            print(f"   Title: {extracted['title']}")
        if found_technologies:
            print(f"   Technologies: {', '.join(found_technologies[:5])}")
    
    return processed

async def enrich_profile_with_websites(profile_data: Dict[str, Any], use_cache: bool = True, verbose: bool = False) -> Dict[str, Any]:
    """Enrich GitHub profile data with information from personal websites."""
    urls = extract_urls_from_profile(profile_data)
    
    if not urls:
        if verbose:
            print("🔍 No personal websites found in profile")
        return profile_data
    
    if verbose:
        print(f"🌐 Found {len(urls)} potential website(s): {', '.join(urls)}")
    
    enriched_profile = profile_data.copy()
    enriched_profile["website_enrichment"] = {
        "discovered_urls": urls,
        "crawled_websites": [],
        "enrichment_summary": {}
    }
    
    # Process each URL
    for url in urls[:3]:  # Limit to 3 websites to avoid excessive crawling
        cache_path = _get_website_cache_path(url)
        
        # Check cache first
        website_data = None
        if use_cache and _is_website_cache_valid(cache_path):
            if verbose:
                print(f"📦 Loading cached data for {url}")
            website_data = await _load_website_cache(cache_path)
        
        # Crawl if not cached
        if not website_data:
            if verbose:
                print(f"🕷️  Crawling {url}...")
            
                         # Note: This is a synchronous call wrapped for the async context
            loop = asyncio.get_event_loop()
            website_data = await loop.run_in_executor(None, crawl_website_with_firecrawl, url, verbose, None)
            
            # Cache the result
            if website_data and use_cache:
                await _save_website_cache(website_data, cache_path)
        
        if website_data:
            enriched_profile["website_enrichment"]["crawled_websites"].append(website_data)
    
    # Generate enrichment summary
    if enriched_profile["website_enrichment"]["crawled_websites"]:
        enriched_profile["website_enrichment"]["enrichment_summary"] = generate_enrichment_summary(
            enriched_profile["website_enrichment"]["crawled_websites"]
        )
    
    return enriched_profile

def generate_enrichment_summary(website_data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate a summary of insights from all crawled websites."""
    summary = {
        "websites_crawled": len(website_data_list),
        "combined_insights": {
            "additional_skills": set(),
            "additional_technologies": set(),
            "additional_experience": [],
            "additional_projects": [],
            "professional_services": [],
            "website_types": [],
            "technologies_mentioned": set(),
            "contact_info": {},
            "bio_snippets": []
        }
    }
    
    for website_data in website_data_list:
        insights = website_data.get("insights", {})
        
        # Collect website types
        if insights.get("website_type"):
            summary["combined_insights"]["website_types"].append(insights["website_type"])
        
        # Collect technologies
        if insights.get("technologies_mentioned"):
            summary["combined_insights"]["technologies_mentioned"].update(insights["technologies_mentioned"])
        
        # Collect professional information
        professional = insights.get("professional", {})
        if professional.get("skills"):
            summary["combined_insights"]["additional_skills"].update(professional["skills"])
        if professional.get("technologies"):
            summary["combined_insights"]["additional_technologies"].update(professional["technologies"])
        if professional.get("experience"):
            summary["combined_insights"]["additional_experience"].extend(professional["experience"])
        if professional.get("projects"):
            summary["combined_insights"]["additional_projects"].extend(professional["projects"])
        if professional.get("services"):
            summary["combined_insights"]["professional_services"].extend(professional["services"])
        
        # Collect personal information
        personal = insights.get("personal_info", {})
        if personal.get("bio"):
            summary["combined_insights"]["bio_snippets"].append(personal["bio"])
        if personal.get("contact"):
            summary["combined_insights"]["contact_info"].update(personal["contact"])
    
    # Convert sets back to lists for JSON serialization
    summary["combined_insights"]["additional_skills"] = list(summary["combined_insights"]["additional_skills"])
    summary["combined_insights"]["additional_technologies"] = list(summary["combined_insights"]["additional_technologies"])
    summary["combined_insights"]["technologies_mentioned"] = list(summary["combined_insights"]["technologies_mentioned"])
    
    return summary

def sync_enrich_profile_with_websites(profile_data: Dict[str, Any], use_cache: bool = True, verbose: bool = False, firecrawl_scrape_func=None) -> Dict[str, Any]:
    """Synchronous wrapper for profile enrichment."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(enrich_profile_with_websites_sync(profile_data, use_cache, verbose, firecrawl_scrape_func))
    finally:
        loop.close()

async def enrich_profile_with_websites_sync(profile_data: Dict[str, Any], use_cache: bool = True, verbose: bool = False, firecrawl_scrape_func=None) -> Dict[str, Any]:
    """Enrich GitHub profile data with information from personal websites (with firecrawl function injection)."""
    urls = extract_urls_from_profile(profile_data)
    
    if not urls:
        if verbose:
            print("🔍 No personal websites found in profile")
        return profile_data
    
    if verbose:
        print(f"🌐 Found {len(urls)} potential website(s): {', '.join(urls)}")
    
    enriched_profile = profile_data.copy()
    enriched_profile["website_enrichment"] = {
        "discovered_urls": urls,
        "crawled_websites": [],
        "enrichment_summary": {}
    }
    
    # Process each URL
    for url in urls[:3]:  # Limit to 3 websites to avoid excessive crawling
        cache_path = _get_website_cache_path(url)
        
        # Check cache first
        website_data = None
        if use_cache and _is_website_cache_valid(cache_path):
            if verbose:
                print(f"📦 Loading cached data for {url}")
            website_data = await _load_website_cache(cache_path)
        
        # Crawl if not cached
        if not website_data:
            if verbose:
                print(f"🕷️  Crawling {url}...")
            
            # Note: This is a synchronous call wrapped for the async context
            loop = asyncio.get_event_loop()
            website_data = await loop.run_in_executor(None, crawl_website_with_firecrawl, url, verbose, firecrawl_scrape_func)
            
            # Cache the result
            if website_data and use_cache:
                await _save_website_cache(website_data, cache_path)
        
        if website_data:
            enriched_profile["website_enrichment"]["crawled_websites"].append(website_data)
    
    # Generate enrichment summary
    if enriched_profile["website_enrichment"]["crawled_websites"]:
        enriched_profile["website_enrichment"]["enrichment_summary"] = generate_enrichment_summary(
            enriched_profile["website_enrichment"]["crawled_websites"]
        )
    
    return enriched_profile 