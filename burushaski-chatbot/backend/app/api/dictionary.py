from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.db.database import get_db
from app.models import Word, WordClassEnum, DialectEnum

router = APIRouter()

# Pydantic schemas
class WordBase(BaseModel):
    burushaski: str
    english: str
    urdu: Optional[str] = None
    word_class: Optional[WordClassEnum] = None
    dialect: DialectEnum = DialectEnum.HUNZA
    pronunciation_ipa: Optional[str] = None
    audio_file: Optional[str] = None
    example_sentence: Optional[str] = None
    example_translation: Optional[str] = None
    notes: Optional[str] = None

class WordCreate(WordBase):
    pass

class WordResponse(WordBase):
    id: int
    verified: bool
    
    class Config:
        from_attributes = True

# GET all words with search and pagination
@router.get("/", response_model=List[WordResponse])
def get_words(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = None,
    dialect: Optional[DialectEnum] = None,
    db: Session = Depends(get_db)
):
    """
    Get all words from dictionary
    
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum records to return (max 500)
    - **search**: Search in Burushaski, English, or Urdu
    - **dialect**: Filter by dialect (hunza, nagar, yasin)
    """
    query = db.query(Word)
    
    # Apply filters
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Word.burushaski.ilike(search_term)) |
            (Word.english.ilike(search_term)) |
            (Word.urdu.ilike(search_term))
        )
    
    if dialect:
        query = query.filter(Word.dialect == dialect)
    
    # Execute query
    words = query.offset(skip).limit(limit).all()
    return words

# GET total count
@router.get("/count")
def get_word_count(
    search: Optional[str] = None,
    dialect: Optional[DialectEnum] = None,
    db: Session = Depends(get_db)
):
    """Get total number of words in dictionary"""
    query = db.query(Word)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Word.burushaski.ilike(search_term)) |
            (Word.english.ilike(search_term))
        )
    
    if dialect:
        query = query.filter(Word.dialect == dialect)
    
    count = query.count()
    return {"total": count}

# GET single word by ID
@router.get("/{word_id}", response_model=WordResponse)
def get_word(word_id: int, db: Session = Depends(get_db)):
    """Get a specific word by ID"""
    word = db.query(Word).filter(Word.id == word_id).first()
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")
    return word

# POST create new word
@router.post("/", response_model=WordResponse, status_code=201)
def create_word(word: WordCreate, db: Session = Depends(get_db)):
    """Add a new word to dictionary"""
    
    # Check if word already exists
    existing = db.query(Word).filter(Word.burushaski == word.burushaski).first()
    if existing:
        raise HTTPException(
            status_code=400, 
            detail=f"Word '{word.burushaski}' already exists"
        )
    
    # Create new word
    db_word = Word(**word.dict())
    db.add(db_word)
    db.commit()
    db.refresh(db_word)
    return db_word

# PUT update word
@router.put("/{word_id}", response_model=WordResponse)
def update_word(word_id: int, word: WordCreate, db: Session = Depends(get_db)):
    """Update an existing word"""
    db_word = db.query(Word).filter(Word.id == word_id).first()
    if not db_word:
        raise HTTPException(status_code=404, detail="Word not found")
    
    # Update fields
    for key, value in word.dict().items():
        setattr(db_word, key, value)
    
    db.commit()
    db.refresh(db_word)
    return db_word

# DELETE word
@router.delete("/{word_id}")
def delete_word(word_id: int, db: Session = Depends(get_db)):
    """Delete a word"""
    word = db.query(Word).filter(Word.id == word_id).first()
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")
    
    db.delete(word)
    db.commit()
    return {"message": "Word deleted successfully", "id": word_id}

# Search with suggestions
@router.get("/search/suggest")
def search_suggest(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Search with suggestions for autocomplete
    Returns partial matches
    """
    search_term = f"%{q}%"
    words = db.query(Word).filter(
        (Word.burushaski.ilike(search_term)) |
        (Word.english.ilike(search_term))
    ).limit(limit).all()
    
    return {
        "query": q,
        "count": len(words),
        "suggestions": [
            {
                "id": w.id,
                "burushaski": w.burushaski,
                "english": w.english,
                "pronunciation": w.pronunciation_ipa
            }
            for w in words
        ]
    }

# Random word (for learning feature)
@router.get("/random/word", response_model=WordResponse)
def get_random_word(db: Session = Depends(get_db)):
    """Get a random word for practice"""
    from sqlalchemy.sql.expression import func
    word = db.query(Word).order_by(func.random()).first()
    if not word:
        raise HTTPException(status_code=404, detail="No words in database")
    return word

# Statistics
@router.get("/stats/overview")
def get_statistics(db: Session = Depends(get_db)):
    """Get dictionary statistics"""
    total_words = db.query(Word).count()
    verified_words = db.query(Word).filter(Word.verified == True).count()
    words_with_audio = db.query(Word).filter(Word.audio_file.isnot(None)).count()
    
    # Count by dialect
    hunza_count = db.query(Word).filter(Word.dialect == DialectEnum.HUNZA).count()
    nagar_count = db.query(Word).filter(Word.dialect == DialectEnum.NAGAR).count()
    yasin_count = db.query(Word).filter(Word.dialect == DialectEnum.YASIN).count()
    
    return {
        "total_words": total_words,
        "verified_words": verified_words,
        "words_with_audio": words_with_audio,
        "by_dialect": {
            "hunza": hunza_count,
            "nagar": nagar_count,
            "yasin": yasin_count
        },
        "completion_percentage": round((verified_words / total_words * 100) if total_words > 0 else 0, 2)
    }
