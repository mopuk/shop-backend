from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import config



app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOW_ORIGINS,
    allow_credentials=config.ALLOW_CREDENTIALS,
    allow_methods=config.ALLOW_METHODS, 
    allow_headers=config.ALLOW_HEADERS,
    )

from app import models, routes