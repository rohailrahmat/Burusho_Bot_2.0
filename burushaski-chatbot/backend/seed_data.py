from app.db.database import SessionLocal, Base, engine
from app.models import Word, DialectEnum, WordClassEnum


def seed_words():
    # Ensure tables are created (works for SQLite and other DBs)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    sample_words = [
        {
            "burushaski": "be bila?",
            "english": "How are you?",
            "urdu": "آپ کیسے ہیں؟",
            "dialect": DialectEnum.HUNZA,
            "pronunciation_ipa": "be bila",
            "notes": "Informal greeting"
        },
        {
            "burushaski": "áa",
            "english": "yes",
            "urdu": "ہاں",
            "dialect": DialectEnum.HUNZA,
            "pronunciation_ipa": "aː"
        },
        {
            "burushaski": "béé",
            "english": "no",
            "urdu": "نہیں",
            "dialect": DialectEnum.HUNZA,
            "pronunciation_ipa": "beː"
        },
        {
            "burushaski": "ćo",
            "english": "water",
            "urdu": "پانی",
            "word_class": WordClassEnum.Y_CLASS,
            "dialect": DialectEnum.HUNZA,
            "pronunciation_ipa": "tʃo",
            "example_sentence": "a ćo guséṭam",
            "example_translation": "I drink water"
        },
        {
            "burushaski": "harís",
            "english": "bread",
            "urdu": "روٹی",
            "word_class": WordClassEnum.X_CLASS,
            "dialect": DialectEnum.HUNZA,
            "pronunciation_ipa": "haris"
        },
        {
            "burushaski": "hík",
            "english": "one",
            "urdu": "ایک",
            "dialect": DialectEnum.HUNZA,
            "pronunciation_ipa": "hik"
        },
        {
            "burushaski": "altó",
            "english": "two",
            "urdu": "دو",
            "dialect": DialectEnum.HUNZA,
            "pronunciation_ipa": "alto"
        },
        {
            "burushaski": "thili",
            "english": "thank you",
            "urdu": "شکریہ",
            "dialect": DialectEnum.HUNZA,
            "pronunciation_ipa": "θili"
        },
    ]
    
    for word_data in sample_words:
        existing = db.query(Word).filter(Word.burushaski == word_data["burushaski"]).first()
        if not existing:
            word = Word(**word_data, verified=True)
            db.add(word)
            print(f"✅ Added: {word_data['burushaski']} = {word_data['english']}")
    
    db.commit()
    print(f"\n✅ Seeded {len(sample_words)} words!")
    db.close()

if __name__ == "__main__":
    print("🌱 Seeding database...\n")
    seed_words()
    print("\n🎉 Done!")
