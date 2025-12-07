"""
Unit tests for BurushaskiTranslator
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Word, Phrase, WordClassEnum
from app.nlp import BurushaskiTranslator


@pytest.fixture
def test_db():
    """Create an in-memory SQLite database for testing"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    # Seed test data
    word1 = Word(
        burushaski="haq",
        english="good",
        urdu="اچھا",
        pronunciation_ipa="hɑq",
        word_class=WordClassEnum.H_CLASS,
        verified=True
    )
    word2 = Word(
        burushaski="mir",
        english="man",
        urdu="آدمی",
        pronunciation_ipa="mir",
        word_class=WordClassEnum.Y_CLASS,
        verified=True
    )
    word3 = Word(
        burushaski="duṣ",
        english="two",
        urdu="دو",
        pronunciation_ipa="duʂ",
        word_class=WordClassEnum.X_CLASS,
        verified=True
    )
    
    phrase1 = Phrase(
        burushaski="haq mir",
        english="good man",
        urdu="اچھا آدمی",
        context="greeting",
        formality="casual",
        verified=True
    )
    
    session.add_all([word1, word2, word3, phrase1])
    session.commit()
    
    yield session
    session.close()


class TestBurushaskiTranslator:
    """Test suite for BurushaskiTranslator"""
    
    def test_translate_burushaski_word(self, test_db):
        """Test translation of a single Burushaski word"""
        translator = BurushaskiTranslator(test_db)
        result = translator.translate("haq", source_lang="burushaski")
        
        assert result["translation"] == "good"
        assert result["source_language"] == "burushaski"
        assert result["target_language"] == "english"
        assert result["method"] in ["ngram_phrase_match", "dictionary"]  # Either method is acceptable
        assert result["confidence"] >= 0.9
    
    def test_translate_english_word(self, test_db):
        """Test translation of a single English word"""
        translator = BurushaskiTranslator(test_db)
        result = translator.translate("good", source_lang="english")
        
        assert result["translation"] == "haq"
        assert result["source_language"] == "english"
        assert result["target_language"] == "burushaski"
        assert result["method"] in ["ngram_phrase_match", "dictionary"]
        assert result["confidence"] >= 0.9
    
    def test_phrase_lookup_burushaski(self, test_db):
        """Test exact phrase lookup for Burushaski"""
        translator = BurushaskiTranslator(test_db)
        result = translator.translate("haq mir", source_lang="burushaski")
        
        assert result["translation"] == "good man"
        assert result["method"] == "phrase_match"
        assert result["confidence"] == 0.95
    
    def test_ngram_translate_multi_word(self, test_db):
        """Test n-gram translation for multi-word input"""
        translator = BurushaskiTranslator(test_db)
        # "mir duṣ" should match individual words via n-gram
        result = translator.translate("mir duṣ", source_lang="burushaski")
        
        # Should find at least one match
        assert result["translation"] is not None
        assert "man" in result["translation"] or "two" in result["translation"] or result["method"] in ["word_by_word", "ngram_phrase_match"]
    
    def test_word_by_word_translate(self, test_db):
        """Test word-by-word translation fallback"""
        translator = BurushaskiTranslator(test_db)
        result = translator.translate("haq mir duṣ", source_lang="burushaski")
        
        # Should translate to something like "good man two"
        assert result["translation"] is not None
        assert result["method"] in ["word_by_word", "ngram_phrase_match"]
        assert result["words_found"] >= 2
    
    def test_unknown_word_returns_suggestions(self, test_db):
        """Test that unknown word returns suggestions"""
        translator = BurushaskiTranslator(test_db)
        result = translator.translate("xyzabc", source_lang="burushaski")
        
        assert result["translation"] is None
        assert result["method"] == "suggestions" or result["method"] == "none"
    
    def test_auto_detect_burushaski(self, test_db):
        """Test auto-detection of Burushaski language"""
        translator = BurushaskiTranslator(test_db)
        detected = translator._detect_language("duṣ")  # "duṣ" has special char
        
        assert detected == "burushaski"
    
    def test_auto_detect_english(self, test_db):
        """Test auto-detection of English language"""
        translator = BurushaskiTranslator(test_db)
        detected = translator._detect_language("hello")
        
        assert detected == "english"
    
    def test_batch_translate(self, test_db):
        """Test batch translation"""
        translator = BurushaskiTranslator(test_db)
        texts = ["haq", "mir", "duṣ"]
        results = translator.batch_translate(texts, source_lang="burushaski")
        
        assert len(results) == 3
        assert results[0]["translation"] == "good"
        assert results[1]["translation"] == "man"
        assert results[2]["translation"] == "two"    
    def test_strip_whitespace(self, test_db):
        """Test that input whitespace is stripped"""
        translator = BurushaskiTranslator(test_db)
        result = translator.translate("  haq  ", source_lang="burushaski")
        
        assert result["translation"] == "good"
    
    def test_case_insensitive_lookup(self, test_db):
        """Test case-insensitive word lookup"""
        translator = BurushaskiTranslator(test_db)
        result = translator.translate("HAQ", source_lang="burushaski")
        
        assert result["translation"] == "good"
