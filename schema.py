from typing import Optional
from pydantic import BaseModel, validator

class AnalyzeSchema(BaseModel):
    value: str

    @validator("value")
    def validate_value(cls, v):
        if not isinstance(v, str):
            raise TypeError("'value' field must be a string.")
        if not v.strip():
            raise ValueError("'value' field cannot be empty or whitespace.")
        return v.strip()


class StringFilters(BaseModel):
    is_palindrome: Optional[bool] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    word_count: Optional[int] = None
    contains_character: Optional[str] = None
