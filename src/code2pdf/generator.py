"""
Render LaTeX template and compile PDF.
"""
from __future__ import annotations
import subprocess
import tempfile
from pathlib import Path

from jinja2 import Environment, PackageLoader, select_autoescape

env = Environment(
    loader=PackageLoader("code2pdf", "template"),
    autoescape=False,
    trim_blocks=True,
    lstrip_blocks=True,
)


def render_pdf(context: dict, output_path: Path):
    template = env.get_template("resume.tex")
    tex_source = template.render(**context)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_tex = Path(tmpdir) / "resume.tex"
        tmp_tex.write_text(tex_source, encoding="utf-8")
        subprocess.run(
            ["latexmk", "-pdf", "-interaction=nonstopmode", tmp_tex.name],
            cwd=tmpdir,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        final_pdf = Path(tmpdir) / "resume.pdf"
        final_pdf.replace(output_path)