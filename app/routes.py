import logging
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import io

from app.schemas import CurriculumRequest
from app.curriculum_service import generate_curriculum
from app.pdf_generator import generate_pdf
from app.ai_client import AIClient

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
ai_client = AIClient()


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/health")
async def health():
    return {"status": "ok", "ai_providers": ai_client.health()}


@router.post("/api/generate")
async def generate(req: CurriculumRequest):
    logger.info(f"Generating curriculum for: {req.course_title}")
    result = generate_curriculum(req)

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])

    return JSONResponse(content=result["data"])


@router.post("/api/download-pdf")
async def download_pdf(req: CurriculumRequest):
    result = generate_curriculum(req)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])

    pdf_bytes = generate_pdf(result["data"])
    filename = req.course_title.replace(" ", "_") + "_Curriculum.pdf"

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
