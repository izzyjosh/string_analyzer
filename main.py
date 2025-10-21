from typing import Annotated
from fastapi import Depends, FastAPI, status, Request
from sqlalchemy.orm import Session
import uvicorn
from dotenv import load_dotenv
import os
from database import Base, engine
from schema import AnalyzeSchema, StringFilters
from services import analyzer_service
from database import get_db

from fastapi.exceptions import FastAPIError, RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHttpException

from responses import ErrorResponse, ValidationErrorResponse
from responses  import success_response

load_dotenv()


app = FastAPI(title="String analyzer service")


Base.metadata.create_all(engine)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = []
    for error in exc.errors():
        errors.append({
            "field": error.get("loc")[-1],
            "message": error.get("msg")
        })

    is_query_param_error = any(
        err.get("loc")[0] == "query" for err in exc.errors()
    )

    is_missing_field = any(
        err.get("type") in ["value_error.missing", "missing"] for err in exc.errors()
    )

    if is_missing_field or is_query_param_error:
        response = ValidationErrorResponse(status_code=status.HTTP_400_BAD_REQUEST, errors=errors)
    else:
        response = ValidationErrorResponse(errors=errors)

    status_code = (
        status.HTTP_400_BAD_REQUEST
        if is_missing_field or is_query_param_error
        else status.HTTP_422_UNPROCESSABLE_ENTITY
    )

    return JSONResponse(content=response.model_dump(), status_code=status_code)


@app.exception_handler(StarletteHttpException)
async def starlette_http_handler(request: Request, exc: StarletteHttpException) -> JSONResponse:
    response: ErrorResponse = ErrorResponse(status_code=exc.status_code, message=exc.detail)
    return JSONResponse(content=response.model_dump(), status_code=exc.status_code)


@app.exception_handler(FastAPIError)
async def http_exception_handler(request: Request, exc: FastAPIError) -> JSONResponse:

    response: ErrorResponse = ErrorResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="Internal Server Error")

    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=response.model_dump())




@app.post("/strings")
async def analyze(data: AnalyzeSchema, db: Annotated[Session, Depends(get_db)]):

    response = analyzer_service.analyze(data=data, db=db)

    return success_response(status_code=status.HTTP_201_CREATED, message="created successfully", data=response)


@app.get("/strings/filter-by-natural-language")
async def filter_by_natural_language(query: str | None, db: Annotated[Session, Depends(get_db)]):

    response = analyzer_service.natural_query(query=query, db=db)

    return response


@app.get("/strings/{string_value}")
async def fetch_one(string_value: str, db: Annotated[Session, Depends(get_db)]):
    
    response = analyzer_service.get_one(id=string_value, db=db)

    return success_response(status_code=status.HTTP_200_OK, message="Successfull", data=response)


@app.get("/strings")
async def fetch_all(filters: Annotated[StringFilters, Depends()], db: Annotated[Session, Depends(get_db)]):
    
    response = analyzer_service.get_all(filters=filters, db=db)

    return success_response(status_code=status.HTTP_200_OK, message="Successfull", data=response)


@app.delete("/strings/{value}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(value: str, db: Annotated[Session, Depends(get_db)]):

    analyzer_service.delete(id=value, db=db)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run( "main:app", host="0.0.0.0", port=port, reload=True)

