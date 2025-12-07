from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(
    title="Burushaski Language Preservation API",
    description="AI-powered chatbot for Burushaski language learning and preservation",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers
from app.api import dictionary, translate

# Include routers
app.include_router(dictionary.router, prefix="/api/dictionary", tags=["📚 Dictionary"])
app.include_router(translate.router, prefix="/api/translate", tags=["🔄 Translation"])

@app.get("/", tags=["🏠 Home"])
async def root():
    return {
        "message": "🏔️ Burushaski Language Preservation API",
        "status": "✅ running",
        "version": "0.1.0",
        "description": "Preserving the Burushaski language through technology",
        "endpoints": {
            "documentation": "/docs",
            "dictionary": "/api/dictionary",
            "translation": "/api/translate",
            "health": "/health"
        },
        "stats": {
            "languages_supported": ["Burushaski", "English", "Urdu"],
            "dialects": ["Hunza", "Nagar", "Yasin"]
        }
    }

@app.get("/health", tags=["🏠 Home"])
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "api": "operational"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
