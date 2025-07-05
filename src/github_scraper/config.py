"""Configuration management for github-scraper."""

from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any, Optional

DEFAULT_CONFIG = {
    "github": {
        "cache_duration_hours": 1,
        "max_repos": 100,
        "include_forks": False,
        "include_private": False,
        "fetch_readme": True,
        "fetch_contributors": True,
        "fetch_releases": True,
        "fetch_languages": True,
        "fetch_workflows": True,
        "max_contributors_per_repo": 10,
        "max_releases_per_repo": 5,
    },
    "cv": {
        "max_featured_repos": 15,
        "activity_threshold_days": 90,
    },
    "scraping": {
        "enable_website_enrichment": True,
        "max_websites_per_profile": 3,
        "website_cache_duration_hours": 24,
    },
    "user_data": {
        "fetch_organizations": True,
        "fetch_gists": True,
        "fetch_social_accounts": True,
        "fetch_achievements": True,
        "max_gists": 20,
        "max_organizations": 10,
    },

}


def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """Load configuration from file or return defaults."""
    if not config_path:
        # Look for config in common locations
        config_candidates = [
            Path.cwd() / "github-scraper.json",
            Path.cwd() / ".github-scraper.json",
            Path.home() / ".config" / "github-scraper" / "config.json",
        ]

        for candidate in config_candidates:
            if candidate.exists():
                config_path = candidate
                break

    if not config_path or not config_path.exists():
        return DEFAULT_CONFIG.copy()

    try:
        config_text = config_path.read_text(encoding="utf-8")
        user_config = json.loads(config_text)

        # Merge with defaults
        return merge_configs(DEFAULT_CONFIG, user_config)

    except (json.JSONDecodeError, Exception) as e:
        # Fall back to defaults if config is invalid
        print(f"Warning: Could not load config from {config_path}: {e}")
        return DEFAULT_CONFIG.copy()


def merge_configs(default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge user config with defaults."""
    result = default.copy()

    for key, value in user.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value

    return result


def save_config(config: Dict[str, Any], config_path: Path) -> None:
    """Save configuration to file in JSON format."""
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")


def create_sample_config(output_path: Path) -> None:
    """Create a sample configuration file."""
    sample_config = {
        "github": {
            "cache_duration_hours": 2,
            "max_repos": 150,  # Higher limit for comprehensive analysis
            "include_forks": False,
            "include_private": False,
            "fetch_readme": True,
            "fetch_contributors": True,
            "fetch_releases": True,
            "fetch_languages": True,
            "fetch_workflows": True,
            "max_contributors_per_repo": 15,
            "max_releases_per_repo": 10,
        },
        "cv": {
            "max_featured_repos": 15,
            "activity_threshold_days": 365,
        },
        "scraping": {
            "enable_website_enrichment": True,
            "max_websites_per_profile": 5,
            "website_cache_duration_hours": 48,
        },
        "user_data": {
            "fetch_organizations": True,
            "fetch_gists": True,
            "fetch_social_accounts": True,
            "fetch_achievements": True,
            "max_gists": 30,
            "max_organizations": 15,
        },

    }

    save_config(sample_config, output_path)
