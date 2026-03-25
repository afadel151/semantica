from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.main import api_router
from contextlib import asynccontextmanager
from app.core.db import init_db
import sys
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="Semantica API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "tauri://localhost",
        "http://localhost:3000",
        "http://localhost",
        "https://tauri.localhost",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Semantica API", "status": "running"}

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(api_router, prefix='/api/v1')

if __name__ == "__main__":
    import uvicorn
    if getattr(sys, 'frozen', False):
        os.chdir(os.path.dirname(sys.executable))
    uvicorn.run(app, host="127.0.0.1", port=8000)