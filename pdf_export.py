from __future__ import annotations
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Tuple, Optional

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from models import ResumeData
from latex import render_latex


def _find_pdflatex() -> Optional[str]:
    env_path = os.environ.get("LATEX_PDFLATEX")
    if env_path and Path(env_path).exists():
        return env_path

    which = shutil.which("pdflatex")
    if which:
        return which

    # Common Windows installs (MiKTeX / TeX Live)
    candidates = [
        r"C:\\Program Files\\MiKTeX\\miktex\\bin\\x64\\pdflatex.exe",
        r"C:\\Program Files\\MiKTeX\\miktex\\bin\\pdflatex.exe",
        r"C:\\Program Files\\MiKTeX 2.9\\miktex\\bin\\x64\\pdflatex.exe",
        r"C:\\Program Files\\texlive\\2024\\bin\\windows\\pdflatex.exe",
        r"C:\\Program Files\\texlive\\2023\\bin\\windows\\pdflatex.exe",
        r"C:\\Program Files\\texlive\\2022\\bin\\windows\\pdflatex.exe",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return candidate

    return None


def try_build_pdf_with_pdflatex(latex_src: str) -> Tuple[bool, Optional[bytes], str]:
    pdflatex = _find_pdflatex()
    if not pdflatex:
        return (False, None, "pdflatex not found. Install MiKTeX/TeX Live or set LATEX_PDFLATEX.")

    with tempfile.TemporaryDirectory() as d:
        dpath = Path(d)
        tex_path = dpath / "resume.tex"
        tex_path.write_text(latex_src, encoding="utf-8")

        cmd = [pdflatex, "-interaction=nonstopmode", "resume.tex"]
        p = subprocess.run(cmd, cwd=str(dpath), capture_output=True, text=True)
        log = (p.stdout or "") + "\n" + (p.stderr or "")

        pdf_path = dpath / "resume.pdf"
        if p.returncode != 0 or not pdf_path.exists():
            return (False, None, log)

        return (True, pdf_path.read_bytes(), log)


def build_fallback_pdf_reportlab(resume: ResumeData) -> bytes:
    """
    Minimal PDF if pdflatex isn't installed.
    Not as pretty as your LaTeX, but produces a valid downloadable PDF.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
        out_path = Path(f.name)

    c = canvas.Canvas(str(out_path), pagesize=letter)
    width, height = letter
    x = 50
    y = height - 50
    line = 14

    def draw(txt, bold=False):
        nonlocal y
        c.setFont("Helvetica-Bold" if bold else "Helvetica", 11 if not bold else 12)
        c.drawString(x, y, txt[:120])
        y -= line

    p = resume.personal
    draw(p.full_name, bold=True)
    draw(f"{p.location} | {p.phone} | {p.email}")
    draw(f"LinkedIn: {p.linkedin}")
    draw(f"GitHub: {p.github}")
    draw(f"Portfolio: {p.portfolio}")
    y -= 10

    draw(resume.section_education, bold=True)
    for e in resume.education:
        draw(f"{e.school_name} — {e.school_location}", bold=True)
        draw(f"{e.degree} in {e.major} ({e.start_date} - {e.end_date})")
        if e.gpa:
            draw(f"GPA: {e.gpa}")
        y -= 6

    draw(resume.section_skills, bold=True)
    for s in resume.skills:
        draw(f"{s.name}: " + ", ".join(s.details))
    y -= 6

    draw(resume.section_experience, bold=True)
    for xjob in resume.experience:
        draw(f"{xjob.company_name} — {xjob.company_location}", bold=True)
        draw(f"{xjob.job_title} ({xjob.start_date} - {xjob.end_date})")
        for b in xjob.responsibilities[:6]:
            draw(f"• {b}")
        y -= 6

    draw(resume.section_projects, bold=True)
    for pr in resume.projects:
        draw(f"{pr.project_name} — {pr.genre}", bold=True)
        if pr.link:
            draw(pr.link)
        draw(f"{pr.start_date} - {pr.end_date}")
        for b in pr.description_bullets[:5]:
            draw(f"• {b}")
        y -= 6

    draw(resume.section_awards, bold=True)
    for a in resume.awards:
        draw(f"{a.award_name}: {a.summary}", bold=True)
        if a.awarder:
            draw(f"{a.awarder}")
        if a.award_date:
            draw(f"{a.award_date}")
        y -= 6

    c.showPage()
    c.save()

    data = out_path.read_bytes()
    try:
        out_path.unlink(missing_ok=True)
    except Exception:
        pass
    return data