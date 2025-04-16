# Pydantic models for structured data
from pydantic import BaseModel
from typing import List

class ContactInfo(BaseModel):
    first_name: str
    last_name: str
    middle_name: str
    phone_number: str
    email: str
    linkedin: str

class Education(BaseModel):
    degree: str
    year: str
    college: str

class Skills(BaseModel):
    programming_languages: List[str]
    frameworks_libraries: List[str]
    tools_technologies: List[str]

class Experience(BaseModel):
    company_client: str
    job_role: str
    summary_of_responsibilities: str
    place: str
    start_date: str
    end_date: str

class CandidateData(BaseModel):
    contact: ContactInfo
    education: List[Education]
    skills: Skills
    experience: List[Experience]