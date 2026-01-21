from fastapi import FastAPI

from app.api import router

app = FastAPI(title="Main Server")
app.include_router(router.router)