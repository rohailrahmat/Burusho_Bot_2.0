"""
API-level tests for translation endpoints
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.models import Base, Word, Phrase
from app.db.database import get_db


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
        word_class="adjective",
        verified=True
    )
    word2 = Word(
        burushaski="mir",
        english="man",
        urdu="آدمی",
        pronunciation_ipa="mir",
        word_class="noun",
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
    
    session.add_all([word1, word2, phrase1])
    session.commit()
    
    yield session
    session.close()


@pytest.fixture
def client(test_db):
    """Create a test client with test database"""
    def override_get_db():
        yield test_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


class TestTranslateAPI:
    """Test suite for translate API endpoints"""
    
    def test_translate_text_endpoint(self, client):
        """Test POST /api/translate"""
        response = client.post(
            "/api/translate/",
            json={"text": "haq", "source_language": "burushaski"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["translation"] == "good"
        assert data["source_language"] == "burushaski"
        assert data["target_language"] == "english"
    
    def test_quick_translate_endpoint(self, client):
        """Test GET /api/translate/quick/{text}"""
        response = client.get("/api/translate/quick/mir?source=burushaski")
        
        assert response.status_code == 200
        data = response.json()
        assert data["translation"] == "man"
    
    def test_batch_translate_endpoint(self, client):
        """Test POST /api/translate/batch"""
        response = client.post(
            "/api/translate/batch",
            json={"texts": ["haq", "mir"], "source_lang": "burushaski"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 2
        assert data["results"][0]["translation"] == "good"
        assert data["results"][1]["translation"] == "man"    
    def test_phrase_match_in_translate(self, client):
        """Test that phrase matches return highest confidence"""
        response = client.post(
            "/api/translate/",
            json={"text": "haq mir", "source_language": "burushaski"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["translation"] == "good man"
        assert data["method"] == "phrase_match"
        assert data["confidence"] == 0.95
    
    def test_auto_detect_language(self, client):
        """Test automatic language detection"""
        response = client.post(
            "/api/translate/",
            json={"text": "haq"}  # no source_language specified
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["translation"] is not None or data["method"] in ["suggestions", "none"]
    
    def test_invalid_request_missing_text(self, client):
        """Test that missing text parameter returns error"""
        response = client.post(
            "/api/translate/",
            json={"source_language": "burushaski"}
        )
        
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_empty_text(self, client):
        """Test handling of empty text"""
        response = client.post(
            "/api/translate/",
            json={"text": "", "source_language": "burushaski"}
        )
        
        assert response.status_code == 422  # Validation error due to min_length=1
    
    def test_whitespace_handling(self, client):
        """Test that leading/trailing whitespace is handled"""
        response = client.post(
            "/api/translate/",
            json={"text": "  haq  ", "source_language": "burushaski"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["translation"] == "good"
    
    def test_case_insensitivity(self, client):
        """Test case-insensitive translation"""
        response = client.post(
            "/api/translate/",
            json={"text": "HAQ", "source_language": "burushaski"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["translation"] == "good"
    
    def test_translation_examples_endpoint(self, client):
        """Test GET /api/translate/examples"""
        response = client.get("/api/translate/examples")
        
        assert response.status_code == 200
        data = response.json()
        # Response should include examples or an empty list
        assert isinstance(data, dict)
        assert "count" in data or isinstance(data, list)
