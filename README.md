# Resumaker

Inspired by [Resumake](https://latexresu.me/), this is a resume builder for my fellow job seekers in STEM. It is based on my own resume which got me interviews from big tech companies and unicorns like Google, Stripe, Block, Expedia, and Atlassian, and even quant companies like Squarepoint and DRW.
<img width="1635" height="1110" alt="image" src="https://github.com/user-attachments/assets/1b30fd97-5413-4408-97ae-c87d90951542" />
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
