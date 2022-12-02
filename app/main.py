from fastapi import FastAPI, status, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from app.core.api import api_router
from app.core.config import settings

app = FastAPI()
app.include_router(api_router)


'''@app.on_event("startup")
async def on_startup():
    await init_models()'''


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


@app.get('/')
async def root():
    return {'app name': settings.app_name,
            'admin': settings.admin_email,
            'db': settings.database_url}
