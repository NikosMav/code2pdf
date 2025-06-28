"""
Enhanced CV generator with multiple output formats and themes.
"""

from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, Optional
import markdown
from datetime import datetime

from jinja2 import Environment, PackageLoader

# Check for optional dependencies without importing them
_weasyprint_checked = False
_weasyprint_available = False


def _check_weasyprint_available() -> bool:
    """Check if WeasyPrint is available without importing it."""
    global _weasyprint_checked, _weasyprint_available

    if _weasyprint_checked:
        return _weasyprint_available

    try:
        # Suppress WeasyPrint warning messages more robustly
        import warnings
        import sys
        import io

        # Capture both warnings and stderr
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            # Redirect stderr to capture WeasyPrint messages
            old_stderr = sys.stderr
            sys.stderr = io.StringIO()

            try:
                import importlib.util

                if importlib.util.find_spec("weasyprint"):
                    _weasyprint_available = True
                else:
                    _weasyprint_available = False
            except (ImportError, OSError, Exception):
                _weasyprint_available = False
            finally:
                # Restore stderr
                sys.stderr = old_stderr

    except Exception:
        _weasyprint_available = False

    _weasyprint_checked = True
    return _weasyprint_available


# Initialize Jinja2 environment
env = Environment(
    loader=PackageLoader("code2pdf", "template"),
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
    theme: str = "professional",
    config: Optional[Dict[str, Any]] = None,
) -> None:
    """Generate a markdown CV from GitHub profile data."""
    # Add theme and config to context
    enhanced_context = {
        **context,
        "theme": theme,
        "config": config or {},
        "generated_at": datetime.now().isoformat(),
    }

    # Choose template based on theme
    template_name = f"resume_{theme}.md" if theme != "professional" else "resume.md"

    try:
        template = env.get_template(template_name)
    except Exception:
        # Fall back to default template if theme-specific template doesn't exist
        template = env.get_template("resume.md")

    markdown_content = template.render(**enhanced_context)
    output_path.write_text(markdown_content, encoding="utf-8")


def render_html(
    context: Dict[str, Any],
    output_path: Path,
    theme: str = "professional",
    config: Optional[Dict[str, Any]] = None,
) -> None:
    """Generate an HTML CV from GitHub profile data."""
    # First generate markdown
    md_content = _render_markdown_content(context, theme, config)

    # Convert markdown to HTML
    md = markdown.Markdown(
        extensions=[
            "markdown.extensions.tables",
            "markdown.extensions.fenced_code",
            "markdown.extensions.toc",
            "codehilite",
        ]
    )

    html_body = md.convert(md_content)

    # Get CSS for theme
    css_content = _get_theme_css(theme, config)

    # Generate full HTML document
    html_template = env.get_template("base.html")
    full_html = html_template.render(
        title=f"{context['name']} - CV",
        css=css_content,
        body=html_body,
        theme=theme,
        generated_at=datetime.now().isoformat(),
        **context,
    )

    output_path.write_text(full_html, encoding="utf-8")


def render_pdf(
    context: Dict[str, Any],
    output_path: Path,
    theme: str = "professional",
    config: Optional[Dict[str, Any]] = None,
) -> None:
    """Generate a PDF CV from GitHub profile data."""
    if not is_pdf_available():
        raise RuntimeError(
            "📋 PDF generation is not available on this system.\n\n"
            "💡 To enable PDF generation:\n"
            "   • On Ubuntu/Debian: sudo apt-get install libpango1.0-dev libharfbuzz-dev libffi-dev libjpeg-dev libopenjp2-7-dev\n"
            "   • On macOS: brew install pango harfbuzz\n"
            "   • On Windows: Consider using WSL or Docker for PDF generation\n\n"
            "🔄 Alternative solutions:\n"
            "   1. Generate HTML instead: --format html\n"
            "   2. Use browser 'Print to PDF' from HTML output\n"
            "   3. Use online HTML-to-PDF converters\n"
            "   4. Install GTK+ libraries for Windows"
        )

    # Import WeasyPrint only when actually needed
    try:
        import weasyprint  # type: ignore
    except ImportError:
        raise RuntimeError("WeasyPrint is not available for PDF generation")

    # First generate HTML
    html_content = _render_html_content(context, theme, config)

    # Convert HTML to PDF using WeasyPrint
    try:
        pdf_document = weasyprint.HTML(string=html_content)
        pdf_document.write_pdf(output_path)
    except Exception as e:
        raise RuntimeError(
            f"💥 Failed to generate PDF: {str(e)}\n\n"
            "🔄 Try generating HTML instead:\n"
            "   code2pdf build {username} --format html\n"
            "Then use your browser's 'Print to PDF' feature."
        )


def is_pdf_available() -> bool:
    """Check if PDF generation is available on this system."""
    return _check_weasyprint_available()


def _render_markdown_content(
    context: Dict[str, Any], theme: str, config: Optional[Dict[str, Any]] = None
) -> str:
    """Internal method to render markdown content without writing to file."""
    enhanced_context = {
        **context,
        "theme": theme,
        "config": config or {},
        "generated_at": datetime.now().isoformat(),
    }

    template_name = f"resume_{theme}.md" if theme != "professional" else "resume.md"

    try:
        template = env.get_template(template_name)
    except Exception:
        template = env.get_template("resume.md")

    return template.render(**enhanced_context)


def _render_html_content(
    context: Dict[str, Any], theme: str, config: Optional[Dict[str, Any]] = None
) -> str:
    """Internal method to render full HTML content."""
    md_content = _render_markdown_content(context, theme, config)

    md = markdown.Markdown(
        extensions=[
            "markdown.extensions.tables",
            "markdown.extensions.fenced_code",
            "markdown.extensions.toc",
            "codehilite",
        ]
    )

    html_body = md.convert(md_content)
    css_content = _get_theme_css(theme, config)

    html_template = env.get_template("base.html")
    return html_template.render(
        title=f"{context['name']} - CV",
        css=css_content,
        body=html_body,
        theme=theme,
        generated_at=datetime.now().isoformat(),
        **context,
    )


def _get_theme_css(theme: str, config: Optional[Dict[str, Any]] = None) -> str:
    """Get CSS styles for the specified theme."""
    try:
        css_template = env.get_template(f"styles_{theme}.css")
        theme_config = config.get("themes", {}).get(theme, {}) if config else {}
        return css_template.render(**theme_config)
    except Exception:
        # Fall back to default CSS
        try:
            css_template = env.get_template("styles.css")
            return css_template.render()
        except Exception:
            # Ultimate fallback: basic CSS
            return _get_fallback_css()


def _get_fallback_css() -> str:
    """Provide basic fallback CSS when templates are not available."""
    return """
    body { 
        font-family: system-ui, sans-serif; 
        line-height: 1.6; 
        max-width: 800px; 
        margin: 0 auto; 
        padding: 2rem;
        color: #1f2937;
    }
    h1, h2, h3 { 
        color: #2563eb; 
        margin-top: 2rem; 
    }
    h1 {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    h2 {
        font-size: 1.5rem;
        border-bottom: 2px solid #2563eb;
        padding-bottom: 0.5rem;
    }
    table { 
        width: 100%; 
        border-collapse: collapse; 
        margin: 1rem 0; 
    }
    th { 
        background-color: #2563eb;
        color: white;
        padding: 0.75rem;
        text-align: left;
    }
    td { 
        padding: 0.75rem; 
        text-align: left; 
        border-bottom: 1px solid #e5e7eb; 
    }
    tr:nth-child(even) {
        background-color: #f8fafc;
    }
    code { 
        background: #f3f4f6; 
        padding: 0.2rem 0.4rem; 
        border-radius: 0.25rem;
        font-family: ui-monospace, monospace;
    }
    a {
        color: #2563eb;
        text-decoration: none;
    }
    a:hover {
        text-decoration: underline;
    }
    .cv-footer {
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid #e5e7eb;
        text-align: center;
        font-size: 0.9rem;
        color: #6b7280;
    }
    """
