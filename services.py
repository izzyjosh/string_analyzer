from typing import Annotated

from sqlalchemy import select
from sqlalchemy.orm import Session
from utils import freq_chars, hash_word, num_unique_cha, palindrom, num_words
from schema import AnalyzeSchema, StringFilters
from database import get_db
from fastapi import Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from models import WordFeature
from typing import List, Dict

class AnalyzerService:

    def __init__(self):
        # Define patterns and their corresponding filters
        self.rules = [
            {
                "match": "all single word palindromic strings",
                "filters": {"word_count": 1, "is_palindrome": True},
            },
            {
                "match": "strings longer than 10 characters",
                "filters": {"min_length": 11},
            },
            {
                "match": "palindromic strings that contain the first vowel",
                "filters": {"is_palindrome": True, "contains_character": "a"},
            },
            {
                "match": "strings containing the letter z",
                "filters": {"contains_character": "z"},
            },
        ]


    def analyze(self, data: AnalyzeSchema, db: Session):

        phrase = data.value

        existing = db.scalars(select(WordFeature).where(WordFeature.phrase == phrase)).first()

        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already exists in the database")

        pal = palindrom(phrase)
        word_len = num_words(phrase)
        len_unique_cha = num_unique_cha(phrase)
        word_hash = hash_word(phrase)
        char_freq = freq_chars(phrase)
        length_word = len(phrase)


        word_feature = WordFeature(phrase=phrase, length=length_word, palindrome=pal, num_words=word_len, num_unique_cha=len_unique_cha, freq_cha=char_freq, hashed=word_hash)

        db.add(word_feature)
        db.commit()
        db.refresh(word_feature)

        response = self.analyzer_response(word_feature)

        return jsonable_encoder(response)


    def get_one(self, id: str, db: Session):
        word_feature = db.scalars(select(WordFeature).where(WordFeature.phrase == id)).first()

        if not word_feature:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Does not exist")

        response = self.analyzer_response(word_feature)

        return jsonable_encoder(response)


    def get_all(self, filters: StringFilters, db: Session):

        stmt = select(WordFeature)

        conditions = []

        if filters.is_palindrome is not None:
            conditions.append(WordFeature.palindrome == filters.is_palindrome)
        if filters.min_length is not None:
            conditions.append(WordFeature.length >= filters.min_length)
        if filters.max_length is not None:
            conditions.append(WordFeature.length <= filters.max_length)
        if filters.word_count is not None:
            conditions.append(WordFeature.num_words == filters.word_count)
        if filters.contains_character is not None:
            conditions.append(WordFeature.phrase.ilike(f"%{filters.contains_character}%"))

        if conditions:
            stmt = stmt.where(*conditions)

        results = db.scalars(stmt).all()

        data = [self.analyzer_response(item) for item in results]

        response = {
                "data": data,
                "count": len(data),
                "filters_applied": {k: v for k, v in filters.model_dump().items() if v is not None},
                }

        return response


    def analyzer_response(self, word_feature):

        response = {
                "id": word_feature.hashed,
                "value": word_feature.phrase,
                "properties": {
                    "length": word_feature.length,
                    "is_palindrome": word_feature.palindrome,
                    "unique_characters": word_feature.num_unique_cha,
                    "word_count": word_feature.num_words,
                    "sha256_hash": word_feature.hashed,
                    "character_frequency_map": word_feature.freq_cha
                    },
                "created_at": word_feature.created_at.strftime("%Y-%m-%dT%H:%M:%SZ")
                }

        return response


    def parse_query(self, query: str) -> Dict:
        query = query.lower().strip()

        for rule in self.rules:
            if rule["match"] in query:
                return {
                    "original": query,
                    "parsed_filters": rule["filters"]
                }

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unable to interpret natural language query: '{query}'",
        )


    # -----------------------------------
    # Apply filters on list of strings
    # -----------------------------------
    def filter_strings(self, strings: List[str], filters: Dict) -> List[str]:
        result = strings

        if filters.get("word_count") is not None:
            result = [s for s in result if len(s.split()) == filters["word_count"]]

        if filters.get("is_palindrome"):
            result = [s for s in result if palindrom(s)]

        if filters.get("min_length") is not None:
            result = [s for s in result if len(s) >= filters["min_length"]]

        if filters.get("contains_character"):
            ch = filters["contains_character"].lower()
            result = [s for s in result if ch in s.lower()]

        return result

    # -----------------------------------
    # Combine both steps
    # -----------------------------------
    def natural_query(self, db: Session, query: str | None):

        if query is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No query parsed")

        word_features = db.scalars(select(WordFeature)).all()
        words = [w.phrase for w in word_features]

        try:
            interpreted = self.parse_query(query)
            filters = interpreted["parsed_filters"]

            filtered_strings = self.filter_strings(words, filters)

            if not filtered_strings:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail="Query parsed correctly but no results matched.",
                )

            return {
                "count": len(filtered_strings),
                "data": filtered_strings,
                "interpreted_query": interpreted,
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error while parsing query: {str(e)}",
            )


    def delete(self, id: str, db: Session):
        word_feature = db.scalars(select(WordFeature).where(WordFeature.phrase == id)).first()

        if not word_feature:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Does not exist")

        db.delete(word_feature)
        db.commit()

        return {"message": "No content"}

analyzer_service = AnalyzerService()
