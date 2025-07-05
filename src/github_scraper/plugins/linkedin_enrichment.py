"""LinkedIn enrichment plugin for extracting professional profile data."""

from __future__ import annotations
import json
import hashlib
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse


def _get_cache_path(linkedin_url: str) -> Path:
    """Generate cache file path for LinkedIn profile data."""
    from ..github import CACHE_DIR
    url_hash = hashlib.md5(linkedin_url.encode()).hexdigest()
    return CACHE_DIR / f"linkedin_{url_hash}.json"


def _is_cache_valid(cache_path: Path, max_age_hours: int = 24) -> bool:
    """Check if cache file is still valid (24h TTL for LinkedIn data)."""
    if not cache_path.exists():
        return False
    
    cache_age = datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)
    return cache_age < timedelta(hours=max_age_hours)


def discover_linkedin_urls(profile_data: Dict[str, Any]) -> List[str]:
    """
    Discover LinkedIn profile URLs from GitHub profile data.
    
    Args:
        profile_data: GitHub profile data dictionary
        
    Returns:
        List of discovered LinkedIn URLs
    """
    linkedin_urls = []
    
    # LinkedIn URL patterns to match
    linkedin_patterns = [
        r'https?://(?:www\.)?linkedin\.com/in/[a-zA-Z0-9\-]+/?',
        r'linkedin\.com/in/[a-zA-Z0-9\-]+/?',
        r'www\.linkedin\.com/in/[a-zA-Z0-9\-]+/?',
        r'in/[a-zA-Z0-9\-]+/?'  # Support partial URLs like "in/username"
    ]
    
    def extract_linkedin_from_text(text: str) -> List[str]:
        """Extract LinkedIn URLs from text using regex patterns."""
        if not text:
            return []
        
        urls = []
        for pattern in linkedin_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Normalize URL
                if match.startswith('in/'):
                    # Handle partial URLs like "in/username"
                    match = f"https://linkedin.com/{match}"
                elif not match.startswith('http'):
                    # Handle domain-based URLs like "linkedin.com/in/username"
                    match = f"https://{match}"
                # Remove trailing slash and normalize
                match = match.rstrip('/')
                if match not in urls:
                    urls.append(match)
        return urls
    
    # Check bio field
    if profile_data.get("bio"):
        linkedin_urls.extend(extract_linkedin_from_text(profile_data["bio"]))
    
    # Check blog field (sometimes people put LinkedIn there)
    if profile_data.get("blog"):
        linkedin_urls.extend(extract_linkedin_from_text(profile_data["blog"]))
    
    # Check repository descriptions
    for repo in profile_data.get("repos", []):
        if repo.get("description"):
            linkedin_urls.extend(extract_linkedin_from_text(repo["description"]))
    
    # Check README files (if we had them - for future enhancement)
    # This could be expanded to check README content of repositories
    
    # Remove duplicates while preserving order
    unique_urls = []
    for url in linkedin_urls:
        if url not in unique_urls and _is_valid_linkedin_url(url):
            unique_urls.append(url)
    
    return unique_urls


def _normalize_linkedin_url(url: str) -> Optional[str]:
    """Normalize LinkedIn URL to standard format."""
    if not url:
        return None
    
    url = url.strip()
    if not url:
        return None
    
    # Handle different input formats
    if url.startswith('in/'):
        # Partial URL like "in/username"
        return f"https://linkedin.com/{url}"
    elif url.startswith('linkedin.com/in/') or url.startswith('www.linkedin.com/in/'):
        # Domain URL like "linkedin.com/in/username"
        return f"https://{url}".rstrip('/')
    elif url.startswith('http'):
        # Already a full URL - validate it's a LinkedIn URL first
        if 'linkedin.com/in/' in url:
            return url.rstrip('/')
        else:
            return None  # Not a LinkedIn URL
    else:
        # Try to interpret as just username (must be valid format)
        if '/' not in url and len(url) > 0 and url.replace('-', '').replace('_', '').isalnum():
            return f"https://linkedin.com/in/{url}"
    
    return None


def _is_valid_linkedin_url(url: str) -> bool:
    """Validate that the URL is a proper LinkedIn profile URL."""
    try:
        parsed = urlparse(url)
        
        # Must be LinkedIn domain
        if parsed.netloc.lower() not in ['linkedin.com', 'www.linkedin.com']:
            return False
        
        # Must be a profile URL (/in/username)
        if not parsed.path.startswith('/in/'):
            return False
        
        # Extract username part
        username = parsed.path[4:].strip('/')
        
        # Username should be alphanumeric with hyphens, reasonable length
        if not re.match(r'^[a-zA-Z0-9\-]{1,100}$', username):
            return False
        
        return True
        
    except Exception:
        return False


def _parse_linkedin_from_raw_content(raw_content: str, verbose: bool = False) -> Optional[Dict[str, Any]]:
    """Parse LinkedIn profile data from raw markdown content as fallback."""
    if not raw_content or len(raw_content) < 50:
        return None
    
    parsed_data = {}
    content_lines = raw_content.split('\n')
    
    try:
        # Extract headline (often appears near the top, after name)
        headline_patterns = [
            r'(?i)^(.+?)(?:\s*\|\s*linkedin|$)',  # Line ending with | LinkedIn
            r'(?i)^([^#\[\]]+?)$',  # Simple text line (not heading or link)
        ]
        
        for i, line in enumerate(content_lines[:10]):  # Check first 10 lines
            line = line.strip()
            if len(line) > 10 and len(line) < 150:
                # Skip lines that are clearly not headlines
                if any(skip in line.lower() for skip in ['view profile', 'connect', 'message', 'follow', '©', 'linkedin']):
                    continue
                if line.startswith('#') or line.startswith('**') or line.startswith('['):
                    continue
                    
                # This might be a headline
                parsed_data["headline"] = line
                if verbose:
                    print(f"   📋 Found potential headline: {line}")
                break
        
        # Extract location (often follows patterns like "Location: City, Country")
        location_patterns = [
            r'(?i)location[:\s]+([^|\n\r]+)',
            r'(?i)based in[:\s]+([^|\n\r]+)',
            r'(?i)from[:\s]+([^|\n\r]+)',
        ]
        
        for line in content_lines:
            for pattern in location_patterns:
                match = re.search(pattern, line)
                if match:
                    location = match.group(1).strip()
                    if len(location) > 2 and len(location) < 100:
                        parsed_data["location"] = location
                        if verbose:
                            print(f"   📍 Found location: {location}")
                        break
        
        # Extract education institutions
        education_keywords = ['university', 'college', 'school', 'institute', 'academy']
        education_entries = []
        
        for line in content_lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in education_keywords):
                # Clean up the line
                cleaned = re.sub(r'[*#\[\]]+', '', line).strip()
                if len(cleaned) > 5 and len(cleaned) < 200:
                    education_entries.append({
                        "institution": cleaned,
                        "degree": "",
                        "field_of_study": "",
                        "years": "",
                        "description": ""
                    })
                    if verbose:
                        print(f"   🎓 Found education: {cleaned}")
        
        if education_entries:
            parsed_data["education"] = education_entries[:5]  # Limit to 5 entries
        
        # Extract experience/companies
        experience_keywords = ['company', 'corporation', 'inc', 'ltd', 'llc', 'at ', 'work', 'employed']
        experience_entries = []
        
        for line in content_lines:
            line_lower = line.lower()
            # Look for lines that might contain company information
            if any(keyword in line_lower for keyword in experience_keywords):
                cleaned = re.sub(r'[*#\[\]]+', '', line).strip()
                if len(cleaned) > 5 and len(cleaned) < 200:
                    experience_entries.append({
                        "title": "",
                        "company": cleaned,
                        "duration": "",
                        "location": "",
                        "description": ""
                    })
                    if verbose:
                        print(f"   💼 Found experience: {cleaned}")
        
        if experience_entries:
            parsed_data["experience"] = experience_entries[:5]  # Limit to 5 entries
        
        # Extract skills (look for common skill-related keywords)
        skills_keywords = ['python', 'javascript', 'java', 'react', 'node', 'aws', 'docker', 'kubernetes',
                          'sql', 'mongodb', 'postgresql', 'git', 'linux', 'windows', 'macos',
                          'machine learning', 'ai', 'data science', 'analytics', 'cloud', 'devops']
        
        skills = []
        content_lower = raw_content.lower()
        
        for skill in skills_keywords:
            if skill in content_lower and skill not in skills:
                skills.append(skill.title())
                if verbose:
                    print(f"   🔧 Found skill: {skill}")
        
        if skills:
            parsed_data["skills"] = skills[:10]  # Limit to 10 skills
        
        # Set default empty arrays for missing fields
        if "education" not in parsed_data:
            parsed_data["education"] = []
        if "certifications" not in parsed_data:
            parsed_data["certifications"] = []
        if "experience" not in parsed_data:
            parsed_data["experience"] = []
        if "skills" not in parsed_data:
            parsed_data["skills"] = []
        if "location" not in parsed_data:
            parsed_data["location"] = ""
        if "industry" not in parsed_data:
            parsed_data["industry"] = ""
        
        # Only return data if we found at least a headline or some meaningful content
        if parsed_data.get("headline") or len(parsed_data.get("education", [])) > 0 or len(parsed_data.get("skills", [])) > 0:
            return parsed_data
        
    except Exception as e:
        if verbose:
            print(f"   ❌ Error parsing content: {e}")
    
    return None


def _create_linkedin_extraction_schema() -> Dict[str, Any]:
    """Create extraction schema for LinkedIn data."""
    return {
        "type": "object",
        "properties": {
            "headline": {
                "type": "string",
                "description": "Professional headline/title from LinkedIn profile"
            },
            "education": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "institution": {"type": "string"},
                        "degree": {"type": "string"},
                        "field_of_study": {"type": "string"},
                        "years": {"type": "string"},
                        "description": {"type": "string"}
                    }
                },
                "description": "Educational background and degrees"
            },
            "certifications": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "issuing_organization": {"type": "string"},
                        "issue_date": {"type": "string"},
                        "expiration_date": {"type": "string"},
                        "credential_id": {"type": "string"},
                        "credential_url": {"type": "string"}
                    }
                },
                "description": "Professional certifications and credentials"
            },
            "experience": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "company": {"type": "string"},
                        "duration": {"type": "string"},
                        "location": {"type": "string"},
                        "description": {"type": "string"}
                    }
                },
                "description": "Professional work experience"
            },
            "skills": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Professional skills listed on LinkedIn"
            },
            "location": {
                "type": "string",
                "description": "Current location from LinkedIn profile"
            },
            "industry": {
                "type": "string", 
                "description": "Industry or professional field"
            }
        },
        "required": ["headline"]
    }


def _extract_linkedin_data_with_search(
    linkedin_url: str, verbose: bool = False
) -> Optional[Dict[str, Any]]:
    """Extract LinkedIn profile data using web search and alternative sources."""
    try:
        # Import MCP search tools
        try:
            from mcp_firecrawl_firecrawl_search import firecrawl_search
            if verbose:
                print("🔧 Using MCP Firecrawl search tools...")
        except ImportError:
            if verbose:
                print("⚠️  MCP search tools not available - falling back to direct scraping attempt")
            return _extract_linkedin_data_with_firecrawl_fallback(linkedin_url, verbose)
        
        if verbose:
            print(f"🔍 Searching for LinkedIn profile information: {linkedin_url}")
            print("🌐 Using web search to find publicly available LinkedIn data...")
        
        # Extract username from LinkedIn URL
        username = None
        try:
            from urllib.parse import urlparse
            parsed = urlparse(linkedin_url)
            if parsed.path.startswith('/in/'):
                username = parsed.path.split('/')[-1]
        except:
            pass
        
        if not username:
            if verbose:
                print("❌ Could not extract username from LinkedIn URL")
            return None
        
        # Search for publicly available information about this LinkedIn profile
        search_queries = [
            f'"{username}" LinkedIn profile',
            f'"{username}" LinkedIn professional',
            f'site:github.com "{username}" LinkedIn',
            f'"{username}" professional background',
            f'"{username}" developer engineer'
        ]
        
        if verbose:
            print(f"🔍 Searching for user: {username}")
        
        all_search_results = []
        
        for query in search_queries:
            if verbose:
                print(f"   🔎 Query: {query}")
            
            try:
                search_results = firecrawl_search(
                    query=query,
                    limit=5,
                    scrapeOptions={
                        "formats": ["markdown"],
                        "onlyMainContent": True
                    }
                )
                
                if search_results:
                    all_search_results.extend(search_results)
                    if verbose:
                        print(f"   ✅ Found {len(search_results)} results")
                else:
                    if verbose:
                        print(f"   ❌ No results found")
                        
            except Exception as e:
                if verbose:
                    print(f"   ❌ Search failed: {e}")
                continue
        
        if not all_search_results:
            if verbose:
                print("❌ No search results found for LinkedIn profile")
            return None
        
        # Combine and analyze all search results
        combined_content = ""
        for result in all_search_results:
            title = result.get('title', '')
            content = result.get('content', result.get('markdown', ''))
            if content:
                combined_content += f"\n\n--- {title} ---\n{content}"
        
        if verbose:
            print(f"📄 Combined search content: {len(combined_content)} characters")
            print(f"   📄 Sample content: {combined_content[:300]}...")
        
        # Parse the combined content for LinkedIn and professional information
        parsed_data = _parse_professional_data_from_search_content(combined_content, verbose)
        
        if parsed_data:
            # Add metadata
            processed_data = {
                "url": linkedin_url,
                "extracted_at": datetime.now().isoformat(),
                "profile_data": parsed_data,
                "raw_markdown": combined_content[:1000],
                "extraction_success": True,
                "method": "web_search",
                "search_results_count": len(all_search_results)
            }
            
            if verbose:
                print(f"✅ Successfully extracted professional data via web search!")
                print(f"   - Headline: {parsed_data.get('headline', 'N/A')}")
                print(f"   - Location: {parsed_data.get('location', 'N/A')}")
                print(f"   - Company: {parsed_data.get('company', 'N/A')}")
                print(f"   - Skills: {len(parsed_data.get('skills', []))}")
            
            return processed_data
        else:
            if verbose:
                print("❌ Could not extract meaningful professional data from search results")
            return None
            
    except Exception as e:
        if verbose:
            print(f"❌ Exception during web search: {e}")
        return None


def _parse_professional_data_from_search_content(content: str, verbose: bool = False) -> Optional[Dict[str, Any]]:
    """Parse professional data from search results content."""
    if not content or len(content) < 50:
        return None
    
    parsed_data = {}
    content_lines = content.split('\n')
    content_lower = content.lower()
    
    try:
        # Extract company information
        company_patterns = [
            r'(?:company|employer|works at|employed at):\s*([^|\n\r\.]+)',
            r'(?:^|\s)([A-Z][a-zA-Z\s&,]+(?:International|Inc|Corp|Corporation|LLC|Ltd|Company))',
            r'\*\*([A-Z][a-zA-Z\s&,]+(?:International|Inc|Corp|Corporation|LLC|Ltd))\*\*',
        ]
        
        for pattern in company_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                company = match.strip()
                if len(company) > 2 and len(company) < 100 and not any(skip in company.lower() for skip in ['github', 'linkedin', 'http', 'www']):
                    parsed_data["company"] = company
                    if verbose:
                        print(f"   🏢 Found company: {company}")
                    break
            if "company" in parsed_data:
                break
        
        # Extract location
        location_patterns = [
            r'(?:location|based in|from|lives in):\s*([^|\n\r\.]+)',
            r'📍\s*([^|\n\r\.]+)',
            r'(?:^|\s)([A-Z][a-zA-Z\s]+,\s*[A-Z][a-zA-Z\s]+)(?:\s|$)',  # City, Country format
        ]
        
        for pattern in location_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                location = match.strip()
                if len(location) > 3 and len(location) < 100:
                    parsed_data["location"] = location
                    if verbose:
                        print(f"   📍 Found location: {location}")
                    break
            if "location" in parsed_data:
                break
        
        # Extract professional title/headline
        title_patterns = [
            r'(?:title|role|position|job):\s*([^|\n\r\.]+)',
            r'_([A-Z][a-zA-Z\s]+(?:Developer|Engineer|Analyst|Manager|Director|Architect|Consultant|Specialist))_',
            r'(?:^|\s)((?:Senior|Lead|Principal|Staff)?\s*(?:Software|Full Stack|Backend|Frontend|Data|Machine Learning|AI|Cloud)?\s*(?:Developer|Engineer|Analyst|Architect|Consultant|Specialist))(?:\s|$)',
        ]
        
        for pattern in title_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                title = match.strip()
                if len(title) > 5 and len(title) < 100:
                    parsed_data["headline"] = title
                    if verbose:
                        print(f"   💼 Found title: {title}")
                    break
            if "headline" in parsed_data:
                break
        
        # If no specific title found, create one from context
        if "headline" not in parsed_data:
            if "github" in content_lower and "developer" in content_lower:
                years_match = re.search(r'(\d+(?:\.\d+)?)\s*years?', content_lower)
                if years_match:
                    years = years_match.group(1)
                    parsed_data["headline"] = f"Developer with {years} years of experience"
                else:
                    parsed_data["headline"] = "Software Developer"
                if verbose:
                    print(f"   💼 Inferred title: {parsed_data['headline']}")
        
        # Extract technical skills
        skills = []
        skill_keywords = [
            'python', 'javascript', 'java', 'react', 'node', 'html', 'css',
            'c++', 'c#', 'go', 'rust', 'typescript', 'angular', 'vue',
            'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'git',
            'sql', 'postgresql', 'mysql', 'mongodb', 'redis',
            'machine learning', 'ai', 'data science', 'analytics',
            'jupyter notebook', 'pandas', 'numpy', 'tensorflow',
            'spring', 'django', 'flask', 'express'
        ]
        
        for skill in skill_keywords:
            if skill.lower() in content_lower and skill.title() not in skills:
                skills.append(skill.title())
                if verbose:
                    print(f"   🔧 Found skill: {skill}")
        
        if skills:
            parsed_data["skills"] = skills[:15]  # Limit to 15 skills
        
        # Extract experience from GitHub data
        experience_entries = []
        if "github" in content_lower:
            # Look for repository information that might indicate experience
            repo_matches = re.findall(r'([A-Z][a-zA-Z0-9\-]+)(?:Public|Private)', content)
            if repo_matches:
                experience_entries.append({
                    "title": "Open Source Developer",
                    "company": "GitHub",
                    "duration": "Active contributor",
                    "location": "Remote",
                    "description": f"Maintains {len(repo_matches)} repositories including: {', '.join(repo_matches[:3])}"
                })
        
        if "company" in parsed_data:
            experience_entries.append({
                "title": parsed_data.get("headline", "Developer"),
                "company": parsed_data["company"],
                "duration": "Current",
                "location": parsed_data.get("location", ""),
                "description": ""
            })
        
        if experience_entries:
            parsed_data["experience"] = experience_entries
        
        # Set default empty arrays for missing fields
        if "education" not in parsed_data:
            parsed_data["education"] = []
        if "certifications" not in parsed_data:
            parsed_data["certifications"] = []
        if "experience" not in parsed_data:
            parsed_data["experience"] = []
        if "skills" not in parsed_data:
            parsed_data["skills"] = []
        if "location" not in parsed_data:
            parsed_data["location"] = ""
        if "industry" not in parsed_data:
            # Infer industry from skills
            if any(skill in skills for skill in ['Python', 'JavaScript', 'Java', 'React']):
                parsed_data["industry"] = "Software Development"
            else:
                parsed_data["industry"] = ""
        
        # Only return data if we found meaningful content
        if (parsed_data.get("headline") or 
            parsed_data.get("company") or 
            len(parsed_data.get("skills", [])) > 0 or
            len(parsed_data.get("experience", [])) > 0):
            return parsed_data
        
    except Exception as e:
        if verbose:
            print(f"   ❌ Error parsing content: {e}")
    
    return None


def _extract_linkedin_data_with_firecrawl_fallback(
    linkedin_url: str, verbose: bool = False
) -> Optional[Dict[str, Any]]:
    """Fallback method using direct Firecrawl scraping."""
    try:
        # Try using MCP Firecrawl tools first (more robust)
        try:
            from mcp_firecrawl_firecrawl_scrape import firecrawl_scrape
            use_mcp_tools = True
            if verbose:
                print("🔧 Using MCP Firecrawl tools for direct scraping...")
        except ImportError:
            # Fallback to local integration
            from ..mcp_integration import firecrawl_scrape_sync, is_mcp_available, firecrawl_scrape_with_details
            use_mcp_tools = False
            if verbose:
                print("🔧 Using local Firecrawl integration...")
        
        if not use_mcp_tools and not is_mcp_available():
            if verbose:
                print("⚠️  Firecrawl API not available - LinkedIn enrichment disabled")
                print("   💡 Set FIRECRAWL_API_KEY environment variable to enable")
            return None
        
        if verbose:
            print(f"🔗 Attempting direct extraction from {linkedin_url}...")
            print("⚠️  Note: LinkedIn has strong anti-scraping protection - this may fail")
        
        # Create extraction schema
        extraction_schema = _create_linkedin_extraction_schema()
        
        # Configure extraction prompt
        extraction_prompt = """
        Extract professional information from this LinkedIn profile page.
        Focus on:
        1. Professional headline/title
        2. Education (degrees, institutions, years)
        3. Certifications (name, issuing org, dates)
        4. Work experience (titles, companies, duration)
        5. Skills and endorsements
        6. Current location and industry
        
        Be precise and only extract information that is clearly visible.
        For education and certifications, extract all entries you can find.
        """
        
        # Try multiple scraping strategies for LinkedIn
        if use_mcp_tools:
            # Use MCP Firecrawl tools with advanced options
            scraping_strategies = [
                {
                    "name": "MCP Standard extraction",
                    "params": {
                        "url": linkedin_url,
                        "formats": ["markdown", "extract"],
                        "onlyMainContent": True,
                        "waitFor": 8000,
                        "extract": {
                            "schema": extraction_schema,
                            "prompt": extraction_prompt
                        },
                        "timeout": 60,
                        "mobile": False
                    }
                },
                {
                    "name": "MCP Mobile extraction",
                    "params": {
                        "url": linkedin_url,
                        "formats": ["markdown", "extract"], 
                        "onlyMainContent": False,
                        "waitFor": 10000,
                        "extract": {
                            "schema": extraction_schema,
                            "prompt": extraction_prompt
                        },
                        "timeout": 60,
                        "mobile": True
                    }
                },
                {
                    "name": "MCP Content-only",
                    "params": {
                        "url": linkedin_url,
                        "formats": ["markdown"],
                        "onlyMainContent": True,
                        "waitFor": 5000,
                        "timeout": 45
                    }
                }
            ]
        else:
            # Use local integration
            scraping_strategies = [
                {
                    "name": "Standard extraction",
                    "params": {
                        "formats": ["markdown", "extract"],
                        "onlyMainContent": True,
                        "waitFor": 8000,
                        "extract": {
                            "schema": extraction_schema,
                            "prompt": extraction_prompt
                        },
                        "timeout": 60,
                        "mobile": False
                    }
                },
                {
                    "name": "Mobile view extraction", 
                    "params": {
                        "formats": ["markdown", "extract"],
                        "onlyMainContent": False,
                        "waitFor": 10000,
                        "extract": {
                            "schema": extraction_schema,
                            "prompt": extraction_prompt
                        },
                        "timeout": 60,
                        "mobile": True
                    }
                },
                {
                    "name": "Content-only extraction",
                    "params": {
                        "formats": ["markdown"],
                        "onlyMainContent": True,
                        "waitFor": 5000,
                        "timeout": 45,
                        "mobile": False
                    }
                }
            ]
        
        result = None
        error_details = None
        
        for strategy in scraping_strategies:
            if verbose:
                print(f"   🔄 Trying {strategy['name']}...")
            
            if use_mcp_tools:
                try:
                    result = firecrawl_scrape(**strategy['params'])
                    error_details = None
                except Exception as e:
                    result = None
                    error_details = str(e)
            else:
                result, error_details = firecrawl_scrape_with_details(
                    url=linkedin_url,
                    **strategy['params']
                )
            
            if result:
                if verbose:
                    print(f"   ✅ {strategy['name']} succeeded!")
                break
            elif verbose:
                print(f"   ❌ {strategy['name']} failed: {error_details}")
        
        if not result and verbose:
            print(f"   🔄 All strategies failed, trying basic markdown extraction...")
            # Last resort: just try to get any content
            if use_mcp_tools:
                try:
                    result = firecrawl_scrape(
                        url=linkedin_url,
                        formats=["markdown"],
                        onlyMainContent=False,
                        waitFor=3000,
                        timeout=30
                    )
                    error_details = None
                except Exception as e:
                    result = None
                    error_details = str(e)
            else:
                result, error_details = firecrawl_scrape_with_details(
                    url=linkedin_url,
                    formats=["markdown"],
                    onlyMainContent=False,
                    waitFor=3000,
                    timeout=30
                )
        
        if not result:
            if verbose:
                print(f"❌ Failed to extract data from {linkedin_url}")
                if error_details:
                    print(f"   🔍 Error details: {error_details}")
                print()
                print("🚫 LinkedIn Scraping Limitations:")
                print("   • LinkedIn actively blocks automated scraping")
                print("   • Profiles may require login to access content") 
                print("   • LinkedIn uses CAPTCHAs and rate limiting")
                print("   • Many profiles are set to private visibility")
                print()
                print("💡 Alternative approaches:")
                print("   1. Manually copy-paste LinkedIn data into a local file")
                print("   2. Use LinkedIn's official API (requires approval)")
                print("   3. Ask the user to provide LinkedIn data manually")
                print("   4. Focus on GitHub data enrichment instead")
            return None
        
        # Process and validate the extracted data
        extracted_data = result.get("extract", {})
        raw_content = result.get("markdown", "")
        
        if verbose:
            print(f"📄 Raw content length: {len(raw_content)} characters")
            if "linkedin" not in raw_content.lower() and len(raw_content) < 100:
                print("⚠️  Content appears to be blocked or redirected")
        
        # If structured extraction failed, try parsing from raw content
        if not extracted_data or not extracted_data.get("headline"):
            if verbose:
                print(f"⚠️  No structured data extracted, trying content parsing...")
            
            if raw_content:
                if verbose:
                    print(f"   📄 Raw content preview: {raw_content[:200]}...")
                
                # Check for common blocking patterns
                content_lower = raw_content.lower()
                if "sign in" in content_lower or "log in" in content_lower:
                    if verbose:
                        print("   🔒 Content appears to require authentication")
                elif "captcha" in content_lower:
                    if verbose:
                        print("   🤖 CAPTCHA challenge detected")
                elif "blocked" in content_lower:
                    if verbose:
                        print("   🚫 Access appears to be blocked")
                else:
                    # Try to parse data from raw content
                    parsed_data = _parse_linkedin_from_raw_content(raw_content, verbose)
                    if parsed_data:
                        extracted_data = parsed_data
                        if verbose:
                            print("   ✅ Successfully parsed data from raw content!")
                    elif verbose:
                        print("   ❌ Could not parse meaningful data from raw content")
            else:
                if verbose:
                    print("   📄 No content retrieved")
        
        # Final check - do we have any usable data?
        if not extracted_data or not extracted_data.get("headline"):
            return None
        
        # Add metadata
        processed_data = {
            "url": linkedin_url,
            "extracted_at": datetime.now().isoformat(),
            "profile_data": extracted_data,
            "raw_markdown": raw_content[:1000],  # Store first 1KB for debugging
            "extraction_success": True
        }
        
        if verbose:
            print(f"✅ Successfully extracted LinkedIn data!")
            print(f"   - Headline: {extracted_data.get('headline', 'N/A')}")
            print(f"   - Education entries: {len(extracted_data.get('education', []))}")
            print(f"   - Certifications: {len(extracted_data.get('certifications', []))}")
            print(f"   - Experience entries: {len(extracted_data.get('experience', []))}")
            print(f"   - Skills: {len(extracted_data.get('skills', []))}")
        
        return processed_data
        
    except Exception as e:
        if verbose:
            print(f"❌ Exception while extracting LinkedIn data: {e}")
            print("   🔧 This is likely due to LinkedIn's anti-scraping measures")
        return None


def _try_load_manual_linkedin_data(username: str) -> Optional[Dict[str, Any]]:
    """Try to load manually provided LinkedIn data from a local file."""
    try:
        from ..github import CACHE_DIR
        
        # Look for manual LinkedIn data files
        possible_files = [
            CACHE_DIR / f"linkedin_manual_{username}.json",
            CACHE_DIR / f"linkedin_{username}.json",
            Path(f"linkedin_{username}.json"),  # In current directory
            Path(f"{username}_linkedin.json"),
        ]
        
        for file_path in possible_files:
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Add metadata to indicate this is manual data
                    return {
                        "url": data.get("url", "manually_provided"),
                        "extracted_at": data.get("extracted_at", datetime.now().isoformat()),
                        "profile_data": data.get("profile_data", data),
                        "raw_markdown": "",
                        "extraction_success": True,
                        "manual_data": True,
                        "source_file": str(file_path)
                    }
    except Exception:
        pass
    
    return None


def create_manual_linkedin_template(username: str, save_to_cache: bool = True) -> str:
    """Create a template file for manual LinkedIn data entry."""
    try:
        from ..github import CACHE_DIR
        
        template = {
            "url": f"https://linkedin.com/in/{username}",
            "profile_data": {
                "headline": "Your professional headline here",
                "location": "Your location here",
                "industry": "Your industry here",
                "education": [
                    {
                        "institution": "University/School name",
                        "degree": "Degree type (e.g., Bachelor's, Master's)",
                        "field_of_study": "Field of study",
                        "years": "Years attended (e.g., 2018-2022)",
                        "description": "Optional description"
                    }
                ],
                "certifications": [
                    {
                        "name": "Certification name",
                        "issuing_organization": "Issuing organization",
                        "issue_date": "Issue date",
                        "expiration_date": "Expiration date (if any)",
                        "credential_id": "Credential ID (if any)",
                        "credential_url": "Credential URL (if any)"
                    }
                ],
                "experience": [
                    {
                        "title": "Job title",
                        "company": "Company name",
                        "duration": "Duration (e.g., Jan 2020 - Present)",
                        "location": "Job location",
                        "description": "Job description and achievements"
                    }
                ],
                "skills": ["Skill 1", "Skill 2", "Skill 3"]
            }
        }
        
        if save_to_cache:
            file_path = CACHE_DIR / f"linkedin_manual_{username}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(template, f, indent=2)
            return str(file_path)
        else:
            return json.dumps(template, indent=2)
            
    except Exception as e:
        return f"Error creating template: {e}"


def collect(
    profile_data: Dict[str, Any],
    use_cache: bool = True,
    verbose: bool = False,
    manual_linkedin_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Collect LinkedIn profile data for enrichment.
    
    Args:
        profile_data: GitHub profile data dictionary
        use_cache: Whether to use cached data
        verbose: Whether to print verbose output
        manual_linkedin_url: Manually provided LinkedIn URL (overrides auto-discovery)
        
    Returns:
        Dictionary containing LinkedIn profile data
    """
    # Use manual URL if provided, otherwise discover from GitHub profile
    if manual_linkedin_url:
        # Normalize the manual URL
        normalized_url = _normalize_linkedin_url(manual_linkedin_url)
        if normalized_url and _is_valid_linkedin_url(normalized_url):
            linkedin_urls = [normalized_url]
            if verbose:
                print(f"🔗 Using manually provided LinkedIn URL: {normalized_url}")
        else:
            if verbose:
                print(f"⚠️  Invalid manual LinkedIn URL provided: {manual_linkedin_url}")
            linkedin_urls = []
    else:
        # Discover LinkedIn URLs from GitHub profile
        linkedin_urls = discover_linkedin_urls(profile_data)
    
    if not linkedin_urls:
        if verbose:
            print("🔍 No LinkedIn profiles found in GitHub data")
        return {}
    
    if verbose:
        print(f"🔗 Found {len(linkedin_urls)} LinkedIn profile(s): {', '.join(linkedin_urls)}")
    
    linkedin_data = {
        "discovered_urls": linkedin_urls,
        "profiles": [],
        "enrichment_summary": {}
    }
    
    # Process the first LinkedIn URL (primary profile)
    for linkedin_url in linkedin_urls[:1]:  # Only process first URL to avoid rate limits
        cache_path = _get_cache_path(linkedin_url)
        profile_data_cached = None
        
        # Try to extract username from URL for manual data lookup
        username = None
        try:
            from urllib.parse import urlparse
            parsed = urlparse(linkedin_url)
            username = parsed.path.strip('/').split('/')[-1] if parsed.path.startswith('/in/') else None
        except:
            pass
        
        # 1. Check cache first
        if use_cache and _is_cache_valid(cache_path):
            if verbose:
                print(f"📦 Loading cached LinkedIn data for {linkedin_url}")
            try:
                with open(cache_path, "r", encoding="utf-8") as f:
                    profile_data_cached = json.load(f)
            except Exception:
                pass  # Fall through to fresh extraction
        
        # 2. Extract fresh data if not cached
        if not profile_data_cached:
            # Try web search first (more reliable for LinkedIn)
            profile_data_cached = _extract_linkedin_data_with_search(linkedin_url, verbose)
            
            # If search fails, try direct scraping as fallback
            if not profile_data_cached and verbose:
                print("🔄 Web search failed, trying direct scraping as fallback...")
                profile_data_cached = _extract_linkedin_data_with_firecrawl_fallback(linkedin_url, verbose)
            
            # Cache the result if successful
            if profile_data_cached and use_cache:
                try:
                    with open(cache_path, "w", encoding="utf-8") as f:
                        json.dump(profile_data_cached, f, indent=2)
                    if verbose:
                        print("💾 Cached LinkedIn data for future use")
                except Exception:
                    pass  # Ignore cache write errors
        
        if profile_data_cached:
            linkedin_data["profiles"].append(profile_data_cached)
    
    # Create enrichment summary
    if linkedin_data["profiles"]:
        primary_profile = linkedin_data["profiles"][0]["profile_data"]
        linkedin_data["enrichment_summary"] = {
            "headline": primary_profile.get("headline", ""),
            "location": primary_profile.get("location", ""),
            "industry": primary_profile.get("industry", ""),
            "education_count": len(primary_profile.get("education", [])),
            "certification_count": len(primary_profile.get("certifications", [])),
            "experience_count": len(primary_profile.get("experience", [])),
            "skills_count": len(primary_profile.get("skills", [])),
            "has_professional_data": bool(
                primary_profile.get("headline") or 
                primary_profile.get("education") or 
                primary_profile.get("certifications")
            )
        }
    
    return linkedin_data 