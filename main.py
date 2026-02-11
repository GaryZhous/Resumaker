from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import List, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QFormLayout, QLineEdit, QTextEdit, QPushButton, QLabel, QFileDialog,
    QMessageBox, QSpinBox, QScrollArea, QGroupBox, QComboBox
)

from models import ResumeData, EducationEntry, ExperienceEntry, SkillCategory, ProjectEntry, AwardEntry, PersonalInfo
from latex import render_latex


APP_TITLE = "Resume Builder (Template-based)"


def info(msg: str, parent=None):
    QMessageBox.information(parent, APP_TITLE, msg)


def warn(msg: str, parent=None):
    QMessageBox.warning(parent, APP_TITLE, msg)


class Repeater(QWidget):
    """
    A simple repeating section: user can add/remove cards of a certain type.
    You provide:
      - factory() -> object
      - render(item, container_layout) -> list of field widgets or a callable getter
    We keep it practical: each card returns a getter() that rebuilds the item.
    """
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.outer = QVBoxLayout(self)
        self.outer.setContentsMargins(0, 0, 0, 0)
        self.cards_layout = QVBoxLayout()
        self.outer.addLayout(self.cards_layout)
        self.cards = []  # list[tuple[QWidget, callable]]

    def clear(self):
        while self.cards_layout.count():
            it = self.cards_layout.takeAt(0)
            w = it.widget()
            if w:
                w.deleteLater()
        self.cards = []

    def add_card(self, card_widget: QWidget, getter):
        self.cards_layout.addWidget(card_widget)
        self.cards.append((card_widget, getter))

    def remove_card(self, card_widget: QWidget):
        for idx, (w, _) in enumerate(self.cards):
            if w is card_widget:
                self.cards_layout.removeWidget(w)
                w.setParent(None)
                w.deleteLater()
                self.cards.pop(idx)
                return

    def values(self):
        return [g() for _, g in self.cards]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.resize(1100, 720)

        self.data = ResumeData()  # defaults from your resume

        root = QWidget()
        self.setCentralWidget(root)
        main = QVBoxLayout(root)

        # Tabs
        self.tabs = QTabWidget()
        main.addWidget(self.tabs, stretch=1)

        # Bottom export buttons
        btn_row = QHBoxLayout()
        main.addLayout(btn_row)

        self.btn_export_json = QPushButton("Export JSON")
        self.btn_export_tex = QPushButton("Export LaTeX (.tex)")
        self.btn_load_json = QPushButton("Load JSON")

        btn_row.addWidget(self.btn_load_json)
        btn_row.addStretch(1)
        btn_row.addWidget(self.btn_export_json)
        btn_row.addWidget(self.btn_export_tex)

        self.btn_export_json.clicked.connect(self.export_json)
        self.btn_export_tex.clicked.connect(self.export_tex)
        self.btn_load_json.clicked.connect(self.load_json)

        # Build tabs
        self.tab_personal = self._build_personal_tab()
        self.tab_education = self._build_education_tab()
        self.tab_experience = self._build_experience_tab()
        self.tab_skills = self._build_skills_tab()
        self.tab_projects = self._build_projects_tab()
        self.tab_awards = self._build_awards_tab()

        self.tabs.addTab(self.tab_personal, "Personal")
        self.tabs.addTab(self.tab_education, "Education")
        self.tabs.addTab(self.tab_experience, "Work")
        self.tabs.addTab(self.tab_skills, "Skills")
        self.tabs.addTab(self.tab_projects, "Projects")
        self.tabs.addTab(self.tab_awards, "Honors & Awards")

    # ---------- Utilities ----------
    def _wrap_scroll(self, inner: QWidget) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(inner)
        return scroll

    def _groupbox(self, title: str) -> QGroupBox:
        gb = QGroupBox(title)
        gb.setStyleSheet("QGroupBox { font-weight: 600; }")
        return gb

    def gather(self) -> ResumeData:
        # Personal
        self.data.personal = PersonalInfo(
            full_name=self.p_full_name.text().strip(),
            email=self.p_email.text().strip(),
            phone=self.p_phone.text().strip(),
            location=self.p_location.text().strip(),
            portfolio=self.p_portfolio.text().strip(),
            linkedin=self.p_linkedin.text().strip(),
            github=self.p_github.text().strip(),
        )

        # Headings (optional: keep simple)
        # Education
        self.data.education = self.education_rep.values()
        # Experience
        self.data.experience = self.experience_rep.values()
        # Skills
        self.data.skills = self.skills_rep.values()
        # Projects
        self.data.projects = self.projects_rep.values()
        # Awards
        self.data.awards = self.awards_rep.values()

        return self.data

    # ---------- Tabs ----------
    def _build_personal_tab(self) -> QWidget:
        inner = QWidget()
        layout = QVBoxLayout(inner)

        gb = self._groupbox("Your Personal Info")
        form = QFormLayout(gb)

        self.p_full_name = QLineEdit(self.data.personal.full_name)
        self.p_email = QLineEdit(self.data.personal.email)
        self.p_phone = QLineEdit(self.data.personal.phone)
        self.p_location = QLineEdit(self.data.personal.location)
        self.p_portfolio = QLineEdit(self.data.personal.portfolio)
        self.p_linkedin = QLineEdit(self.data.personal.linkedin)
        self.p_github = QLineEdit(self.data.personal.github)

        form.addRow("Full Name", self.p_full_name)
        form.addRow("Email", self.p_email)
        form.addRow("Phone Number", self.p_phone)
        form.addRow("Location", self.p_location)
        form.addRow("Portfolio", self.p_portfolio)
        form.addRow("LinkedIn", self.p_linkedin)
        form.addRow("GitHub", self.p_github)

        layout.addWidget(gb)
        layout.addStretch(1)
        return self._wrap_scroll(inner)

    def _build_education_tab(self) -> QWidget:
        inner = QWidget()
        layout = QVBoxLayout(inner)

        header = QHBoxLayout()
        layout.addLayout(header)
        header.addWidget(QLabel("Education"))
        header.addStretch(1)
        add_btn = QPushButton("Add School")
        header.addWidget(add_btn)

        self.education_rep = Repeater("Education")
        layout.addWidget(self.education_rep)

        def add_card(initial: Optional[EducationEntry] = None):
            e = initial or EducationEntry()
            gb = self._groupbox("School")
            form = QFormLayout(gb)

            school = QLineEdit(e.school_name)
            loc = QLineEdit(e.school_location)
            degree = QLineEdit(e.degree)
            major = QLineEdit(e.major)
            gpa = QLineEdit("" if e.gpa is None else str(e.gpa))
            start = QLineEdit(e.start_date)
            end = QLineEdit(e.end_date)

            form.addRow("School Name", school)
            form.addRow("School Location", loc)
            form.addRow("Degree", degree)
            form.addRow("Major", major)
            form.addRow("GPA (optional)", gpa)
            form.addRow("Start Date", start)
            form.addRow("End Date", end)

            rm = QPushButton("Remove School")
            rm.setStyleSheet("QPushButton { color: #b33; }")

            row = QHBoxLayout()
            row.addStretch(1)
            row.addWidget(rm)
            form.addRow(row)

            def getter() -> EducationEntry:
                g = gpa.text().strip()
                return EducationEntry(
                    school_name=school.text().strip(),
                    school_location=loc.text().strip(),
                    degree=degree.text().strip(),
                    major=major.text().strip(),
                    gpa=g if g else None,
                    start_date=start.text().strip(),
                    end_date=end.text().strip(),
                )

            def remove_this():
                self.education_rep.remove_card(gb)

            rm.clicked.connect(remove_this)
            self.education_rep.add_card(gb, getter)

        add_btn.clicked.connect(lambda: add_card())

        # seed from existing data
        for e in self.data.education:
            add_card(e)

        layout.addStretch(1)
        return self._wrap_scroll(inner)

    def _build_experience_tab(self) -> QWidget:
        inner = QWidget()
        layout = QVBoxLayout(inner)

        header = QHBoxLayout()
        layout.addLayout(header)
        header.addWidget(QLabel("Work Experience"))
        header.addStretch(1)
        add_btn = QPushButton("Add Job")
        header.addWidget(add_btn)

        self.experience_rep = Repeater("Experience")
        layout.addWidget(self.experience_rep)

        def add_card(initial: Optional[ExperienceEntry] = None):
            x = initial or ExperienceEntry()
            gb = self._groupbox("Job")
            form = QFormLayout(gb)

            company = QLineEdit(x.company_name)
            cloc = QLineEdit(x.company_location)
            title = QLineEdit(x.job_title)
            start = QLineEdit(x.start_date)
            end = QLineEdit(x.end_date)

            bullets = QTextEdit("\n".join(x.responsibilities))
            bullets.setPlaceholderText("One bullet per line...")

            form.addRow("Company Name", company)
            form.addRow("Company Location", cloc)
            form.addRow("Job Title", title)
            form.addRow("Start Date", start)
            form.addRow("End Date", end)
            form.addRow("Responsibilities (1 per line)", bullets)

            rm = QPushButton("Remove Job")
            rm.setStyleSheet("QPushButton { color: #b33; }")
            row = QHBoxLayout()
            row.addStretch(1)
            row.addWidget(rm)
            form.addRow(row)

            def getter() -> ExperienceEntry:
                lines = [ln.strip() for ln in bullets.toPlainText().splitlines() if ln.strip()]
                return ExperienceEntry(
                    company_name=company.text().strip(),
                    company_location=cloc.text().strip(),
                    job_title=title.text().strip(),
                    start_date=start.text().strip(),
                    end_date=end.text().strip(),
                    responsibilities=lines,
                )

            def remove_this():
                self.experience_rep.remove_card(gb)

            rm.clicked.connect(remove_this)
            self.experience_rep.add_card(gb, getter)

        add_btn.clicked.connect(lambda: add_card())

        for x in self.data.experience:
            add_card(x)

        layout.addStretch(1)
        return self._wrap_scroll(inner)

    def _build_skills_tab(self) -> QWidget:
        inner = QWidget()
        layout = QVBoxLayout(inner)

        header = QHBoxLayout()
        layout.addLayout(header)
        header.addWidget(QLabel("Skills"))
        header.addStretch(1)
        add_btn = QPushButton("Add Skill Category")
        header.addWidget(add_btn)

        self.skills_rep = Repeater("Skills")
        layout.addWidget(self.skills_rep)

        def add_card(initial: Optional[SkillCategory] = None):
            s = initial or SkillCategory()
            gb = self._groupbox("Skill Category")
            form = QFormLayout(gb)

            name = QLineEdit(s.name)
            details = QTextEdit("\n".join(s.details))
            details.setPlaceholderText("One item per line (will render comma-separated)...")

            form.addRow("Skill Name", name)
            form.addRow("Skill Details (1 per line)", details)

            rm = QPushButton("Remove Category")
            rm.setStyleSheet("QPushButton { color: #b33; }")
            row = QHBoxLayout()
            row.addStretch(1)
            row.addWidget(rm)
            form.addRow(row)

            def getter() -> SkillCategory:
                lines = [ln.strip() for ln in details.toPlainText().splitlines() if ln.strip()]
                return SkillCategory(name=name.text().strip(), details=lines)

            def remove_this():
                self.skills_rep.remove_card(gb)

            rm.clicked.connect(remove_this)
            self.skills_rep.add_card(gb, getter)

        add_btn.clicked.connect(lambda: add_card())

        for s in self.data.skills:
            add_card(s)

        layout.addStretch(1)
        return self._wrap_scroll(inner)

    def _build_projects_tab(self) -> QWidget:
        inner = QWidget()
        layout = QVBoxLayout(inner)

        header = QHBoxLayout()
        layout.addLayout(header)
        header.addWidget(QLabel("Projects"))
        header.addStretch(1)
        add_btn = QPushButton("Add Project")
        header.addWidget(add_btn)

        self.projects_rep = Repeater("Projects")
        layout.addWidget(self.projects_rep)

        def add_card(initial: Optional[ProjectEntry] = None):
            p = initial or ProjectEntry()
            gb = self._groupbox("Project")
            form = QFormLayout(gb)

            name = QLineEdit(p.project_name)
            link = QLineEdit(p.link)
            genre = QLineEdit(p.genre)
            start = QLineEdit(p.start_date)
            end = QLineEdit(p.end_date)

            bullets = QTextEdit("\n".join(p.description_bullets))
            bullets.setPlaceholderText("One bullet per line...")

            tools = QTextEdit("\n".join(p.tools_used))
            tools.setPlaceholderText("One tool per line (optional)...")

            form.addRow("Project Name", name)
            form.addRow("Link", link)
            form.addRow("Type/Genre", genre)
            form.addRow("Start Date", start)
            form.addRow("End Date", end)
            form.addRow("Description (1 per line)", bullets)
            form.addRow("Tools Used (1 per line)", tools)

            rm = QPushButton("Remove Project")
            rm.setStyleSheet("QPushButton { color: #b33; }")
            row = QHBoxLayout()
            row.addStretch(1)
            row.addWidget(rm)
            form.addRow(row)

            def getter() -> ProjectEntry:
                bl = [ln.strip() for ln in bullets.toPlainText().splitlines() if ln.strip()]
                tl = [ln.strip() for ln in tools.toPlainText().splitlines() if ln.strip()]
                return ProjectEntry(
                    project_name=name.text().strip(),
                    link=link.text().strip(),
                    genre=genre.text().strip(),
                    start_date=start.text().strip(),
                    end_date=end.text().strip(),
                    description_bullets=bl,
                    tools_used=tl,
                )

            def remove_this():
                self.projects_rep.remove_card(gb)

            rm.clicked.connect(remove_this)
            self.projects_rep.add_card(gb, getter)

        add_btn.clicked.connect(lambda: add_card())

        for p in self.data.projects:
            add_card(p)

        layout.addStretch(1)
        return self._wrap_scroll(inner)

    def _build_awards_tab(self) -> QWidget:
        inner = QWidget()
        layout = QVBoxLayout(inner)

        header = QHBoxLayout()
        layout.addLayout(header)
        header.addWidget(QLabel("Honors & Awards"))
        header.addStretch(1)
        add_btn = QPushButton("Add Award")
        header.addWidget(add_btn)

        self.awards_rep = Repeater("Awards")
        layout.addWidget(self.awards_rep)

        def add_card(initial: Optional[AwardEntry] = None):
            a = initial or AwardEntry()
            gb = self._groupbox("Award")
            form = QFormLayout(gb)

            name = QLineEdit(a.award_name)
            date = QLineEdit(a.award_date)
            awarder = QLineEdit(a.awarder)
            summary = QLineEdit(a.summary)

            form.addRow("Award Name", name)
            form.addRow("Award Date", date)
            form.addRow("Awarder", awarder)
            form.addRow("Summary", summary)

            rm = QPushButton("Remove Award")
            rm.setStyleSheet("QPushButton { color: #b33; }")
            row = QHBoxLayout()
            row.addStretch(1)
            row.addWidget(rm)
            form.addRow(row)

            def getter() -> AwardEntry:
                return AwardEntry(
                    award_name=name.text().strip(),
                    award_date=date.text().strip(),
                    awarder=awarder.text().strip(),
                    summary=summary.text().strip(),
                )

            def remove_this():
                self.awards_rep.remove_card(gb)

            rm.clicked.connect(remove_this)
            self.awards_rep.add_card(gb, getter)

        add_btn.clicked.connect(lambda: add_card())

        for a in self.data.awards:
            add_card(a)

        layout.addStretch(1)
        return self._wrap_scroll(inner)

    def _rebuild_repeater_from_widgets(self, rep: Repeater):
        """
        When removing a card, easiest safe method is to:
        - scan existing cards, reattach getters in same order
        But we don't have direct card->getter map after deletion.
        So we rebuild by reading the remaining getters from rep.getters
        by filtering alive widgets. For simplicity: we rebuild by re-gathering.
        """
        # No-op approach here: removal already deletes widget;
        # getters list may contain stale getter closures referencing deleted widgets.
        # So we rebuild by forcing user to export/compile via gather(),
        # but to keep correctness we do a simple "refresh":
        # -> rebuild the whole tab from current gathered data when removing.
        self.data = self.gather()

        # Rebuild all tabs except personal (fast enough)
        # NOTE: in a bigger app you'd keep a stable model-binding system.
        self.tabs.clear()
        self.tab_personal = self._build_personal_tab()
        self.tab_education = self._build_education_tab()
        self.tab_experience = self._build_experience_tab()
        self.tab_skills = self._build_skills_tab()
        self.tab_projects = self._build_projects_tab()
        self.tab_awards = self._build_awards_tab()
        self.tabs.addTab(self.tab_personal, "Personal")
        self.tabs.addTab(self.tab_education, "Education")
        self.tabs.addTab(self.tab_experience, "Work")
        self.tabs.addTab(self.tab_skills, "Skills")
        self.tabs.addTab(self.tab_projects, "Projects")
        self.tabs.addTab(self.tab_awards, "Honors & Awards")

    # ---------- Export / Import ----------
    def export_json(self):
        data = self.gather()
        path, _ = QFileDialog.getSaveFileName(self, "Save JSON", "resume.json", "JSON (*.json)")
        if not path:
            return
        Path(path).write_text(data.model_dump_json(indent=2), encoding="utf-8")
        info("Saved JSON.", self)

    def export_tex(self):
        data = self.gather()
        latex_src = render_latex(data)
        path, _ = QFileDialog.getSaveFileName(self, "Save LaTeX", "resume.tex", "LaTeX (*.tex)")
        if not path:
            return
        Path(path).write_text(latex_src, encoding="utf-8")
        info("Saved LaTeX (.tex).", self)

    def load_json(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load JSON", "", "JSON (*.json)")
        if not path:
            return
        try:
            raw = json.loads(Path(path).read_text(encoding="utf-8"))
            self.data = ResumeData.model_validate(raw)
            info("Loaded JSON. Refreshing UI...", self)
            self._rebuild_repeater_from_widgets(self.education_rep)  # triggers rebuild
        except Exception as e:
            warn(f"Could not load JSON: {e}", self)


def main():
    app = QApplication([])
    w = MainWindow()
    w.show()
    app.exec()


if __name__ == "__main__":
    main()