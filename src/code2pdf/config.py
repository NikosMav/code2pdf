"""Configuration management for code2pdf."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any, Optional

# Optional YAML support
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    yaml = None

DEFAULT_CONFIG = {
    "output": {
        "default_format": "markdown",
        "filename_template": "{username}_cv",
        "include_timestamp": False,
    },
    "github": {
        "cache_duration_hours": 1,
        "max_repos": 10,
        "include_forks": False,
        "include_private": False,
    },
    "cv": {
        "include_contact_info": True,
        "include_stats_table": True,
        "include_insights": True,
        "max_featured_repos": 8,
        "activity_threshold_days": 90,
    },
    "themes": {
        "professional": {
            "colors": {
                "primary": "#2563eb",
                "secondary": "#64748b",
                "accent": "#059669",
            },
            "fonts": {
                "body": "system-ui, -apple-system, sans-serif",
                "heading": "system-ui, -apple-system, sans-serif",
                "mono": "ui-monospace, 'Cascadia Code', consolas, monospace",
            }
        },
        "modern": {
            "colors": {
                "primary": "#7c3aed",
                "secondary": "#6b7280",
                "accent": "#f59e0b",
            },
            "fonts": {
                "body": "'Inter', system-ui, sans-serif",
                "heading": "'Inter', system-ui, sans-serif", 
                "mono": "'JetBrains Mono', ui-monospace, monospace",
            }
        },
        "minimal": {
            "colors": {
                "primary": "#374151",
                "secondary": "#9ca3af",
                "accent": "#111827",
            },
            "fonts": {
                "body": "Georgia, 'Times New Roman', serif",
                "heading": "Georgia, 'Times New Roman', serif",
                "mono": "'Courier New', monospace",
            }
        }
    }
}


def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """Load configuration from file or return defaults."""
    if not config_path:
        # Look for config in common locations
        config_candidates = [
            Path.cwd() / "code2pdf.json",
            Path.cwd() / ".code2pdf.json",
            Path.home() / ".config" / "code2pdf" / "config.json",
        ]
        
        # Only look for YAML files if YAML is available
        if YAML_AVAILABLE:
            config_candidates.extend([
                Path.cwd() / "code2pdf.yaml",
                Path.cwd() / ".code2pdf.yaml",
                Path.home() / ".config" / "code2pdf" / "config.yaml",
            ])
        
        for candidate in config_candidates:
            if candidate.exists():
                config_path = candidate
                break
    
    if not config_path or not config_path.exists():
        return DEFAULT_CONFIG.copy()
    
    try:
        config_text = config_path.read_text(encoding="utf-8")
        
        if config_path.suffix.lower() in ['.yaml', '.yml']:
            if not YAML_AVAILABLE:
                raise RuntimeError(
                    f"YAML configuration file found ({config_path}), "
                    "but PyYAML is not installed. Install it with: pip install pyyaml"
                )
            user_config = yaml.safe_load(config_text)
        else:
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


def save_config(config: Dict[str, Any], config_path: Path, format: str = "json") -> None:
    """Save configuration to file."""
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    if format.lower() == "yaml":
        if not YAML_AVAILABLE:
            raise RuntimeError("Cannot save YAML config: PyYAML is not installed")
        config_path.write_text(yaml.dump(config, default_flow_style=False), encoding="utf-8")
    else:
        config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")


def create_sample_config(output_path: Path, format: str = "json") -> None:
    """Create a sample configuration file."""
    sample_config = {
        "github": {
            "cache_duration_hours": 1,
            "max_repos": 15,
        },
        "cv": {
            "max_featured_repos": 10,
            "include_insights": True,
        },
        "output": {
            "default_format": "pdf",
            "include_timestamp": True,
        }
    }
    
    save_config(sample_config, output_path, format)


def is_yaml_available() -> bool:
    """Check if YAML support is available."""
    return YAML_AVAILABLE 