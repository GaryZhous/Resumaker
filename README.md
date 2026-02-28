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
## How to use
<img width="1626" height="1107" alt="image" src="https://github.com/user-attachments/assets/dc60528e-5ab2-4843-a696-ea5d595859aa" />

1. Launch the app and fill in your details.
2. Add or remove sections as needed (Education, Work, Skills, Projects, Awards).
3. Export to LaTeX (.tex) for best results.
4. Upload the .tex file to [Overleaf](https://www.overleaf.com) and compile to download your PDF.

Notes:
- JSON is the app's data format. Use it to save/load your resume content.
- To use a different layout, edit the LaTeX template at `templates/resume.tex.j2`.
