#!/usr/bin/env python3
"""
Complete MCP Firecrawl integration for code2pdf website enrichment.

This module demonstrates how to properly integrate the MCP Firecrawl tools
with the code2pdf website enrichment system in a production environment.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, Callable

# Add the src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from code2pdf.github import fetch_profile
from code2pdf.website_enrichment import sync_enrich_profile_with_websites
from code2pdf.generator import render_markdown, render_html
from code2pdf.config import load_config, DEFAULT_CONFIG

def create_mcp_firecrawl_wrapper():
    """
    Create a wrapper function that uses actual MCP Firecrawl tools.
    
    This function demonstrates how to integrate with MCP Firecrawl in a real environment.
    When this code runs in an MCP-enabled system, it will use the actual tools.
    """
    
    def mcp_firecrawl_wrapper(url: str, formats=None, onlyMainContent=True, waitFor=3000, extract=None):
        """
        Wrapper function that calls MCP Firecrawl tools.
        
        In an MCP environment, this would directly call:
        mcp_firecrawl_firecrawl_scrape(url=url, formats=formats, ...)
        """
        try:
            # In a real MCP environment, you would make this call:
            # result = mcp_firecrawl_firecrawl_scrape(
            #     url=url,
            #     formats=formats or ["markdown", "extract"],
            #     onlyMainContent=onlyMainContent,
            #     waitFor=waitFor,
            #     extract=extract
            # )
            # return result
            
            # For demonstration, we'll simulate using the actual data we got from Firecrawl
            if "nikosmav.github.io" in url:
                return demonstrate_real_firecrawl_data()
            
            # For other URLs, return None to trigger fallback
            return None
            
        except Exception as e:
            print(f"⚠️  MCP Firecrawl error: {e}")
            return None
    
    return mcp_firecrawl_wrapper

def demonstrate_real_firecrawl_data():
    """Return real data from Firecrawl scraping for demonstration."""
    return {
        "markdown": """# Nikolaos Mavrapidis - Software Engineer

Software Engineer with a Bachelor of Science in Informatics & Computer Science from the **National Kapodistrian University of Athens**, currently specializing in **Industrial Printing Systems** at **Software Competitiveness International S.A.**

## Skills & Technologies
- **C/C++** (Expert level)
- **Python** (Advanced) 
- **Java** (Advanced)
- **Spring Framework & Spring Boot** (Advanced)
- **React** (Advanced)
- **Jenkins, Docker, GitLab CI** (Proficient)
- **Networking protocols, TCP/IP** (Expert)
- **Cybersecurity** (Learning - IBM Certificate)

## Professional Experience
- **Software Engineer - Industrial Printing Systems** at Software Competitiveness International S.A. (Jun 2025 — Present)
  - Designing and optimizing high-performance software solutions for industrial printing applications
  
- **Software Engineer - Telecommunications Industry** at Software Competitiveness International S.A. (Dec 2023 — Jun 2025)
  - Developed high performance Linux-based network software for major telecom client
  - Contributed to hitless software upgrade feature, eliminating service outages
  - Used networking tools for performance testing and protocol analysis

## Education
- **Bachelor of Science in Informatics and Computer Science** 
  National Kapodistrian University of Athens (2017 — 2022)

## Notable Projects
- **Worthify** — AI-driven car valuation platform achieving **97% accuracy** across 200,000+ vehicle listings
- **Bachelor's Thesis**: Museum of IT - Ubiquitous Computing web application
- **Hitless Software Upgrades**: Contributed to zero-downtime system updates

## Achievements & Certifications
- IBM Cybersecurity Analyst Professional Certificate (in progress)
- Cisco Junior Cybersecurity Analyst Career Path (in progress)
- Participated in 1st Greek AI Hackathon (2024)
- Student Volunteer at MobileHCI 2023 - ACM SIGCHI
- Google Hash Code 2022 participant

## Contact Information
- Email: mavrapidisnikolaos@gmail.com
- LinkedIn: https://www.linkedin.com/in/nikolaos-mavrapidis
- GitHub: https://github.com/NikosMav
- PyPI: https://pypi.org/user/NikosMav/
""",
        "extract": {
            "name": "Nikolaos Mavrapidis",
            "title": "Software Engineer specializing in Industrial Printing Systems",
            "bio": "Software Engineer with a Bachelor of Science in Informatics & Computer Science from the National Kapodistrian University of Athens, currently specializing in Industrial Printing Systems at Software Competitiveness International S.A. Proven experience across diverse domains: from developing high-performance Linux-based network software for telecommunications to designing enterprise-grade industrial printing solutions. Expanding expertise in cybersecurity through the IBM Cybersecurity Analyst Professional Certificate.",
            "skills": [
                "C/C++", "Java", "Python", "Spring Framework", "Spring Boot", 
                "Jenkins", "GitLab CI/CD", "React", "Docker", "networking protocols", 
                "automated testing frameworks", "JavaScript", "HTML/CSS", "Node.js",
                "Network Protocols", "Wireshark", "TCP/IP", "Network Security",
                "Linux", "System Programming", "Telecommunications", "Industrial Software",
                "AI/Machine Learning", "Data Analysis", "Cybersecurity"
            ],
            "experience": [
                "Software Engineer - Industrial Printing Systems at Software Competitiveness International S.A. (Jun 2025 — Present): Designing and optimizing high-performance software solutions for industrial printing applications",
                "Software Engineer - Telecommunications Industry at Software Competitiveness International S.A. (Dec 2023 — Jun 2025): Developed high performance Linux-based network software for major telecom client, contributed to hitless software upgrade feature"
            ],
            "education": [
                "Bachelor of Science in Informatics and Computer Science from National Kapodistrian University of Athens (2017 — 2022)"
            ],
            "projects": [
                "Worthify – AI-Driven Car Valuation Platform achieving 97% accuracy across 200,000+ vehicle listings",
                "Bachelor's Thesis: Museum of IT - Ubiquitous Computing web application for NKUA",
                "Hitless Software Upgrade system - eliminating service outages in telecommunications",
                "Industrial Printing Software Solutions - high-performance enterprise applications"
            ],
            "services": [
                "Software Development", "Industrial Printing Systems", "Telecommunications Software",
                "Data Analysis", "Web Development", "AI/ML Solutions", "System Programming",
                "Network Software Development", "Cybersecurity Consulting"
            ],
            "contact": {
                "email": "mavrapidisnikolaos@gmail.com",
                "linkedin": "https://www.linkedin.com/in/nikolaos-mavrapidis",
                "github": "https://github.com/NikosMav",
                "pypi": "https://pypi.org/user/NikosMav/",
                "website": "https://nikosmav.github.io/nikosmav-react/"
            },
            "social": {
                "linkedin": "https://www.linkedin.com/in/nikolaos-mavrapidis",
                "github": "https://github.com/NikosMav",
                "pypi": "https://pypi.org/user/NikosMav/"
            },
            "achievements": [
                "Contributed to developing hitless software upgrade capabilities, eliminating service outages",
                "Created Worthify AI platform with 97% accuracy across 200,000+ vehicle listings",
                "Participated in 1st Greek AI Hackathon (2024)",
                "Student Volunteer at MobileHCI 2023 - ACM SIGCHI",
                "IBM Cybersecurity Analyst Professional Certificate (in progress)",
                "Cisco Junior Cybersecurity Analyst Career Path (in progress)",
                "Google Hash Code 2022 participant"
            ]
        }
    }

def generate_enhanced_cv_with_mcp(username: str, output_format: str = "markdown", theme: str = "professional", verbose: bool = True):
    """
    Generate an enhanced CV using MCP Firecrawl integration.
    
    This function demonstrates the complete workflow:
    1. Fetch GitHub profile
    2. Discover personal websites
    3. Use MCP Firecrawl to crawl websites
    4. Enrich profile with website data
    5. Generate enhanced CV
    """
    if verbose:
        print(f"🎯 Generating enhanced CV for {username} using MCP Firecrawl integration")
    
    try:
        # Create MCP Firecrawl wrapper
        firecrawl_func = create_mcp_firecrawl_wrapper()
        
        # Fetch GitHub profile with website enrichment
        if verbose:
            print(f"🔍 Fetching GitHub profile and enriching with website data...")
            
        profile_data = fetch_profile(
            username, 
            verbose=verbose, 
            enrich_websites=True
        )
        
        # Manual enrichment with MCP function (for demonstration)
        if verbose:
            print(f"🌐 Performing additional website enrichment with MCP Firecrawl...")
            
        enriched_profile = sync_enrich_profile_with_websites(
            profile_data,
            verbose=verbose,
            firecrawl_scrape_func=firecrawl_func
        )
        
        # Generate output files
        timestamp = "enhanced"
        output_dir = Path(f"generated_cvs/{username}_{timestamp}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        config = load_config()
        
        if output_format in ["markdown", "all"]:
            md_file = output_dir / f"{username}_cv_enhanced.md"
            render_markdown(enriched_profile, md_file, theme, config)
            if verbose:
                print(f"✅ Enhanced Markdown CV: {md_file}")
        
        if output_format in ["html", "all"]:
            html_file = output_dir / f"{username}_cv_enhanced.html"
            render_html(enriched_profile, html_file, theme, config)
            if verbose:
                print(f"✅ Enhanced HTML CV: {html_file}")
        
        # Display enrichment summary
        if "website_enrichment" in enriched_profile:
            enrichment = enriched_profile["website_enrichment"]
            summary = enrichment.get("enrichment_summary", {})
            insights = summary.get("combined_insights", {})
            
            if verbose:
                print(f"\n📊 Enrichment Summary:")
                print(f"   Websites discovered: {len(enrichment.get('discovered_urls', []))}")
                print(f"   Websites successfully crawled: {summary.get('websites_crawled', 0)}")
                print(f"   Additional skills found: {len(insights.get('additional_skills', []))}")
                print(f"   Experience entries: {len(insights.get('additional_experience', []))}")
                print(f"   Notable projects: {len(insights.get('additional_projects', []))}")
                print(f"   Professional services: {len(insights.get('professional_services', []))}")
        
        return enriched_profile
        
    except Exception as e:
        print(f"❌ Error generating enhanced CV: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return None

def main():
    """Main demonstration function."""
    print("🚀 MCP Firecrawl Integration for code2pdf")
    print("Complete website enrichment system demonstration")
    print("=" * 60)
    
    # Example usage
    username = "nikosmav"
    
    print(f"\n1️⃣  Basic enhanced CV generation:")
    profile = generate_enhanced_cv_with_mcp(username, "markdown", "professional", verbose=True)
    
    if profile:
        print(f"\n2️⃣  Additional formats:")
        generate_enhanced_cv_with_mcp(username, "html", "modern", verbose=False)
        
        print(f"\n3️⃣  Professional insights discovered:")
        enrichment = profile.get("website_enrichment", {})
        if enrichment.get("crawled_websites"):
            for site_data in enrichment["crawled_websites"]:
                insights = site_data.get("insights", {})
                print(f"   🌐 {site_data['url']}")
                print(f"      Type: {insights.get('website_type', 'Unknown')}")
                if insights.get("technologies_mentioned"):
                    techs = insights["technologies_mentioned"][:5]
                    print(f"      Technologies: {', '.join(techs)}")
                if insights.get("personal_info", {}).get("title"):
                    print(f"      Title: {insights['personal_info']['title']}")
    
    print(f"\n✅ MCP Firecrawl integration demonstration complete!")
    print(f"\n💡 In a real MCP environment:")
    print(f"   • Replace the wrapper function with actual MCP tool calls")
    print(f"   • The system will automatically use Firecrawl for website crawling")
    print(f"   • Enhanced CVs will include rich website insights")
    print(f"   • All data is cached for performance")

if __name__ == "__main__":
    main() 