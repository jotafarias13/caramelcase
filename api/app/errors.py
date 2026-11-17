"""The single error shape: {"error": {"code": "...", "message": "..."}}.

Routes raise AppError. Errors raised by FastAPI itself (unknown route,
invalid body) and unexpected exceptions are converted to the same shape.
"""

from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException


class ErrorBody(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorBody


class AppError(Exception):
    def __init__(self, status: int, code: str, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message


def error_response(status: int, code: str, message: str) -> JSONResponse:
    body = ErrorResponse(error=ErrorBody(code=code, message=message))
    return JSONResponse(status_code=status, content=body.model_dump())


def _code_for_status(status: int) -> str:
    """Name a status in snake case: 404 becomes "not_found"."""
    return HTTPStatus(status).name.lower()


def _on_app_error(_: Request, error: Exception) -> JSONResponse:
    assert isinstance(error, AppError)
    return error_response(error.status, error.code, error.message)


def _on_http_exception(_: Request, error: Exception) -> JSONResponse:
    assert isinstance(error, HTTPException)
    code = _code_for_status(error.status_code)
    return error_response(error.status_code, code, str(error.detail))


def _on_validation_error(_: Request, error: Exception) -> JSONResponse:
    assert isinstance(error, RequestValidationError)
    first = error.errors()[0]
    field = ".".join(str(part) for part in first["loc"])
    message = f"{field}: {first['msg']}"
    return error_response(422, "validation_error", message)


def _on_unexpected_error(_: Request, __: Exception) -> JSONResponse:
    return error_response(500, "internal_error", "Something went wrong.")


def add_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, _on_app_error)
    app.add_exception_handler(HTTPException, _on_http_exception)
    app.add_exception_handler(RequestValidationError, _on_validation_error)
    app.add_exception_handler(Exception, _on_unexpected_error)
