# CariPath 🎓
**Generative AI–Powered Curriculum Design System**

---

## Project Structure
```
curricuforge/
├── app/
│   ├── __init__.py           # FastAPI app factory
│   ├── routes.py             # API endpoints
│   ├── ai_client.py          # Gemini + Ollama hybrid client
│   ├── curriculum_service.py # Prompt builder & generation logic
│   ├── pdf_generator.py      # ReportLab PDF generation
│   ├── schemas.py            # Pydantic models
│   └── templates/
│       └── index.html        # Frontend dashboard
├── config/
│   ├── __init__.py
│   └── settings.py           # Environment config
├── tests/
│   └── test_basic.py
├── .env.example
├── main.py                   # Entry point
└── requirements.txt
```

---

## Setup

### 1. Create virtual environment
```bash
python -m venv venv
source venv/Scripts/activate   # Git Bash on Windows
# or
venv\Scripts\activate          # PowerShell
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment
```bash
cp .env.example .env
```
Edit `.env` and add your **Gemini API key**:
```
GEMINI_API_KEY=your_actual_key_here
```
Get a free key at: https://aistudio.google.com/app/apikey

### 4. (Optional) Pull Ollama fallback model
```bash
ollama pull granite3.3:8b
```

### 5. Run the app
```bash
python main.py
```
Open: http://localhost:8000

---

## API Endpoints

| Method | Endpoint            | Description                  |
|--------|---------------------|------------------------------|
| GET    | `/`                 | Dashboard UI                 |
| GET    | `/health`           | AI provider status           |
| POST   | `/api/generate`     | Generate curriculum (JSON)   |
| POST   | `/api/download-pdf` | Generate + download PDF      |

---

## AI Model Recommendation

| Model              | Use Case                        | Quality  |
|--------------------|---------------------------------|----------|
| Gemini 1.5 Flash   | Primary (cloud, free tier)      | ⭐⭐⭐⭐⭐  |
| granite3.3:8b      | Fallback (local, offline)       | ⭐⭐⭐⭐   |
| granite3.3:2b      | Emergency fallback only         | ⭐⭐      |

`granite3.3:2b` is too small for rich curriculum generation. Use `8b` or `Gemini`.
