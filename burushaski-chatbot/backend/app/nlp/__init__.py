"""
Hybrid Translation Engine for Burushaski
Strategy: Dictionary → Rules → AI Fallback
"""
from sqlalchemy.orm import Session
from app.models import Word, Phrase
from typing import Optional, Dict, List
import os

class BurushaskiTranslator:
    def __init__(self, db: Session):
        self.db = db
        
    def translate(self, text: str, source_lang: str = "auto") -> Dict:
        """
        Main translation function
        
        Args:
            text: Text to translate
            source_lang: "burushaski", "english", or "auto"
            
        Returns:
            Dict with translation and metadata
        """
        # Clean and normalize input
        text = text.strip()
        text_lower = text.lower()
        
        # Auto-detect language
        if source_lang == "auto":
            source_lang = self._detect_language(text_lower)
        
        # Strategy 1: Exact phrase match (highest accuracy)
        result = self._phrase_lookup(text_lower, source_lang)
        if result:
            result["method"] = "phrase_match"
            result["confidence"] = 0.95
            return result

        # Strategy 1b: N-gram / phrase segmentation lookup (multi-word matches)
        result = self._ngram_translate(text_lower, source_lang)
        if result:
            result["method"] = "ngram_phrase_match"
            result["confidence"] = 0.92
            return result
        
        # Strategy 2: Dictionary word lookup
        result = self._dictionary_lookup(text_lower, source_lang)
        if result:
            result["method"] = "dictionary"
            result["confidence"] = 0.90
            return result
        
        # Strategy 3: Word-by-word translation
        result = self._word_by_word_translate(text_lower, source_lang)
        if result:
            result["method"] = "word_by_word"
            result["confidence"] = 0.70
            return result
        
        # Strategy 4: Fuzzy search (suggestions)
        suggestions = self._fuzzy_search(text_lower, source_lang)
        if suggestions:
            return {
                "translation": None,
                "source": text,
                "source_language": source_lang,
                "target_language": "english" if source_lang == "burushaski" else "burushaski",
                "method": "suggestions",
                "confidence": 0.0,
                "suggestions": suggestions,
                "message": f"No exact match found. Did you mean one of these?"
            }
        
        # No match found
        return {
            "translation": None,
            "source": text,
            "source_language": source_lang,
            "target_language": "english" if source_lang == "burushaski" else "burushaski",
            "method": "none",
            "confidence": 0.0,
            "message": "Translation not found. This word is not in our dictionary yet."
        }
    
    def _detect_language(self, text: str) -> str:
        """Detect if text is Burushaski or English"""
        # Burushaski special characters
        burushaski_chars = ['ć', 'ṣ', 'ṭ', 'ẓ', 'ś', 'ŋ', 'é', 'í', 'ó', 'ú']
        
        for char in burushaski_chars:
            if char in text:
                return "burushaski"
        
        # Check in database
        word_check = self.db.query(Word).filter(
            Word.burushaski.ilike(text)
        ).first()
        if word_check:
            return "burushaski"
        
        # Default to English
        return "english"
    
    def _phrase_lookup(self, text: str, source_lang: str) -> Optional[Dict]:
        """Look up exact phrase"""
        if source_lang == "burushaski":
            phrase = self.db.query(Phrase).filter(
                Phrase.burushaski.ilike(text)
            ).first()
            if phrase:
                return {
                    "translation": phrase.english,
                    "source": text,
                    "source_language": "burushaski",
                    "target_language": "english",
                    "urdu": phrase.urdu,
                    "context": phrase.context,
                    "formality": phrase.formality,
                    "audio": phrase.audio_file
                }
        else:
            phrase = self.db.query(Phrase).filter(
                Phrase.english.ilike(text)
            ).first()
            if phrase:
                return {
                    "translation": phrase.burushaski,
                    "source": text,
                    "source_language": "english",
                    "target_language": "burushaski",
                    "urdu": phrase.urdu,
                    "context": phrase.context,
                    "formality": phrase.formality,
                    "audio": phrase.audio_file
                }
        return None
    
    def _ngram_translate(self, text: str, source_lang: str, max_ngram: int = 5) -> Optional[Dict]:
        """Attempt longest n-gram matching across Phrase and Word tables.
        Scans the input left-to-right and prefers the longest match at each position.
        Returns a translation dict similar to other strategies or None if nothing found.
        """
        tokens = text.split()
        if not tokens:
            return None

        n_tokens = len(tokens)
        max_n = min(max_ngram, n_tokens)

        out_tokens = []
        i = 0
        words_found = 0

        while i < n_tokens:
            matched = False
            # try longest span first
            for n in range(max_n, 0, -1):
                if i + n > n_tokens:
                    continue
                chunk = " ".join(tokens[i:i+n])

                if source_lang == "burushaski":
                    # phrase match first
                    phrase = self.db.query(Phrase).filter(Phrase.burushaski.ilike(chunk)).first()
                    if phrase:
                        out_tokens.append(phrase.english)
                        words_found += n
                        i += n
                        matched = True
                        break

                    # then single-word dictionary match (use when chunk length==1)
                    if n == 1:
                        word = self.db.query(Word).filter(Word.burushaski.ilike(chunk)).first()
                        if word:
                            out_tokens.append(word.english)
                            words_found += 1
                            i += 1
                            matched = True
                            break
                else:
                    phrase = self.db.query(Phrase).filter(Phrase.english.ilike(chunk)).first()
                    if phrase:
                        out_tokens.append(phrase.burushaski)
                        words_found += n
                        i += n
                        matched = True
                        break

                    if n == 1:
                        word = self.db.query(Word).filter(Word.english.ilike(chunk)).first()
                        if word:
                            out_tokens.append(word.burushaski)
                            words_found += 1
                            i += 1
                            matched = True
                            break

            if not matched:
                # no multi-word or single-word match: mark as unknown and advance one token
                out_tokens.append(f"[{tokens[i]}]")
                i += 1

        if words_found == 0:
            return None

        return {
            "translation": " ".join(out_tokens),
            "source": text,
            "source_language": source_lang,
            "target_language": "english" if source_lang == "burushaski" else "burushaski",
            "words_found": words_found,
            "total_words": n_tokens,
            "note": "⚠️ N-gram phrase-based translation. Grammar may be approximate. Unknown tokens in [brackets]."
        }
    
    def _dictionary_lookup(self, text: str, source_lang: str) -> Optional[Dict]:
        """Look up single word in dictionary"""
        if source_lang == "burushaski":
            word = self.db.query(Word).filter(
                Word.burushaski.ilike(text)
            ).first()
            if word:
                return {
                    "translation": word.english,
                    "source": text,
                    "source_language": "burushaski",
                    "target_language": "english",
                    "urdu": word.urdu,
                    "pronunciation": word.pronunciation_ipa,
                    "word_class": word.word_class.value if word.word_class else None,
                    "example": word.example_sentence,
                    "example_translation": word.example_translation,
                    "audio": word.audio_file,
                    "notes": word.notes
                }
        else:
            word = self.db.query(Word).filter(
                Word.english.ilike(text)
            ).first()
            if word:
                return {
                    "translation": word.burushaski,
                    "source": text,
                    "source_language": "english",
                    "target_language": "burushaski",
                    "urdu": word.urdu,
                    "pronunciation": word.pronunciation_ipa,
                    "word_class": word.word_class.value if word.word_class else None,
                    "example": word.example_sentence,
                    "example_translation": word.example_translation,
                    "audio": word.audio_file,
                    "notes": word.notes
                }
        return None
    
    def _word_by_word_translate(self, text: str, source_lang: str) -> Optional[Dict]:
        """Translate sentence word by word"""
        words = text.split()
        if len(words) <= 1:
            return None
        
        translations = []
        found_count = 0
        
        for word in words:
            # Remove punctuation
            word_clean = word.strip('.,!?;:')
            result = self._dictionary_lookup(word_clean, source_lang)
            
            if result:
                translations.append(result["translation"])
                found_count += 1
            else:
                translations.append(f"[{word_clean}]")
        
        # Only return if we found at least 50% of words
        if found_count >= len(words) / 2:
            return {
                "translation": " ".join(translations),
                "source": text,
                "source_language": source_lang,
                "target_language": "english" if source_lang == "burushaski" else "burushaski",
                "words_found": found_count,
                "total_words": len(words),
                "note": "⚠️ Word-by-word translation. Grammar may not be perfect. Words in [brackets] not found."
            }
        return None
    
    def _fuzzy_search(self, text: str, source_lang: str, limit: int = 5) -> List[Dict]:
        """Find similar words for suggestions"""
        search_term = f"%{text}%"
        
        if source_lang == "burushaski":
            words = self.db.query(Word).filter(
                Word.burushaski.ilike(search_term)
            ).limit(limit).all()
        else:
            words = self.db.query(Word).filter(
                Word.english.ilike(search_term)
            ).limit(limit).all()
        
        return [
            {
                "burushaski": w.burushaski,
                "english": w.english,
                "pronunciation": w.pronunciation_ipa
            }
            for w in words
        ]
    
    def batch_translate(self, texts: List[str], source_lang: str = "auto") -> List[Dict]:
        """Translate multiple texts at once"""
        results = []
        for text in texts:
            result = self.translate(text, source_lang)
            results.append(result)
        return results
