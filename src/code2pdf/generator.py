"""
Render Markdown CV template.
"""
from __future__ import annotations
from pathlib import Path

from jinja2 import Environment, PackageLoader

env = Environment(
    loader=PackageLoader("code2pdf", "template"),
    autoescape=False,
    trim_blocks=True,
    lstrip_blocks=True,
)


def render_markdown(context: dict, output_path: Path):
    """Generate a markdown CV from GitHub profile data."""
    template = env.get_template("resume.md")
    markdown_content = template.render(**context)
    
    output_path.write_text(markdown_content, encoding="utf-8")