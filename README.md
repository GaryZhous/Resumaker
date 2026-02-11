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

- Simply fill the entries and add/remove sections based on your experience
- Export the file in either json or LaTex (recommended)
- Open the LaTex file on [Overleaf](https://www.overleaf.com) and you can download your newly built resume as a PDF!
- If you want to change the template, you can simply load your own template in the form of json
