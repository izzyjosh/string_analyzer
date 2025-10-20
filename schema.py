from typing import Optional
from pydantic import BaseModel

class AnalyzeSchema(BaseModel):
    value: str


class StringFilters(BaseModel):
    is_palindrome: Optional[bool] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    word_count: Optional[int] = None
    contains_character: Optional[str] = None
