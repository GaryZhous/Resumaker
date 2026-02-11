from __future__ import annotations
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from models import ResumeData

TEMPLATE_DIR = Path(__file__).parent / "templates"

# Use LaTeX-safe delimiters:
#   << ... >>  for variables
#   <% ... %>  for blocks
#   <# ... #>  for comments
_env = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)),
    autoescape=False,
    variable_start_string="<<",
    variable_end_string=">>",
    block_start_string="<%",
    block_end_string="%>",
    comment_start_string="<#",
    comment_end_string="#>",
)

def render_latex(resume: ResumeData) -> str:
    tpl = _env.get_template("resume.tex.j2")
    return tpl.render(**resume.model_dump())