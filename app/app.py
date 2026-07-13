import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router as api_router

load_dotenv()

origins = [
    "http://localhost:3000",
]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], 
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Accept",
        "X-Requested-With",
        "Idempotency-Key"
    ],
    )
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(api_router)

