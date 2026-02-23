from pydantic import BaseModel
from typing import List, Optional


class CurriculumRequest(BaseModel):
    course_title: str
    subject_area: str
    education_level: str          # e.g. Undergraduate, Postgraduate, High School
    duration_weeks: int
    target_audience: str
    industry_focus: Optional[str] = ""
    special_requirements: Optional[str] = ""


class LearningOutcome(BaseModel):
    code: str
    description: str
    bloom_level: str              # Remember / Understand / Apply / Analyze / Evaluate / Create


class Topic(BaseModel):
    week: int
    title: str
    subtopics: List[str]
    resources: List[str]
    assessment_type: Optional[str] = ""


class Module(BaseModel):
    module_number: int
    title: str
    description: str
    weeks: List[int]
    topics: List[Topic]
    learning_outcomes: List[str]


class CurriculumResponse(BaseModel):
    course_title: str
    subject_area: str
    education_level: str
    duration_weeks: int
    course_description: str
    learning_outcomes: List[LearningOutcome]
    modules: List[Module]
    recommended_topics: List[str]
    industry_alignment: List[str]
    assessment_strategy: str
    provider: str                 # gemini or ollama
