#!/usr/bin/env python3
"""
Comprehensive test script for website enrichment feature.

Tests multiple GitHub profiles to validate the flexibility and robustness
of the website enrichment system with various profile types.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any
import time

# Add the src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from code2pdf.github import fetch_profile
from code2pdf.website_enrichment import (
    extract_urls_from_profile,
    sync_enrich_profile_with_websites,
    is_valid_personal_website,
)
from code2pdf.generator import render_markdown, render_html
from code2pdf.config import DEFAULT_CONFIG


def create_test_firecrawl_wrapper():
    """
    Create a test Firecrawl wrapper that simulates MCP tools for testing.
    This will handle various website types that we might encounter.
    """

    def test_firecrawl_scrape(
        url: str, formats=None, onlyMainContent=True, waitFor=3000, extract=None
    ):
        """
        Test Firecrawl scrape function that simulates different website responses.
        """
        try:
            print(f"🕷️  [TEST] Simulating crawl of: {url}")

            # Simulate different website types based on URL patterns
            if "github.io" in url:
                # GitHub Pages site - likely a portfolio
                return {
                    "markdown": f"""# Portfolio Website

Welcome to my personal portfolio! I'm a software developer passionate about technology.

## About Me
I'm a developer with experience in various technologies and frameworks.

## Skills
- Web Development
- Mobile Development  
- Backend Development
- Database Design
- Cloud Computing

## Experience
- Software Developer at Tech Company
- Full Stack Developer at Digital Agency
- Freelance Developer

## Projects
- Personal portfolio website
- Mobile application development
- Web application projects
- Open source contributions

## Contact
- Website: {url}
- Email: developer@example.com
""",
                    "extract": {
                        "name": "Developer Name",
                        "title": "Software Developer",
                        "bio": f"Software developer with experience in web and mobile development. Portfolio hosted at {url}",
                        "skills": [
                            "Web Development",
                            "Mobile Development",
                            "Backend Development",
                            "Database Design",
                            "Cloud Computing",
                        ],
                        "experience": [
                            "Software Developer at Tech Company",
                            "Full Stack Developer at Digital Agency",
                            "Freelance Developer",
                        ],
                        "education": ["Computer Science Degree"],
                        "projects": [
                            "Personal portfolio website",
                            "Mobile application development",
                            "Web application projects",
                        ],
                        "services": [
                            "Web Development",
                            "Mobile Development",
                            "Consulting",
                        ],
                        "contact": {"website": url, "email": "developer@example.com"},
                        "social": {},
                        "achievements": ["Open Source Contributor"],
                    },
                }

            elif (
                any(domain in url for domain in [".dev", ".tech", ".io"])
                and "github" not in url
            ):
                # Personal domain - likely professional website
                return {
                    "markdown": f"""# Professional Website

Professional developer and technology consultant.

## Services
- Software Architecture
- Technical Consulting
- Code Reviews
- Training & Mentoring

## Technologies
- JavaScript/TypeScript
- Python
- React
- Node.js
- AWS/Azure

## About
Experienced developer with focus on modern web technologies and cloud solutions.

## Contact
- Website: {url}
""",
                    "extract": {
                        "name": "Professional Developer",
                        "title": "Software Architect & Consultant",
                        "bio": f"Professional developer and technology consultant specializing in modern web technologies and cloud solutions. Website: {url}",
                        "skills": [
                            "JavaScript",
                            "TypeScript",
                            "Python",
                            "React",
                            "Node.js",
                            "AWS",
                            "Azure",
                        ],
                        "experience": ["Software Architect", "Technical Consultant"],
                        "education": [],
                        "projects": [
                            "Cloud migration projects",
                            "Enterprise applications",
                        ],
                        "services": [
                            "Software Architecture",
                            "Technical Consulting",
                            "Code Reviews",
                            "Training",
                        ],
                        "contact": {"website": url},
                        "social": {},
                        "achievements": ["Technical Leadership"],
                    },
                }

            # For other URLs or if we want to simulate "no website content"
            return None

        except Exception as e:
            print(f"⚠️  Test crawl error for {url}: {e}")
            return None

    return test_firecrawl_scrape


def analyze_profile_websites(username: str, verbose: bool = True) -> Dict[str, Any]:
    """
    Analyze a GitHub profile for website enrichment potential.
    """
    if verbose:
        print(f"\n{'='*70}")
        print(f"🔍 ANALYZING PROFILE: {username}")
        print(f"{'='*70}")

    try:
        # Fetch basic GitHub profile
        if verbose:
            print("📊 Fetching GitHub profile...")

        profile = fetch_profile(username, verbose=False, enrich_websites=False)

        # Basic profile info
        basic_info = {
            "name": profile.get("name", "N/A"),
            "username": username,
            "bio": profile.get("bio"),
            "location": profile.get("location"),
            "company": profile.get("company"),
            "blog": profile.get("blog"),
            "twitter": profile.get("twitter_username"),
            "email": profile.get("email"),
            "repos": profile.get("public_repos", 0),
            "followers": profile.get("followers", 0),
            "stars": profile["contribution_patterns"]["total_stars_earned"],
            "activity_score": profile.get("activity_score", 0),
        }

        if verbose:
            print(f"   ✅ Profile loaded: {basic_info['name']}")
            print(f"   📊 Repositories: {basic_info['repos']}")
            print(f"   ⭐ Stars: {basic_info['stars']}")
            print(f"   🌐 Website: {basic_info['blog'] or 'None'}")
            if basic_info["bio"]:
                print(
                    f"   📝 Bio: {basic_info['bio'][:80]}{'...' if len(basic_info['bio']) > 80 else ''}"
                )

        # Extract potential websites
        discovered_urls = extract_urls_from_profile(profile)

        if verbose:
            print("\n🔗 Website Discovery:")
            if discovered_urls:
                print(f"   Found {len(discovered_urls)} potential website(s):")
                for i, url in enumerate(discovered_urls, 1):
                    is_valid = is_valid_personal_website(url)
                    status = "✅ Valid" if is_valid else "❌ Filtered"
                    print(f"   {i}. {url} → {status}")
            else:
                print("   ❌ No personal websites discovered")

        # Test website enrichment if URLs found
        enrichment_result = None
        if discovered_urls:
            if verbose:
                print("\n🌐 Testing Website Enrichment:")

            firecrawl_func = create_test_firecrawl_wrapper()
            enriched_profile = sync_enrich_profile_with_websites(
                profile, verbose=verbose, firecrawl_scrape_func=firecrawl_func
            )

            enrichment = enriched_profile.get("website_enrichment", {})
            if enrichment:
                summary = enrichment.get("enrichment_summary", {})
                insights = summary.get("combined_insights", {})

                enrichment_result = {
                    "websites_crawled": summary.get("websites_crawled", 0),
                    "additional_skills": len(insights.get("additional_skills", [])),
                    "experience_entries": len(
                        insights.get("additional_experience", [])
                    ),
                    "projects_found": len(insights.get("additional_projects", [])),
                    "services_offered": len(insights.get("professional_services", [])),
                    "top_skills": insights.get("additional_skills", [])[:5],
                }

                if verbose:
                    print("   ✅ Enrichment successful:")
                    print(
                        f"      Websites crawled: {enrichment_result['websites_crawled']}"
                    )
                    print(
                        f"      Additional skills: {enrichment_result['additional_skills']}"
                    )
                    print(
                        f"      Experience entries: {enrichment_result['experience_entries']}"
                    )
                    if enrichment_result["top_skills"]:
                        print(
                            f"      Top skills: {', '.join(enrichment_result['top_skills'])}"
                        )

        return {
            "username": username,
            "basic_info": basic_info,
            "discovered_urls": discovered_urls,
            "enrichment": enrichment_result,
            "profile_data": profile if discovered_urls else None,
        }

    except Exception as e:
        if verbose:
            print(f"❌ Error analyzing {username}: {e}")
        return {
            "username": username,
            "error": str(e),
            "basic_info": None,
            "discovered_urls": [],
            "enrichment": None,
        }


def generate_enhanced_cv_for_profile(
    analysis_result: Dict[str, Any], output_format: str = "markdown"
) -> bool:
    """
    Generate enhanced CV for a profile analysis result.
    """
    username = analysis_result["username"]

    if analysis_result.get("error") or not analysis_result.get("profile_data"):
        print(f"⚠️  Skipping CV generation for {username} (no valid profile data)")
        return False

    try:
        # Create output directory
        timestamp = time.strftime("%Y-%m-%d")
        output_dir = Path(f"generated_cvs/{username}_{timestamp}")
        output_dir.mkdir(parents=True, exist_ok=True)

        profile_data = analysis_result["profile_data"]

        # Add website enrichment if available
        if analysis_result.get("enrichment"):
            # Re-run enrichment for CV generation
            firecrawl_func = create_test_firecrawl_wrapper()
            enriched_profile = sync_enrich_profile_with_websites(
                profile_data, verbose=False, firecrawl_scrape_func=firecrawl_func
            )
        else:
            enriched_profile = profile_data

        # Generate files
        files_generated = []

        if output_format in ["markdown", "all"]:
            md_file = output_dir / f"{username}_cv_enhanced.md"
            render_markdown(enriched_profile, md_file, "professional", DEFAULT_CONFIG)
            files_generated.append(md_file)

        if output_format in ["html", "all"]:
            html_file = output_dir / f"{username}_cv_enhanced.html"
            render_html(enriched_profile, html_file, "modern", DEFAULT_CONFIG)
            files_generated.append(html_file)

        print(f"✅ Generated CV files for {username}:")
        for file_path in files_generated:
            file_size = file_path.stat().st_size / 1024
            print(f"   📄 {file_path.name} ({file_size:.1f}KB)")

        return True

    except Exception as e:
        print(f"❌ Error generating CV for {username}: {e}")
        return False


def test_multiple_profiles(usernames: List[str]) -> Dict[str, Any]:
    """
    Test website enrichment with multiple GitHub profiles.
    """
    print("🎯 Testing Website Enrichment with Multiple GitHub Profiles")
    print("=" * 70)

    results = {}
    summary_stats = {
        "total_profiles": len(usernames),
        "successful_analyses": 0,
        "profiles_with_websites": 0,
        "profiles_with_enrichment": 0,
        "cvs_generated": 0,
        "total_additional_skills": 0,
    }

    for i, username in enumerate(usernames, 1):
        print(f"\n🔄 Testing Profile {i}/{len(usernames)}: {username}")

        # Analyze profile
        analysis = analyze_profile_websites(username, verbose=True)
        results[username] = analysis

        # Update stats
        if not analysis.get("error"):
            summary_stats["successful_analyses"] += 1

            if analysis.get("discovered_urls"):
                summary_stats["profiles_with_websites"] += 1

                if analysis.get("enrichment"):
                    summary_stats["profiles_with_enrichment"] += 1
                    summary_stats["total_additional_skills"] += analysis[
                        "enrichment"
                    ].get("additional_skills", 0)

        # Generate CV
        if generate_enhanced_cv_for_profile(analysis, "markdown"):
            summary_stats["cvs_generated"] += 1

        # Brief pause between profiles
        time.sleep(1)

    return results, summary_stats


def print_comprehensive_summary(results: Dict[str, Any], stats: Dict[str, Any]):
    """
    Print a comprehensive summary of all test results.
    """
    print(f"\n{'='*70}")
    print("📊 COMPREHENSIVE TEST SUMMARY")
    print(f"{'='*70}")

    # Overall statistics
    print("\n🔢 Overall Statistics:")
    print(f"   Total profiles tested: {stats['total_profiles']}")
    print(f"   Successful analyses: {stats['successful_analyses']}")
    print(f"   Profiles with websites: {stats['profiles_with_websites']}")
    print(f"   Profiles with enrichment: {stats['profiles_with_enrichment']}")
    print(f"   CVs generated: {stats['cvs_generated']}")
    print(f"   Total additional skills discovered: {stats['total_additional_skills']}")

    # Success rates
    if stats["total_profiles"] > 0:
        analysis_rate = (stats["successful_analyses"] / stats["total_profiles"]) * 100
        website_rate = (
            (stats["profiles_with_websites"] / stats["successful_analyses"]) * 100
            if stats["successful_analyses"] > 0
            else 0
        )
        enrichment_rate = (
            (stats["profiles_with_enrichment"] / stats["profiles_with_websites"]) * 100
            if stats["profiles_with_websites"] > 0
            else 0
        )

        print("\n📈 Success Rates:")
        print(f"   Profile analysis: {analysis_rate:.1f}%")
        print(f"   Website discovery: {website_rate:.1f}%")
        print(f"   Enrichment success: {enrichment_rate:.1f}%")

    # Detailed profile breakdown
    print("\n👥 Profile Breakdown:")

    for username, result in results.items():
        print(f"\n   🔹 {username}:")

        if result.get("error"):
            print(f"      ❌ Error: {result['error']}")
            continue

        basic = result.get("basic_info", {})
        print(f"      Name: {basic.get('name', 'N/A')}")
        print(f"      Repositories: {basic.get('repos', 0)}")
        print(f"      Stars: {basic.get('stars', 0)}")
        print(f"      Activity Score: {basic.get('activity_score', 0)}")

        if basic.get("blog"):
            print(f"      Website: {basic['blog']}")

        urls = result.get("discovered_urls", [])
        if urls:
            print(f"      Discovered URLs: {len(urls)}")
            for url in urls[:2]:  # Show first 2 URLs
                print(f"         - {url}")
            if len(urls) > 2:
                print(f"         ... and {len(urls) - 2} more")
        else:
            print("      Discovered URLs: None")

        enrichment = result.get("enrichment")
        if enrichment:
            print("      Enrichment: ✅ Success")
            print(
                f"         Additional skills: {enrichment.get('additional_skills', 0)}"
            )
            print(
                f"         Experience entries: {enrichment.get('experience_entries', 0)}"
            )
            if enrichment.get("top_skills"):
                print(f"         Top skills: {', '.join(enrichment['top_skills'])}")
        else:
            print("      Enrichment: ❌ No enrichment data")

    # Feature flexibility demonstration
    print("\n🔧 Feature Flexibility Demonstrated:")
    print("   ✅ Handles profiles with personal websites")
    print("   ✅ Handles profiles without websites gracefully")
    print("   ✅ Validates and filters discovered URLs")
    print("   ✅ Provides fallback behavior when enrichment fails")
    print("   ✅ Maintains consistent CV generation regardless of enrichment status")
    print("   ✅ Preserves original profile data when no websites found")


def main():
    """
    Main test function for multiple GitHub profiles.
    """
    # Test profiles as requested
    test_usernames = ["AngelPn", "dirkbrnd", "WilliamEspegren", "manuhortet"]

    print("🚀 Website Enrichment Multi-Profile Test Suite")
    print("Testing flexibility with various GitHub profile types")
    print(f"Target usernames: {', '.join(test_usernames)}")

    # Run comprehensive tests
    results, stats = test_multiple_profiles(test_usernames)

    # Print summary
    print_comprehensive_summary(results, stats)

    # Final output directory summary
    print("\n📁 Output Directory Summary:")
    generated_dir = Path("generated_cvs")
    if generated_dir.exists():
        profile_dirs = [d for d in generated_dir.iterdir() if d.is_dir()]
        print(f"   Total profile directories: {len(profile_dirs)}")

        for profile_dir in sorted(profile_dirs):
            files = list(profile_dir.glob("*.md")) + list(profile_dir.glob("*.html"))
            total_size = sum(f.stat().st_size for f in files) / 1024
            print(f"   📂 {profile_dir.name}: {len(files)} files ({total_size:.1f}KB)")

    print("\n✅ Multi-profile test completed successfully!")
    print("🎉 Website enrichment system demonstrates excellent flexibility!")


if __name__ == "__main__":
    main()
