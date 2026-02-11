from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field


class PersonalInfo(BaseModel):
    full_name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    portfolio: str = ""
    linkedin: str = ""
    github: str = ""


class EducationEntry(BaseModel):
    school_name: str = ""
    school_location: str = ""
    degree: str = ""
    major: str = ""
    gpa: Optional[str] = None
    start_date: str = ""
    end_date: str = ""


class ExperienceEntry(BaseModel):
    company_name: str = ""
    company_location: str = ""
    job_title: str = ""
    start_date: str = ""
    end_date: str = ""
    responsibilities: List[str] = Field(default_factory=list)


class SkillCategory(BaseModel):
    name: str = ""
    details: List[str] = Field(default_factory=list)


class ProjectEntry(BaseModel):
    project_name: str = ""
    link: str = ""
    genre: str = ""
    start_date: str = ""
    end_date: str = ""
    description_bullets: List[str] = Field(default_factory=list)
    tools_used: List[str] = Field(default_factory=list)


class AwardEntry(BaseModel):
    award_name: str = ""
    award_date: str = ""
    awarder: str = ""
    summary: str = ""


class ResumeData(BaseModel):
    # Section headings (like your UI)
    section_personal: str = "Your Personal Info"
    section_education: str = "Education"
    section_experience: str = "Work Experience"
    section_skills: str = "Skills"
    section_projects: str = "Selected Projects"
    section_awards: str = "Awards and Honors"

    personal: PersonalInfo = Field(default_factory=PersonalInfo)
    education: List[EducationEntry] = Field(default_factory=list)
    experience: List[ExperienceEntry] = Field(default_factory=list)
    skills: List[SkillCategory] = Field(default_factory=list)
    projects: List[ProjectEntry] = Field(default_factory=list)
    awards: List[AwardEntry] = Field(default_factory=list)