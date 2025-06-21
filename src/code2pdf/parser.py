"""
Convert GitHub data into the dictionary expected by the LaTeX template.
Later we'll add local README.md parsing and resume.toml overrides.
"""
from __future__ import annotations


def to_template_context(profile: dict) -> dict:
    # For now pass through unchanged.
    return profile