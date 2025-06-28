import typer
from pathlib import Path
from typing import Optional
from enum import Enum
from datetime import datetime, timedelta

from .github import fetch_profile
from .generator import render_markdown, render_html
from .config import load_config, DEFAULT_CONFIG

app = typer.Typer(add_completion=False, no_args_is_help=True)


class OutputFormat(str, Enum):
    markdown = "markdown"
    html = "html"
    all = "all"


class TemplateTheme(str, Enum):
    professional = "professional"
    modern = "modern"
    minimal = "minimal"


def create_output_directory(username: str, output_dir: Optional[Path] = None) -> Path:
    """Create and return the output directory for generated files."""
    if output_dir:
        # Use custom output directory
        base_dir = output_dir
    else:
        # Create organized folder structure
        timestamp = datetime.now().strftime("%Y-%m-%d")
        base_dir = Path("generated_cvs") / f"{username}_{timestamp}"

    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir


@app.command()
def build(
    user: str = typer.Argument(..., help="GitHub username to generate CV for"),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Output file path or directory"
    ),
    output_dir: Optional[Path] = typer.Option(
        None, "--output-dir", "-d", help="Output directory for generated files"
    ),
    format: OutputFormat = typer.Option(
        OutputFormat.html, "--format", "-f", help="Output format"
    ),
    theme: TemplateTheme = typer.Option(
        TemplateTheme.professional, "--theme", "-t", help="CV template theme"
    ),
    token: Optional[str] = typer.Option(
        None, "--token", help="GitHub token for higher rate limits"
    ),
    config: Optional[Path] = typer.Option(
        None, "--config", "-c", help="Path to configuration file"
    ),
    cache: bool = typer.Option(
        True, "--cache/--no-cache", help="Enable/disable API response caching"
    ),
    enrich_websites: bool = typer.Option(
        False,
        "--enrich-websites",
        help="Crawl personal websites for additional profile information",
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
):
    """Build a professional CV from a GitHub profile with HTML and Markdown output formats."""

    try:
        # Load configuration
        config_data = load_config(config) if config else DEFAULT_CONFIG

        if verbose:
            typer.echo(f"🚀 Fetching profile data for {user}...")

        # Fetch profile data with caching support
        data = fetch_profile(
            user,
            token,
            use_cache=cache,
            verbose=verbose,
            enrich_websites=enrich_websites,
        )

        if verbose:
            typer.echo(f"📊 Found {len(data['repos'])} repositories")
            typer.echo(
                f"🏆 Total stars: {data['contribution_patterns']['total_stars_earned']}"
            )

        typer.echo(f"✨ Generating CV for {data['name']} using {theme.value} theme...")

        # Create output directory
        if output and output.is_file():
            # Single file output - use parent directory
            output_directory = output.parent
            custom_filename = output.name
        else:
            # Directory output or default
            output_directory = create_output_directory(user, output_dir or output)
            custom_filename = None

            if verbose:
                typer.echo(f"📁 Output directory: {output_directory}")

        # Determine output file(s)
        if custom_filename:
            # Single custom file specified
            base_name = (
                custom_filename.rsplit(".", 1)[0]
                if "." in custom_filename
                else custom_filename
            )
            if format == OutputFormat.all:
                outputs = {
                    "markdown": output_directory / f"{base_name}.md",
                    "html": output_directory / f"{base_name}.html",
                }
            else:
                ext = "md" if format == OutputFormat.markdown else format.value
                if format == OutputFormat.markdown and custom_filename.endswith(".html"):
                    # Auto-detect format from extension
                    ext = "html"
                    format = OutputFormat.html
                outputs = {format.value: output_directory / f"{base_name}.{ext}"}
        else:
            # Default organized filenames
            base_name = f"{user}_cv_{theme.value}"
            if format == OutputFormat.all:
                outputs = {
                    "markdown": output_directory / f"{base_name}.md",
                    "html": output_directory / f"{base_name}.html",
                }
            else:
                ext = "md" if format == OutputFormat.markdown else format.value
                outputs = {format.value: output_directory / f"{base_name}.{ext}"}

        # Generate output(s)
        generated_files = []
        for output_format, output_path in outputs.items():
            try:
                if output_format == "markdown":
                    render_markdown(data, output_path, theme.value, config_data)
                elif output_format == "html":
                    render_html(data, output_path, theme.value, config_data)

                generated_files.append(output_path)
                if verbose:
                    typer.echo(f"📄 Generated {output_format.upper()}: {output_path}")

            except Exception as e:
                typer.echo(
                    f"❌ Failed to generate {output_format.upper()}: {str(e)}", err=True
                )
                continue

        if generated_files:
            typer.echo(f"✅ Successfully generated {len(generated_files)} file(s)")
            typer.echo(f"📁 Output directory: {output_directory.resolve()}")
            for file in generated_files:
                file_size = file.stat().st_size / 1024  # Size in KB
                typer.echo(f"   → {file.name} ({file_size:.1f}KB)")
        else:
            typer.echo("❌ No files were generated successfully", err=True)
            raise typer.Exit(1)

    except KeyboardInterrupt:
        typer.echo("\n⏹️  Operation cancelled by user", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"❌ Error: {str(e)}", err=True)
        if verbose:
            import traceback

            typer.echo("🔍 Full error traceback:", err=True)
            typer.echo(traceback.format_exc(), err=True)
        raise typer.Exit(1)


@app.command()
def config():
    """Show current configuration and setup help."""
    typer.echo("🔧 GitHub Scraper Configuration")
    typer.echo("\n📁 Available output formats:")
    typer.echo("  • markdown (.md) - GitHub-compatible markdown")
    typer.echo("  • html (.html) - Styled HTML with CSS (default)")

    typer.echo("\n📂 Output Organization:")
    typer.echo("  • Files are organized in generated_cvs/{username}_{date}/ folders")
    typer.echo("  • Use --output-dir to specify a custom directory")
    typer.echo("  • Use --output file.ext for single file output")

    typer.echo("\n🎨 Available themes:")
    typer.echo("  • professional - Clean, corporate style")
    typer.echo("  • modern - Contemporary design with colors")
    typer.echo("  • minimal - Simple, text-focused layout")

    typer.echo("\n🔑 GitHub Token Setup:")
    typer.echo("  1. Visit: https://github.com/settings/tokens")
    typer.echo("  2. Generate a new token with 'public_repo' scope")
    typer.echo("  3. Use: github-scraper build username --token YOUR_TOKEN")

    typer.echo("\n📊 Rate Limits:")
    typer.echo("  • Without token: 60 requests/hour")
    typer.echo("  • With token: 5,000 requests/hour")


@app.command()
def clean(
    username: Optional[str] = typer.Argument(
        None, help="Username to clean (or all if not specified)"
    ),
    days: int = typer.Option(7, "--days", help="Remove folders older than N days"),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
):
    """Clean up old generated CV folders."""
    generated_dir = Path("generated_cvs")

    if not generated_dir.exists():
        typer.echo("📂 No generated_cvs directory found - nothing to clean")
        return

    folders_to_remove = []
    cutoff_date = datetime.now() - timedelta(days=days)

    for folder in generated_dir.iterdir():
        if folder.is_dir():
            # Check if folder matches username pattern
            if username and not folder.name.startswith(f"{username}_"):
                continue

            # Check folder age
            folder_time = datetime.fromtimestamp(folder.stat().st_mtime)
            if folder_time < cutoff_date:
                folders_to_remove.append(folder)

    if not folders_to_remove:
        age_desc = f"older than {days} days"
        user_desc = f"for user '{username}'" if username else ""
        typer.echo(f"🧹 No folders found {user_desc} {age_desc}")
        return

    typer.echo(f"🗑️  Found {len(folders_to_remove)} folder(s) to remove:")
    for folder in folders_to_remove:
        folder_size = sum(f.stat().st_size for f in folder.rglob("*") if f.is_file())
        typer.echo(f"   • {folder.name} ({folder_size / 1024:.1f}KB)")

    if not confirm:
        if not typer.confirm(f"\nRemove these {len(folders_to_remove)} folder(s)?"):
            typer.echo("❌ Cleanup cancelled")
            return

    removed_count = 0
    for folder in folders_to_remove:
        try:
            import shutil

            shutil.rmtree(folder)
            removed_count += 1
            typer.echo(f"🗑️  Removed {folder.name}")
        except Exception as e:
            typer.echo(f"❌ Failed to remove {folder.name}: {e}", err=True)

    typer.echo(f"✅ Successfully removed {removed_count} folder(s)")


@app.command()
def doctor():
    """Check system dependencies and configuration."""
    typer.echo("🔍 System Diagnostic")
    typer.echo("=" * 40)

    # Check Python version
    import sys

    typer.echo(f"🐍 Python version: {sys.version.split()[0]}")

    # Check core dependencies
    import importlib.util

    if importlib.util.find_spec("github"):
        typer.echo("✅ PyGithub: Available")
    else:
        typer.echo("❌ PyGithub: Missing")

    if importlib.util.find_spec("jinja2"):
        typer.echo("✅ Jinja2: Available")
    else:
        typer.echo("❌ Jinja2: Missing")

    if importlib.util.find_spec("markdown"):
        typer.echo("✅ Markdown: Available")
    else:
        typer.echo("❌ Markdown: Missing")

    if importlib.util.find_spec("yaml"):
        typer.echo("✅ YAML config support: Available")
    else:
        typer.echo("⚠️  YAML config support: Not available (optional)")

    # Check cache directory
    from .github import CACHE_DIR

    if CACHE_DIR.exists():
        typer.echo(f"✅ Cache directory: {CACHE_DIR}")
        cache_files = list(CACHE_DIR.glob("*.json"))
        typer.echo(f"📦 Cached profiles: {len(cache_files)}")
    else:
        typer.echo(f"⚠️  Cache directory will be created: {CACHE_DIR}")

    # Check output directory
    output_dir = Path("generated_cvs")
    if output_dir.exists():
        folders = [f for f in output_dir.iterdir() if f.is_dir()]
        total_size = sum(
            f.stat().st_size
            for folder in folders
            for f in folder.rglob("*")
            if f.is_file()
        )
        typer.echo(
            f"📁 Generated CVs: {len(folders)} folders ({total_size / 1024:.1f}KB total)"
        )
    else:
        typer.echo("📁 Generated CVs: No output directory yet")


if __name__ == "__main__":
    app()
