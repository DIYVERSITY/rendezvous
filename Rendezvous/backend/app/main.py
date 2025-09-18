from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import endpoints as api_router

app = FastAPI(title="Rendezvous Backend", version="0.1.0")

# CORS (Cross-Origin Resource Sharing)
origins = [
    "http://localhost:3000",  # Next.js frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Rendezvous backend."}
