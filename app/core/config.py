import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://arcade:arcade@localhost:5432/arcade",
    )


settings = Settings()