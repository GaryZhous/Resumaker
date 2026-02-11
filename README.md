# Resumaker

A simple, template-based resume builder with a desktop UI (PySide6). Edit your resume data in the app and export to LaTeX or JSON.

## Features
- Form-based editor for personal info, education, work, skills, projects, and awards
- Export resume to LaTeX (.tex)
- Export and import resume data as JSON

## Requirements
- Python 3.10+
- Dependencies in `requirements.txt`

## Setup
```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run
```bash
python main.py
```

## Notes
- PDF export is currently disabled in the UI.
- The LaTeX template lives at `templates/resume.tex.j2`.

## Project Structure
- `main.py`: UI and app logic
- `models.py`: Pydantic models for resume data
- `latex.py`: Jinja2 LaTeX rendering
- `pdf_export.py`: PDF rendering helpers (unused by default)
- `templates/`: LaTeX templates
