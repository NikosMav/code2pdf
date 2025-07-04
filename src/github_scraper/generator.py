"""
Enhanced CV generator with comprehensive data analysis and markdown output.
"""

from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from jinja2 import Environment, PackageLoader

# Initialize Jinja2 environment
env = Environment(
    loader=PackageLoader("github_scraper", "template"),
    autoescape=False,
    trim_blocks=True,
    lstrip_blocks=True,
)


# Add custom filters
def format_number(value: int) -> str:
    """Format large numbers with K/M suffixes."""
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    elif value >= 1_000:
        return f"{value / 1_000:.1f}K"
    return str(value)


def days_ago(days: int) -> str:
    """Convert days to human-readable format."""
    if days == 0:
        return "today"
    elif days == 1:
        return "yesterday"
    elif days < 7:
        return f"{days} days ago"
    elif days < 30:
        return f"{days // 7} weeks ago"
    elif days < 365:
        return f"{days // 30} months ago"
    else:
        return f"{days // 365} years ago"


env.filters["format_number"] = format_number
env.filters["days_ago"] = days_ago


def render_markdown(
    context: Dict[str, Any],
    output_path: Path,
    config: Optional[Dict[str, Any]] = None,
) -> None:
    """Generate a comprehensive markdown CV from GitHub profile data with rich analytics."""
    # Add config to context
    enhanced_context = {
        **context,
        "config": config or {},
        "generated_at": datetime.now().isoformat(),
    }

    # Use the main comprehensive template
    template = env.get_template("resume.md")
    markdown_content = template.render(**enhanced_context)
    output_path.write_text(markdown_content, encoding="utf-8")