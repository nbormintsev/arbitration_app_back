from contextlib import asynccontextmanager
from os import getenv

import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer

from src.auth.views import router as auth_router
from src.clients.views import router as clients_router
from src.security import keys_manager
from src.database import database_manager

http_bearer = HTTPBearer(auto_error=False)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    keys_manager.generate_keys()
    await database_manager.get_pool()
    yield
    await database_manager.close_pool()


app = FastAPI(lifespan=lifespan)
app.include_router(
    router=auth_router,
    dependencies=[Depends(http_bearer)],
    prefix="/auth",
    tags=["Auth"],
)
app.include_router(
    router=clients_router,
    dependencies=[Depends(http_bearer)],
    prefix="/clients",
    tags=["Clients"],
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def start():
    """Точка входа для poetry."""
    uvicorn.run(
        app='src.main:app',
        host=getenv('BACK_HOST'),
        port=int(getenv('BACK_PORT')),
        reload=True
    )
