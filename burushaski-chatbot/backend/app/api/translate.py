

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from app.db.database import get_db
from app.nlp import BurushaskiTranslator
from typing import Optional, List

router = APIRouter()

class TranslationRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)
    source_language: str = Field(default="auto", pattern="^(auto|burushaski|english)$")

class BatchTranslationRequest(BaseModel):
    texts: List[str] = Field(..., min_length=1, max_length=50)
    source_lang: str = Field(default="auto", pattern="^(auto|burushaski|english)$")

class TranslationResponse(BaseModel):
    translation: Optional[str]
    source: str
    source_language: str
    target_language: str
    method: str
    confidence: float
    urdu: Optional[str] = None
    pronunciation: Optional[str] = None
    audio: Optional[str] = None
    example: Optional[str] = None
    note: Optional[str] = None
    message: Optional[str] = None
    suggestions: Optional[List[dict]] = None

@router.post("/", response_model=TranslationResponse)
def translate_text(
    request: TranslationRequest,
    db: Session = Depends(get_db)
):
    """
    **Translate text between Burushaski and English**
    
    The translator uses multiple strategies:
    1. Exact phrase match (95% confidence)
    2. Dictionary lookup (90% confidence)
    3. Word-by-word translation (70% confidence)
    4. Fuzzy suggestions (0% confidence, provides alternatives)
    
    **Parameters:**
    - **text**: The text to translate (1-500 characters)
    - **source_language**: 
        - "auto" - Automatic detection (default)
        - "burushaski" - Source is Burushaski
        - "english" - Source is English
    
    **Returns:** Translation with confidence score and metadata
    """
    translator = BurushaskiTranslator(db)
    result = translator.translate(request.text, request.source_language)
    return result

@router.get("/quick/{text}")
def quick_translate(
    text: str,
    source: str = Query("auto", pattern="^(auto|burushaski|english)$"),
    db: Session = Depends(get_db)
):
    """
    Quick translation via GET request
    Useful for simple lookups and browser testing
    
    Example: /api/translate/quick/water?source=english
    """
    translator = BurushaskiTranslator(db)
    result = translator.translate(text, source)
    return result

@router.post("/batch")
def batch_translate(
    request: BatchTranslationRequest,
    db: Session = Depends(get_db)
):
    """
    Translate multiple texts at once
    Maximum 50 texts per request
    
    Useful for:
    - Translating documents
    - Bulk word lists
    - Lesson content
    """
    translator = BurushaskiTranslator(db)
    results = translator.batch_translate(request.texts, request.source_lang)
    
    return {
        "total": len(results),
        "successful": len([r for r in results if r["translation"]]),
        "failed": len([r for r in results if not r["translation"]]),
        "results": results
    }

@router.get("/examples")
def get_translation_examples(
    word: Optional[str] = None,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Get example translations
    Useful for learning and documentation
    """
    from app.models import Phrase
    
    query = db.query(Phrase)
    if word:
        query = query.filter((Phrase.burushaski.ilike(f"%{word}%")) | (Phrase.english.ilike(f"%{word}%")))
    
    phrases = query.limit(limit).all()
    
    return {
        "count": len(phrases),
        "examples": [
            {
                "burushaski": p.burushaski,
                "english": p.english,
                "urdu": p.urdu,
                "context": p.context,
                "formality": p.formality
            }
            for p in phrases
        ]
    }

