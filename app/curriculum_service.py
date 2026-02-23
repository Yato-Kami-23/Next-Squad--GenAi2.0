import logging
from app.ai_client import AIClient
from app.schemas import CurriculumRequest, CurriculumResponse

logger = logging.getLogger(__name__)
client = AIClient()


def build_prompt(req: CurriculumRequest) -> str:
    return f"""
You are an expert curriculum designer and education specialist. 
Generate a comprehensive, industry-aligned curriculum based on the following requirements.

COURSE DETAILS:
- Title: {req.course_title}
- Subject Area: {req.subject_area}
- Education Level: {req.education_level}
- Duration: {req.duration_weeks} weeks
- Target Audience: {req.target_audience}
- Industry Focus: {req.industry_focus or "General"}
- Special Requirements: {req.special_requirements or "None"}

OUTPUT FORMAT:
Return ONLY valid JSON matching this exact structure (no markdown, no explanation):

{{
  "course_title": "{req.course_title}",
  "subject_area": "{req.subject_area}",
  "education_level": "{req.education_level}",
  "duration_weeks": {req.duration_weeks},
  "course_description": "2-3 sentence overview of the course",
  "learning_outcomes": [
    {{
      "code": "LO1",
      "description": "Clear, measurable outcome statement",
      "bloom_level": "Apply"
    }}
  ],
  "modules": [
    {{
      "module_number": 1,
      "title": "Module title",
      "description": "What this module covers",
      "weeks": [1, 2],
      "topics": [
        {{
          "week": 1,
          "title": "Topic title",
          "subtopics": ["subtopic 1", "subtopic 2", "subtopic 3"],
          "resources": ["Textbook chapter", "Online resource", "Tool/Lab"],
          "assessment_type": "Quiz / Assignment / Lab / Project"
        }}
      ],
      "learning_outcomes": ["LO1", "LO2"]
    }}
  ],
  "recommended_topics": ["Additional topic 1", "Additional topic 2", "Additional topic 3"],
  "industry_alignment": ["Skill/technology aligned with industry 1", "Skill 2", "Skill 3"],
  "assessment_strategy": "Description of overall assessment approach"
}}

REQUIREMENTS:
- Generate {max(3, req.duration_weeks // 3)} modules covering all {req.duration_weeks} weeks
- Generate at least 6 learning outcomes using Bloom's Taxonomy levels
- Each module must have one topic per week it covers
- Make content specific, practical, and industry-relevant
- Align with current {req.industry_focus or req.subject_area} industry standards
"""


def generate_curriculum(req: CurriculumRequest) -> dict:
    prompt = build_prompt(req)
    result = client.generate(prompt)

    if not result["success"]:
        return {"success": False, "error": result["error"]}

    parsed = client.parse_json_response(result["response"])
    if not parsed:
        logger.error("Failed to parse JSON from AI response.")
        return {"success": False, "error": "AI returned invalid JSON. Try again."}

    parsed["provider"] = result.get("provider", "unknown")

    try:
        curriculum = CurriculumResponse(**parsed)
        return {"success": True, "data": curriculum.model_dump()}
    except Exception as e:
        logger.error(f"Schema validation error: {e}")
        # Return raw parsed data even if schema validation fails
        return {"success": True, "data": parsed}
