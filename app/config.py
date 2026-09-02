import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    DATABASE_URL: str = os.getenv("DATABASE_URI")

    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: str = os.getenv(
        "JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 10
    )

    ALLOW_ORIGINS: list[str] = os.getenv(
        "ALLOW_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
    ).split(",")
    ALLOW_CREDENTIALS: bool = True
    ALLOW_METHODS: list[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    ALLOW_HEADERS: list[str] = [
        "Content-Type",
        "Authorization",
        "Accept",
        "X-Requested-With",
        "Idempotency-Key",
    ]


config = Config()
