from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import create_vector_extension

app = FastAPI(title="Reidar V3")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.on_event("startup")
async def startup() -> None:
    await create_vector_extension()


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "version": "v3"}
