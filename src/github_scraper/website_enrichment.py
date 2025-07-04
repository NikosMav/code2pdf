"""Website enrichment module for extracting valuable information from personal websites."""

from __future__ import annotations
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import asyncio
from urllib.parse import urlparse



# Cache configuration
WEBSITE_CACHE_DIR = Path.home() / ".cache" / "github-scraper" / "websites"
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


def _save_website_cache(data: Dict[str, Any], cache_path: Path) -> None:
    """Save website data to cache file."""
    try:
        cache_path.write_text(
            json.dumps(data, default=str, indent=2), encoding="utf-8"
        )
    except Exception:
        pass  # Ignore cache write errors


def _load_website_cache(cache_path: Path) -> Optional[Dict[str, Any]]:
    """Load website data from cache file."""
    try:
        content = cache_path.read_text(encoding="utf-8")
        return json.loads(content)
    except Exception:
        return None


def extract_urls_from_profile(profile_data: Dict[str, Any]) -> List[str]:
    """Extract potential website URLs from GitHub profile data."""
    urls = []

    # Primary website from blog field
    if profile_data.get("blog"):
        blog_url = profile_data["blog"].strip()
        if blog_url and not blog_url.startswith("http"):
            blog_url = f"https://{blog_url}"
        if blog_url and is_valid_personal_website(blog_url):
            urls.append(blog_url)

    # Look for URLs in bio
    if profile_data.get("bio"):
        bio_urls = extract_urls_from_text(profile_data["bio"])
        urls.extend([url for url in bio_urls if is_valid_personal_website(url)])

    # Look for URLs in repository descriptions
    for repo in profile_data.get("repos", []):
        if repo.get("description"):
            desc_urls = extract_urls_from_text(repo["description"])
            urls.extend([url for url in desc_urls if is_valid_personal_website(url)])

        # Check if repository has GitHub Pages
        if repo.get("has_pages") and repo.get("name"):
            username = profile_data.get("username", "")
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
        if not url.startswith("http"):
            if url.startswith("www."):
                url = f"https://{url}"
            elif "." in url:
                url = f"https://{url}"

        if url.startswith("http"):
            processed_urls.append(url)

    return processed_urls


def is_valid_personal_website(url: str) -> bool:
    """Check if URL appears to be a personal website worth crawling."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        # Skip common non-personal sites
        skip_domains = {
            "github.com",
            "gitlab.com",
            "bitbucket.org",
            "linkedin.com",
            "twitter.com",
            "x.com",
            "facebook.com",
            "instagram.com",
            "youtube.com",
            "tiktok.com",
            "stackoverflow.com",
            "stackexchange.com",
            "medium.com",
            "dev.to",
            "hashnode.com",
            "discord.gg",
            "discord.com",
            "slack.com",
            "google.com",
            "amazon.com",
            "microsoft.com",
            "apple.com",
            "npmjs.com",
            "pypi.org",
        }

        # Check if domain is in skip list
        for skip_domain in skip_domains:
            if domain == skip_domain or domain.endswith(f".{skip_domain}"):
                return False

        # Accept common personal website patterns
        personal_patterns = [
            r"^[a-zA-Z0-9.-]+\.github\.io$",  # GitHub Pages
            r"^[a-zA-Z0-9.-]+\.netlify\.app$",  # Netlify
            r"^[a-zA-Z0-9.-]+\.vercel\.app$",  # Vercel
            r"^[a-zA-Z0-9.-]+\.herokuapp\.com$",  # Heroku
            r"^[a-zA-Z0-9.-]+\.(com|org|net|io|dev|me|personal)$",  # Personal domains
        ]

        import re

        for pattern in personal_patterns:
            if re.match(pattern, domain):
                return True

        # If it's not a known skip domain and has a reasonable TLD, consider it personal
        common_tlds = [
            ".com",
            ".org",
            ".net",
            ".io",
            ".dev",
            ".me",
            ".personal",
            ".tech",
            ".co",
        ]
        return any(domain.endswith(tld) for tld in common_tlds)

    except Exception:
        return False


def crawl_website_with_firecrawl(
    url: str, verbose: bool = False, firecrawl_scrape_func=None
) -> Optional[Dict[str, Any]]:
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
                print(f"❌ Firecrawl not available, cannot scrape {url}")
            return None

        if verbose:
            print(f"🕷️  Crawling website: {url}")

        # Configure scraping options for personal websites
        # First extract general information with broader scope
        scrape_result = firecrawl_scrape_func(
            url=url,
            formats=["markdown", "extract"],
            onlyMainContent=True,
            waitFor=5000,  # Wait for dynamic content (increased for MUI components)
            extract={
                "prompt": "Extract comprehensive personal and professional information including: name, title/role, ALL skills (both technical and soft), experience, education, projects, services, contact information, about/bio sections, and any other relevant career or personal details. Include both technical skills (programming languages, frameworks, tools) and soft skills (methodologies, practices, competencies). Look specifically for 'Tech Stack', 'Technology Stack', 'Technologies Used', 'Built With', or similar sections that list technologies. IMPORTANT: Only extract information that is actually present on the website. Do not generate placeholder content, make assumptions, or hallucinate any information. If a field cannot be found, leave it empty rather than creating fictional content.",
                "schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Person's full name"},
                        "title": {
                            "type": "string",
                            "description": "Professional title or role",
                        },
                        "bio": {
                            "type": "string",
                            "description": "About/bio section content",
                        },
                        "skills": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "ALL skills including technical skills (CSS, JavaScript, React, etc.), soft skills, methodologies, and practices found on the website",
                        },
                        "technologies": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Technical technologies, programming languages, frameworks, tools, libraries, and platforms. Look for 'Tech Stack', 'Technology Stack', 'Technologies Used', 'Built With' sections",
                        },
                        "tech_stack": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Technologies specifically mentioned in 'Tech Stack', 'Technology Stack', 'Technologies Used', 'Built With', 'Stack', or similar sections",
                        },
                        "experience": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Work experience, roles, and professional history",
                        },
                        "education": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Educational background",
                        },
                        "projects": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Notable projects or work",
                        },
                        "services": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Services offered or areas of expertise",
                        },
                        "clients": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Past clients or companies worked with",
                        },
                        "contact": {
                            "type": "object",
                            "description": "Contact information",
                        },
                        "social": {
                            "type": "object",
                            "description": "Social media links",
                        },
                        "achievements": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Awards, certifications, or notable achievements",
                        },
                    },
                },
            },
        )

        # Then do a second pass specifically for technologies and skills with a more targeted approach
        if scrape_result:
            tech_result = firecrawl_scrape_func(
                url=url,
                formats=["extract"],
                onlyMainContent=True,
                waitFor=5000,
                extract={
                    "prompt": "Extract ALL technologies, programming languages, frameworks, tools, libraries, platforms, and technical skills mentioned anywhere on this website. Look specifically for 'Tech Stack', 'Technology Stack', 'Technologies Used', 'Built With', 'Stack', 'Tools & Technologies', or similar sections. Also extract any soft skills, methodologies, or professional competencies. Be comprehensive and include everything, especially from technology listing sections. IMPORTANT: Only extract technologies and skills that are explicitly mentioned on the website. Do not generate placeholder content, make assumptions, or hallucinate any technologies. If no technologies are found in a section, leave it empty rather than creating fictional entries.",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "all_technologies": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "ALL technologies, programming languages, frameworks, tools, libraries, and platforms found anywhere on the website",
                            },
                            "tech_stack_items": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Technologies specifically found in 'Tech Stack', 'Technology Stack', 'Technologies Used', 'Built With', 'Stack', or similar dedicated technology sections",
                            },
                            "all_skills": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "ALL skills including technical skills, soft skills, methodologies, and competencies found on the website",
                            }
                        },
                    },
                },
            )

            # Third pass specifically for client companies
            client_result = firecrawl_scrape_func(
                url=url,
                formats=["extract"],
                onlyMainContent=True,
                waitFor=5000,
                extract={
                    "prompt": "Look specifically for a 'Clients' section, portfolio section, or any area showing past work relationships on this website. Extract all company names, brand names, organization names, or client names mentioned. Look for company logos, client showcases, or any business relationships. Include names from image titles, alt text, or any visible company/brand identifiers. IMPORTANT: Only extract client/company names that are explicitly mentioned or shown on the website. Do not generate placeholder content, make assumptions, or hallucinate any company names. If no clients or companies are found, leave the list empty rather than creating fictional entries.",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "client_companies": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Names of client companies, organizations, brands, or business relationships found on the website",
                            }
                        },
                    },
                },
            )

            # Merge the technology, skills, and client data into the main result
            if "extract" in scrape_result:
                # Merge technologies from tech_result
                if tech_result and "extract" in tech_result:
                    tech_data = tech_result["extract"]
                    existing_technologies = scrape_result["extract"].get("technologies", [])
                    new_technologies = tech_data.get("all_technologies", [])
                    tech_stack_items = tech_data.get("tech_stack_items", [])
                    
                    # Also get tech_stack from main extraction
                    main_tech_stack = scrape_result["extract"].get("tech_stack", [])
                    
                    # Combine all technology sources
                    all_technologies = list(set(existing_technologies + new_technologies + tech_stack_items + main_tech_stack))
                    scrape_result["extract"]["technologies"] = all_technologies
                    
                    # Store tech stack items separately for reference
                    scrape_result["extract"]["tech_stack"] = list(set(tech_stack_items + main_tech_stack))
                    
                    # Merge skills
                    existing_skills = scrape_result["extract"].get("skills", [])
                    new_skills = tech_data.get("all_skills", [])
                    all_skills = list(set(existing_skills + new_skills))
                    scrape_result["extract"]["skills"] = all_skills
                
                # Merge clients from client_result
                if client_result and "extract" in client_result:
                    client_data = client_result["extract"]
                    existing_clients = scrape_result["extract"].get("clients", [])
                    new_clients = client_data.get("client_companies", [])
                    all_clients = list(set(existing_clients + new_clients))
                    scrape_result["extract"]["clients"] = all_clients

        if scrape_result and "data" in scrape_result:
            return process_scraped_data(scrape_result["data"], url, verbose)
        elif scrape_result:
            return process_scraped_data(scrape_result, url, verbose)

    except Exception as e:
        if verbose:
            print(f"❌ Error crawling {url}: {str(e)}")
        return None

    return None


def process_scraped_data(
    scraped_data: Dict[str, Any], url: str, verbose: bool = False
) -> Dict[str, Any]:
    """Process and normalize scraped website data."""
    processed: Dict[str, Any] = {
        "url": url,
        "scraped_at": datetime.now().isoformat(),
        "content": {
            "raw_markdown": scraped_data.get("markdown", ""),
            "extracted_data": scraped_data.get("extract", {}),
        },
        "insights": {},
    }

    # Extract structured information
    extracted = scraped_data.get("extract", {})

    if extracted:
        processed["insights"] = {
            "personal_info": {
                "name": extracted.get("name", ""),
                "title": extracted.get("title", ""),
                "bio": extracted.get("bio", ""),
                "contact": extracted.get("contact", {}),
                "social": extracted.get("social", {}),
            },
            "professional": {
                "skills": extracted.get("skills", []),
                "technologies": extracted.get("technologies", []),
                "experience": extracted.get("experience", []),
                "education": extracted.get("education", []),
                "projects": extracted.get("projects", []),
                "services": extracted.get("services", []),
                "clients": extracted.get("clients", []),
                "achievements": extracted.get("achievements", []),
            },
        }

    # Analyze content for additional insights
    markdown_content = scraped_data.get("markdown", "").lower()

    # Ensure insights is properly initialized as a mutable dict
    if "insights" not in processed:
        processed["insights"] = {}

    insights_dict: Dict[str, Any] = processed["insights"]

    # Detect website type
    if any(
        keyword in markdown_content
        for keyword in ["portfolio", "resume", "cv", "about me"]
    ):
        insights_dict["website_type"] = "personal_portfolio"
    elif any(keyword in markdown_content for keyword in ["blog", "articles", "posts"]):
        insights_dict["website_type"] = "blog"
    elif any(
        keyword in markdown_content
        for keyword in ["freelance", "services", "hire", "consulting"]
    ):
        insights_dict["website_type"] = "professional_services"
    else:
        insights_dict["website_type"] = "general"

    # Extract key technologies mentioned in markdown content as backup
    tech_keywords = [
        "python",
        "javascript",
        "typescript",
        "react",
        "vue",
        "angular",
        "node",
        "java",
        "kotlin",
        "swift",
        "golang",
        "rust",
        "c++",
        "c#",
        "docker",
        "kubernetes",
        "aws",
        "azure",
        "gcp",
        "terraform",
        "mongodb",
        "postgresql",
        "mysql",
        "redis",
        "machine learning",
        "ai",
        "data science",
        "blockchain",
        "css",
        "html",
        "scss",
        "sass",
        "bootstrap",
        "material",
        "figma",
        "sketch",
        "photoshop",
        "git",
        "github",
        "firebase",
        "ionic",
        "stencil",
        "jquery",
        "ajax",
        "json",
        "sql",
        "mongodb",
        "jest",
        "storybook",
        "webpack",
        "npm",
        "yarn",
        "babel",
        "eslint",
        "next.js",
        "nextjs",
        "express",
        "expressjs",
        "tailwind",
        "tailwindcss",
        "postgress",
        "postgresql",
        "websockets",
        "socket.io",
        "socketio",
        "jupiter",
        "solana",
        "graphql",
        "apollo",
        "redux",
        "mobx",
        "gatsby",
        "nuxt",
        "svelte",
        "laravel",
        "django",
        "flask",
        "spring",
        "dotnet",
        ".net",
        "unity",
        "unreal",
        "tensorflow",
        "pytorch",
        "keras",
        "pandas",
        "numpy",
        "material ui",
        "ant design",
        "chakra ui",
        "styled components",
        "emotion",
    ]

    found_technologies = [tech for tech in tech_keywords if tech in markdown_content]
    
    # Look for tech stack patterns in markdown content
    tech_stack_patterns = [
        "tech stack:",
        "technology stack:",
        "technologies used:",
        "built with:",
        "stack:",
        "tools & technologies:",
        "tools and technologies:",
        "technologies:",
        "framework:",
        "frameworks:",
        "programming languages:",
        "languages:",
    ]
    
    tech_stack_technologies = []
    for pattern in tech_stack_patterns:
        if pattern in markdown_content:
            # Find the line with the pattern and extract technologies from it
            lines = markdown_content.split('\n')
            for i, line in enumerate(lines):
                if pattern in line.lower():
                    # Check current line and next few lines for technologies
                    tech_line = line.lower()
                    for j in range(i+1, min(i+3, len(lines))):
                        tech_line += " " + lines[j].lower()
                    
                    # Extract technologies from this section
                    for tech in tech_keywords:
                        if tech in tech_line and tech not in tech_stack_technologies:
                            tech_stack_technologies.append(tech)
                    break
    
    # Combine all found technologies
    all_found_technologies = list(set(found_technologies + tech_stack_technologies))
    
    if all_found_technologies:
        insights_dict["technologies_mentioned"] = all_found_technologies

    # Mark as having professional content if we found substantial data
    professional_data = processed.get("insights", {}).get("professional", {})
    has_content = any([
        professional_data.get("skills"),
        professional_data.get("technologies"),
        professional_data.get("experience"),
        professional_data.get("projects"),
        professional_data.get("services"),
        professional_data.get("clients"),
        found_technologies
    ])
    insights_dict["has_professional_content"] = has_content

    if verbose:
        print(f"✅ Processed website data from {url}")
        if extracted.get("name"):
            print(f"   Found: {extracted['name']}")
        if extracted.get("title"):
            print(f"   Title: {extracted['title']}")
        if extracted.get("skills"):
            print(f"   Skills: {len(extracted['skills'])} items")
        if extracted.get("technologies"):
            print(f"   Technologies: {len(extracted['technologies'])} items")
        if extracted.get("tech_stack"):
            print(f"   Tech Stack: {len(extracted['tech_stack'])} items")
            if extracted['tech_stack']:
                print(f"   Tech Stack items: {', '.join(extracted['tech_stack'][:5])}")
        if extracted.get("clients"):
            print(f"   Clients: {len(extracted['clients'])} items")
        if tech_stack_technologies:
            print(f"   Tech Stack from content: {', '.join(tech_stack_technologies[:5])}")
        if found_technologies:
            print(f"   Additional technologies from content: {', '.join(found_technologies[:5])}")

    return processed


async def enrich_profile_with_websites(
    profile_data: Dict[str, Any], use_cache: bool = True, verbose: bool = False
) -> Dict[str, Any]:
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
        "enrichment_summary": {},
    }

    # Process each URL
    for url in urls[:1]:  # Only process the first (personal) website
        cache_path = _get_website_cache_path(url)

        # Check cache first
        website_data = None
        if use_cache and _is_website_cache_valid(cache_path):
            if verbose:
                print(f"📦 Loading cached data for {url}")
            website_data = _load_website_cache(cache_path)

        # Crawl if not cached
        if not website_data:
            if verbose:
                print(f"🕷️  Crawling {url}...")

                # Note: This is a synchronous call wrapped for the async context
            loop = asyncio.get_event_loop()
            website_data = await loop.run_in_executor(
                None, crawl_website_with_firecrawl, url, verbose, None
            )

            # Cache the result
            if website_data and use_cache:
                _save_website_cache(website_data, cache_path)

        if website_data:
            enriched_profile["website_enrichment"]["crawled_websites"].append(
                website_data
            )

    # Generate enrichment summary
    if enriched_profile["website_enrichment"]["crawled_websites"]:
        enriched_profile["website_enrichment"]["enrichment_summary"] = (
            generate_enrichment_summary(
                enriched_profile["website_enrichment"]["crawled_websites"]
            )
        )

    return enriched_profile


def generate_enrichment_summary(
    website_data_list: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Generate a summary of insights from all crawled websites."""
    summary: Dict[str, Any] = {
        "websites_crawled": len(website_data_list),
        "combined_insights": {
            "additional_skills": set(),
            "additional_technologies": set(),
            "additional_experience": [],
            "additional_projects": [],
            "professional_services": [],
            "clients": [],
            "website_types": [],
            "technologies_mentioned": set(),
            "contact_info": {},
            "bio_snippets": [],
        },
    }

    for website_data in website_data_list:
        insights: Dict[str, Any] = website_data.get("insights", {})

        # Collect website types
        website_type = insights.get("website_type")
        if website_type:
            summary["combined_insights"]["website_types"].append(website_type)

        # Collect technologies
        technologies_mentioned = insights.get("technologies_mentioned")
        if technologies_mentioned:
            summary["combined_insights"]["technologies_mentioned"].update(
                technologies_mentioned
            )

        # Collect professional information
        professional: Dict[str, Any] = insights.get("professional", {})

        skills = professional.get("skills")
        if skills:
            summary["combined_insights"]["additional_skills"].update(skills)

        technologies = professional.get("technologies")
        if technologies:
            summary["combined_insights"]["additional_technologies"].update(technologies)

        experience = professional.get("experience")
        if experience:
            summary["combined_insights"]["additional_experience"].extend(experience)

        projects = professional.get("projects")
        if projects:
            summary["combined_insights"]["additional_projects"].extend(projects)

        services = professional.get("services")
        if services:
            summary["combined_insights"]["professional_services"].extend(services)

        clients = professional.get("clients")
        if clients:
            summary["combined_insights"]["clients"].extend(clients)

        # Collect personal information
        personal: Dict[str, Any] = insights.get("personal_info", {})

        bio = personal.get("bio")
        if bio:
            summary["combined_insights"]["bio_snippets"].append(bio)

        contact = personal.get("contact")
        if contact:
            summary["combined_insights"]["contact_info"].update(contact)

    # Convert sets back to lists for JSON serialization
    combined_insights: Dict[str, Any] = summary["combined_insights"]
    combined_insights["additional_skills"] = list(
        combined_insights["additional_skills"]
    )
    combined_insights["additional_technologies"] = list(
        combined_insights["additional_technologies"]
    )
    combined_insights["technologies_mentioned"] = list(
        combined_insights["technologies_mentioned"]
    )

    return summary


def sync_enrich_profile_with_websites(
    profile_data: Dict[str, Any],
    use_cache: bool = True,
    verbose: bool = False,
    firecrawl_scrape_func=None,
) -> Dict[str, Any]:
    """Synchronous wrapper for profile enrichment."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(
            enrich_profile_with_websites_sync(
                profile_data, use_cache, verbose, firecrawl_scrape_func
            )
        )
    finally:
        loop.close()


async def enrich_profile_with_websites_sync(
    profile_data: Dict[str, Any],
    use_cache: bool = True,
    verbose: bool = False,
    firecrawl_scrape_func=None,
) -> Dict[str, Any]:
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
        "enrichment_summary": {},
    }

    # Process each URL
    for url in urls[:1]:  # Only process the first (personal) website
        cache_path = _get_website_cache_path(url)

        # Check cache first
        website_data = None
        if use_cache and _is_website_cache_valid(cache_path):
            if verbose:
                print(f"📦 Loading cached data for {url}")
            website_data = _load_website_cache(cache_path)

        # Crawl if not cached
        if not website_data:
            if verbose:
                print(f"🕷️  Crawling {url}...")

            # Note: This is a synchronous call wrapped for the async context
            loop = asyncio.get_event_loop()
            website_data = await loop.run_in_executor(
                None, crawl_website_with_firecrawl, url, verbose, firecrawl_scrape_func
            )

            # Cache the result
            if website_data and use_cache:
                _save_website_cache(website_data, cache_path)

        if website_data:
            enriched_profile["website_enrichment"]["crawled_websites"].append(
                website_data
            )

    # Generate enrichment summary
    if enriched_profile["website_enrichment"]["crawled_websites"]:
        enriched_profile["website_enrichment"]["enrichment_summary"] = (
            generate_enrichment_summary(
                enriched_profile["website_enrichment"]["crawled_websites"]
            )
        )

    return enriched_profile
