from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api import auth, address
from app.core.exceptions import (
    BizException,
    biz_exception_handler,
    generic_exception_handler,
)
from app.schemas import BaseResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="US Address Proxy Service",
    lifespan=lifespan,
)

app.add_exception_handler(BizException, biz_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)


@app.exception_handler(RequestValidationError)
async def custom_422_handler(request: Request, exc):
    return JSONResponse(
        status_code=422,
        content=BaseResponse(code=422, data=None, msg="请求参数校验失败").model_dump(),
    )


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return JSONResponse(
            status_code=404,
            content=BaseResponse(code=404, data=None, msg="接口不存在").model_dump(),
        )
    detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content=BaseResponse(code=exc.status_code, data=None, msg=detail or "请求错误").model_dump(),
    )


app.include_router(auth.router)
app.include_router(address.router)
