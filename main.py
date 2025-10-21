from typing import Annotated
from fastapi import Depends, FastAPI, status
from sqlalchemy.orm import Session
import uvicorn
from dotenv import load_dotenv
import os
from database import Base, engine
from schema import AnalyzeSchema, StringFilters
from services import analyzer_service
from database import get_db


load_dotenv()


app = FastAPI(title="String analyzer service")


Base.metadata.create_all(engine)


@app.post("/strings")
async def analyze(data: AnalyzeSchema, db: Annotated[Session, Depends(get_db)]):

    response = analyzer_service.analyze(data=data, db=db)

    return response


@app.get("/strings/filter-by-natural-language")
async def filter_by_natural_language(query: str | None, db: Annotated[Session, Depends(get_db)]):

    response = analyzer_service.natural_query(query=query, db=db)

    return response


@app.get("/strings/{string_value}")
async def fetch_one(string_value: str, db: Annotated[Session, Depends(get_db)]):
    
    response = analyzer_service.get_one(id=string_value, db=db)

    return response


@app.get("/strings")
async def fetch_all(filters: Annotated[StringFilters, Depends()], db: Annotated[Session, Depends(get_db)]):
    
    response = analyzer_service.get_all(filters=filters, db=db)

    return response


@app.delete("/strings/{value}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(value: str, db: Annotated[Session, Depends(get_db)]):

    response = analyzer_service.delete(id=value, db=db)

    return response


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run( "main:app", host="0.0.0.0", port=port, reload=True)

