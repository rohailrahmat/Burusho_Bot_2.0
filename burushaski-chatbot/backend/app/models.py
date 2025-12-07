from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum

class DialectEnum(str, enum.Enum):
    HUNZA = "hunza"
    NAGAR = "nagar"
    YASIN = "yasin"

class WordClassEnum(str, enum.Enum):
    H_CLASS = "h-class"
    Y_CLASS = "y-class"
    X_CLASS = "x-class"

class Word(Base):
    __tablename__ = "words"
    
    id = Column(Integer, primary_key=True, index=True)
    burushaski = Column(String(200), unique=True, index=True, nullable=False)
    english = Column(String(200), nullable=False)
    urdu = Column(String(200))
    word_class = Column(Enum(WordClassEnum))
    dialect = Column(Enum(DialectEnum), default=DialectEnum.HUNZA)
    pronunciation_ipa = Column(String(200))
    audio_file = Column(String(500))
    example_sentence = Column(Text)
    example_translation = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    verified = Column(Boolean, default=False)

class Phrase(Base):
    __tablename__ = "phrases"
    
    id = Column(Integer, primary_key=True, index=True)
    burushaski = Column(Text, nullable=False)
    english = Column(Text, nullable=False)
    urdu = Column(Text)
    context = Column(String(100))
    formality = Column(String(50))
    dialect = Column(Enum(DialectEnum), default=DialectEnum.HUNZA)
    audio_file = Column(String(500))
    usage_notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    verified = Column(Boolean, default=False)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(200))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
