
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(
    title="Burushaski Language Preservation API",
    description="AI-powered chatbot for Burushaski language learning",
    version="0.1.0"
)

origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Burushaski Language Preservation API",
        "status": "running",
        "version": "0.1.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# include API routers
from app.api import dictionary, translate  # noqa: E402

app.include_router(dictionary.router, prefix="/api/dictionary", tags=["dictionary"])
app.include_router(translate.router, prefix="/api/translate", tags=["translate"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)