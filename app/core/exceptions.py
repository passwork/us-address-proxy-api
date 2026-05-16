from fastapi import Request
from fastapi.responses import JSONResponse

from app.schemas import BaseResponse


class BizException(Exception):
    def __init__(self, code: int, msg: str):
        self.code = code
        self.msg = msg


async def biz_exception_handler(_request: Request, exc: BizException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.code if exc.code >= 400 else 400,
        content=BaseResponse(code=exc.code, data=None, msg=exc.msg).model_dump(),
    )


async def generic_exception_handler(_request: Request, _exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content=BaseResponse(code=500, data=None, msg="服务器内部错误").model_dump(),
    )
