import typer
from pathlib import Path

from .github import fetch_profile
from .generator import render_pdf

app = typer.Typer(add_completion=False, no_args_is_help=True)

@app.command()
def build(
    user: str,
    output: Path = typer.Option("resume.pdf", help="Destination PDF file"),
    token: str | None = typer.Option(None, help="GitHub token if >60 req/hour"),
):
    """Build a PDF résumé from a GitHub profile."""
    data = fetch_profile(user, token)
    typer.echo(f"Generating résumé for {data['name']} …")
    render_pdf(data, output)
    typer.echo(f"✅  Done → {output}")

if __name__ == "__main__":
    app()