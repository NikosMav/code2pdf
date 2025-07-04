import typer
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta

from .github import fetch_profile
from .generator import render_markdown
from .config import load_config, DEFAULT_CONFIG

app = typer.Typer(add_completion=False, no_args_is_help=True)




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


    token: Optional[str] = typer.Option(
        None, "--token", help="GitHub token for higher rate limits"
    ),
    config: Optional[Path] = typer.Option(
        None, "--config", "-c", help="Path to configuration file"
    ),
    cache: bool = typer.Option(
        True, "--cache/--no-cache", help="Enable/disable caching (GitHub profiles cached 1h, websites 24h)"
    ),
    refresh: bool = typer.Option(
        False, "--refresh", help="Force fresh download, bypass all caches (same as --no-cache)"
    ),
    enrich_websites: bool = typer.Option(
        False,
        "--enrich-websites",
        help="Crawl personal websites for additional profile information",
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
    include_deeper_signals: bool = typer.Option(
        False, "--include-deeper-signals", help="Include deeper GitHub signals (PR reviews, issues, discussions, projects)"
    ),
    full_profile: bool = typer.Option(
        False, "--full-profile", help="Include all features: website enrichment + deeper signals"
    ),
):
    """Build a professional CV from a GitHub profile with comprehensive data scraping and analysis."""

    try:
        # Load configuration
        config_data = load_config(config) if config else DEFAULT_CONFIG

        if verbose:
            typer.echo(f"🚀 Fetching profile data for {user}...")

        # Determine cache usage - refresh flag overrides cache setting
        use_cache = cache and not refresh
        
        if refresh and verbose:
            typer.echo("🔄 Refresh mode: forcing fresh download, bypassing all caches")
        elif not cache and verbose:
            typer.echo("🚫 Cache disabled: fetching fresh data")

        # Full profile mode enables all features
        if full_profile:
            enrich_websites = True
            include_deeper_signals = True
            if verbose:
                typer.echo("🚀 Full profile mode: enabling all features")

        # Fetch profile data with caching support
        data = fetch_profile(
            user,
            token,
            use_cache=use_cache,
            verbose=verbose,
            enrich_websites=enrich_websites,
            config_data=config_data,
        )

        # Collect deeper signals if requested
        if include_deeper_signals:
            try:
                from .plugins.deeper_signals import collect
                deeper_signals = collect(
                    user,
                    token=token,
                    use_cache=use_cache,
                    verbose=verbose
                )
                if deeper_signals:
                    data["deeper_signals"] = deeper_signals
                    if verbose:
                        typer.echo(f"🔍 Collected deeper signals: {len(deeper_signals)} categories")
            except ImportError as e:
                if verbose:
                    typer.echo(f"⚠️  Deeper signals plugin not available: {e}")
            except Exception as e:
                if verbose:
                    typer.echo(f"⚠️  Failed to collect deeper signals: {e}")

        if verbose:
            typer.echo(f"📊 Found {len(data['repos'])} repositories")
            typer.echo(
                f"🏆 Total stars: {data['contribution_patterns']['total_stars_earned']}"
            )

        typer.echo(f"✨ Generating comprehensive CV for {data['name']} with data analysis...")

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

        # Determine output file
        if custom_filename:
            # Single custom file specified
            base_name = (
                custom_filename.rsplit(".", 1)[0]
                if "." in custom_filename
                else custom_filename
            )
            output_file = output_directory / f"{base_name}.md"
        else:
            # Default organized filename
            base_name = f"{user}_comprehensive_cv"
            output_file = output_directory / f"{base_name}.md"

        # Generate markdown output
        try:
            render_markdown(data, output_file, config_data)
            
            file_size = output_file.stat().st_size / 1024  # Size in KB
            typer.echo(f"✅ Successfully generated CV: {output_file.name} ({file_size:.1f}KB)")
            typer.echo(f"📁 Output directory: {output_directory.resolve()}")
            
            if verbose:
                typer.echo(f"📄 Generated Markdown: {output_file}")

        except Exception as e:
            typer.echo(f"❌ Failed to generate CV: {str(e)}", err=True)
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
    typer.echo("\n📁 Output format:")
    typer.echo("  • markdown (.md) - GitHub-compatible markdown with comprehensive data analysis")

    typer.echo("\n📂 Output Organization:")
    typer.echo("  • Files are organized in generated_cvs/{username}_{date}/ folders")
    typer.echo("  • Use --output-dir to specify a custom directory")
    typer.echo("  • Use --output file.ext for single file output")

    typer.echo("\n🎯 Focus:")
    typer.echo("  • Comprehensive data scraping and analysis")
    typer.echo("  • Professional markdown output with rich insights")
    typer.echo("  • Website enrichment for complete profiles")

    typer.echo("\n🔑 GitHub Token Setup:")
    typer.echo("  1. Visit: https://github.com/settings/tokens")
    typer.echo("  2. Generate a new token with 'public_repo' scope")
    typer.echo("  3. Use: github-scraper build username --token YOUR_TOKEN")

    typer.echo("\n📊 Rate Limits:")
    typer.echo("  • Without token: 60 requests/hour")
    typer.echo("  • With token: 5,000 requests/hour (recommended for data scraping)")


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
