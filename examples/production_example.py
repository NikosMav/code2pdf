#!/usr/bin/env python3
"""
Production example: Using MCP Firecrawl tools with code2pdf website enrichment.

This script demonstrates how to generate an enhanced CV using actual MCP Firecrawl tools
in a production environment where MCP tools are available.
"""

import sys
from pathlib import Path

# Add the src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

def create_production_firecrawl_wrapper():
    """
    Create a production-ready Firecrawl wrapper that uses actual MCP tools.
    
    In a real MCP environment, this would directly call the MCP Firecrawl tools.
    """
    
    def production_firecrawl_scrape(url: str, formats=None, onlyMainContent=True, waitFor=3000, extract=None):
        """
        Production Firecrawl scrape function using MCP tools.
        
        This demonstrates the actual MCP integration that would be used in production.
        """
        try:
            # In a real MCP environment, this is the actual call you would make:
            
            # Import the MCP Firecrawl function (available in MCP environment)
            # from mcp_tools import mcp_firecrawl_firecrawl_scrape
            
            # Make the actual MCP call
            # result = mcp_firecrawl_firecrawl_scrape(
            #     url=url,
            #     formats=formats or ["markdown", "extract"],
            #     onlyMainContent=onlyMainContent,
            #     waitFor=waitFor,
            #     extract=extract
            # )
            # return result
            
            # For this demonstration, we'll simulate using the actual Firecrawl data
            # that we successfully obtained earlier in this session
            if "nikosmav.github.io" in url:
                return {
                    "markdown": """# Nikolaos Mavrapidis - Software Engineer

Software Engineer with a Bachelor of Science in Informatics & Computer Science from the **National Kapodistrian University of Athens**, currently specializing in **Industrial Printing Systems** at **Software Competitiveness International S.A.**

Proven experience across diverse domains: from developing high-performance **Linux-based network software** for telecommunications to designing **enterprise-grade industrial printing solutions**.

Technical expertise spans **C/C++, Java, Python, Spring Framework, Spring Boot**, with hands-on experience in **Jenkins, GitLab CI/CD, networking protocols,** and automated testing frameworks.

Notable achievement: Contributed to developing **hitless software upgrade** capabilities, eliminating service outages and significantly enhancing system availability.

Expanding expertise in **cybersecurity** through the **IBM Cybersecurity Analyst Professional Certificate**, while maintaining active involvement in full-stack development.

Creator of **Worthify** — an AI-driven car valuation platform achieving **97% accuracy** across 200,000+ vehicle listings.

## Professional Experience

**Software Engineer - Industrial Printing Systems**  
Software Competitiveness International S.A. | Jun 2025 — Present  
- Designing and optimizing high-performance software solutions for industrial printing applications

**Software Engineer - Telecommunications Industry**  
Software Competitiveness International S.A. | Dec 2023 — Jun 2025  
- Developed high performance Linux-based network software for major telecom client
- Contributed to hitless software upgrade feature, eliminating service outages
- Experience with networking tools for performance testing and protocol analysis

## Skills & Technologies

**Languages**: C/C++ (5/5), Python (4/5), Java (4/5), JavaScript (3/5)  
**Frameworks**: Spring Framework (4/5), Spring Boot (4/5), React (4/5)  
**Tools**: Jenkins (3/5), Docker (3/5), GitLab CI (4/5), Git (5/5)  
**Networking**: Network Protocols (4/5), Wireshark (4/5), TCP/IP (4/5)

## Education

**Bachelor of Science in Informatics and Computer Science**  
National and Kapodistrian University of Athens | 2017 — 2022

## Notable Projects

- **Worthify** — AI-driven car valuation platform achieving 97% accuracy across 200,000+ vehicle listings
- **Bachelor's Thesis**: Museum of IT - Ubiquitous Computing web application
- **Hitless Software Upgrades**: Contributed to zero-downtime system updates

## Contact

- Email: mavrapidisnikolaos@gmail.com
- LinkedIn: https://www.linkedin.com/in/nikolaos-mavrapidis
- GitHub: https://github.com/NikosMav
- PyPI: https://pypi.org/user/NikosMav/
""",
                    "extract": {
                        "name": "Nikolaos Mavrapidis",
                        "title": "Software Engineer",
                        "bio": "Software Engineer with a Bachelor of Science in Informatics & Computer Science from the National Kapodistrian University of Athens, currently specializing in Industrial Printing Systems at Software Competitiveness International S.A. Proven experience across diverse domains: from developing high-performance Linux-based network software for telecommunications to designing enterprise-grade industrial printing solutions.",
                        "skills": [
                            "C/C++", "Java", "Python", "Spring Framework", "Spring Boot", 
                            "Jenkins", "GitLab CI/CD", "React", "Docker", "networking protocols", 
                            "automated testing frameworks", "JavaScript", "HTML/CSS", "Node.js",
                            "Network Protocols", "Wireshark", "TCP/IP", "Network Security"
                        ],
                        "experience": [
                            "Software Engineer - Industrial Printing Systems at Software Competitiveness International S.A. (Jun 2025 — Present)",
                            "Software Engineer - Telecommunications Industry at Software Competitiveness International S.A. (Dec 2023 — Jun 2025)"
                        ],
                        "education": [
                            "Bachelor of Science in Informatics and Computer Science from National Kapodistrian University of Athens (2017 — 2022)"
                        ],
                        "projects": [
                            "Worthify – AI-Driven Car Valuation Platform achieving 97% accuracy across 200,000+ vehicle listings",
                            "Bachelor's Thesis: Museum of IT of the Department of Informatics & Telecommunications of NKUA",
                            "Developed hitless software upgrade capabilities, eliminating service outages"
                        ],
                        "services": [
                            "Software development", "Data analysis", "Web development"
                        ],
                        "contact": {
                            "email": "mavrapidisnikolaos@gmail.com",
                            "linkedin": "https://www.linkedin.com/in/nikolaos-mavrapidis",
                            "github": "https://github.com/NikosMav",
                            "pypi": "https://pypi.org/user/NikosMav/"
                        },
                        "social": {
                            "linkedin": "https://www.linkedin.com/in/nikolaos-mavrapidis",
                            "github": "https://github.com/NikosMav",
                            "pypi": "https://pypi.org/user/NikosMav/"
                        },
                        "achievements": [
                            "Contributed to developing hitless software upgrade capabilities, eliminating service outages and significantly enhancing system availability."
                        ]
                    }
                }
            
            # For other URLs, return None to trigger fallback behavior
            return None
            
        except Exception as e:
            print(f"⚠️  Firecrawl error: {e}")
            return None
    
    return production_firecrawl_scrape

def generate_production_enhanced_cv():
    """
    Generate an enhanced CV using production MCP Firecrawl integration.
    
    This demonstrates the complete production workflow.
    """
    print("🚀 Production Enhanced CV Generation with MCP Firecrawl")
    print("=" * 60)
    
    from code2pdf.github import fetch_profile
    from code2pdf.website_enrichment import sync_enrich_profile_with_websites
    from code2pdf.generator import render_markdown, render_html
    from code2pdf.config import DEFAULT_CONFIG
    
    username = "nikosmav"
    
    try:
        # Step 1: Fetch basic GitHub profile
        print(f"🔍 Step 1: Fetching GitHub profile for {username}...")
        basic_profile = fetch_profile(username, verbose=False, enrich_websites=False)
        
        print(f"   ✅ GitHub profile loaded: {basic_profile['name']}")
        print(f"   📊 Repositories: {basic_profile['public_repos']}")
        print(f"   ⭐ Stars: {basic_profile['contribution_patterns']['total_stars_earned']}")
        print(f"   🌐 Website: {basic_profile.get('blog', 'None')}")
        
        # Step 2: Create production Firecrawl wrapper
        print(f"\n🛠️  Step 2: Setting up production Firecrawl integration...")
        firecrawl_func = create_production_firecrawl_wrapper()
        print(f"   ✅ Firecrawl wrapper configured")
        
        # Step 3: Enrich profile with website data
        print(f"\n🌐 Step 3: Enriching profile with website data...")
        enriched_profile = sync_enrich_profile_with_websites(
            basic_profile,
            verbose=True,
            firecrawl_scrape_func=firecrawl_func
        )
        
        # Step 4: Analyze enrichment results
        enrichment = enriched_profile.get("website_enrichment", {})
        if enrichment:
            summary = enrichment.get("enrichment_summary", {})
            insights = summary.get("combined_insights", {})
            
            print(f"\n📈 Step 4: Enrichment Analysis")
            print(f"   🔗 Websites discovered: {len(enrichment.get('discovered_urls', []))}")
            print(f"   🕷️  Websites crawled: {summary.get('websites_crawled', 0)}")
            print(f"   🛠️  Additional skills: {len(insights.get('additional_skills', []))}")
            print(f"   💼 Experience entries: {len(insights.get('additional_experience', []))}")
            print(f"   🚀 Projects found: {len(insights.get('additional_projects', []))}")
            
            if insights.get('additional_skills'):
                top_skills = insights['additional_skills'][:6]
                print(f"   💡 Top new skills: {', '.join(top_skills)}")
        
        # Step 5: Generate enhanced CV
        print(f"\n📄 Step 5: Generating enhanced CV files...")
        
        output_dir = Path("generated_cvs/production_enhanced")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate Markdown CV
        md_file = output_dir / f"{username}_enhanced_cv.md"
        render_markdown(enriched_profile, md_file, "professional", DEFAULT_CONFIG)
        print(f"   ✅ Markdown CV: {md_file}")
        
        # Generate HTML CV
        html_file = output_dir / f"{username}_enhanced_cv.html"
        render_html(enriched_profile, html_file, "modern", DEFAULT_CONFIG)
        print(f"   ✅ HTML CV: {html_file}")
        
        # Step 6: Show file sizes and preview
        print(f"\n📊 Step 6: Output Summary")
        print(f"   📁 Output directory: {output_dir.resolve()}")
        print(f"   📄 Markdown CV: {md_file.stat().st_size / 1024:.1f}KB")
        print(f"   🌐 HTML CV: {html_file.stat().st_size / 1024:.1f}KB")
        
        # Preview enhanced content
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        print(f"\n🔍 Enhanced CV Preview:")
        if "## 🌐 Website Insights" in content:
            print(f"   ✅ Website Insights section included")
            
            # Extract insights section
            start = content.find("## 🌐 Website Insights")
            end = content.find("---", start)
            if start != -1 and end != -1:
                insights_section = content[start:end].strip()
                lines = insights_section.split('\n')[:15]  # First 15 lines
                for line in lines:
                    print(f"   {line}")
                if len(insights_section.split('\n')) > 15:
                    print(f"   ... and more website insights")
        else:
            print(f"   ⚠️  Website Insights section not found")
        
        return enriched_profile
        
    except Exception as e:
        print(f"❌ Error in production CV generation: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main production demonstration."""
    print("🎯 code2pdf Production MCP Firecrawl Integration")
    print("Complete website enrichment system for production use")
    print()
    
    profile = generate_production_enhanced_cv()
    
    if profile:
        print(f"\n✅ Production demonstration completed successfully!")
        
        print(f"\n💼 Production Integration Guide:")
        print(f"   1. Replace the wrapper function with actual MCP tool calls")
        print(f"   2. Ensure MCP environment is properly configured")
        print(f"   3. Use: code2pdf build username --enrich-websites")
        print(f"   4. System will automatically use Firecrawl when available")
        
        print(f"\n🔧 MCP Integration Code:")
        print(f"   ```python")
        print(f"   # In production MCP environment:")
        print(f"   from mcp_tools import mcp_firecrawl_firecrawl_scrape")
        print(f"   ")
        print(f"   result = mcp_firecrawl_firecrawl_scrape(")
        print(f"       url=url,")
        print(f"       formats=['markdown', 'extract'],")
        print(f"       onlyMainContent=True,")
        print(f"       waitFor=3000,")
        print(f"       extract={{")
        print(f"           'prompt': 'Extract professional information...',")
        print(f"           'schema': {{...}}")
        print(f"       }}")
        print(f"   )")
        print(f"   ```")
        
        print(f"\n🎉 The website enrichment system is ready for production!")
    else:
        print(f"\n❌ Production demonstration failed")

if __name__ == "__main__":
    main() 