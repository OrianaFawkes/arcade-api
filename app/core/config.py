import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    def __init__(self):
        self.app_env = os.getenv(
            "APP_ENV",
            "development",
        ).strip().lower()

        database_url = os.getenv("DATABASE_URL")

        if database_url:
            self.database_url = database_url

        elif self.app_env == "development":
            self.database_url = (
                "postgresql+psycopg://arcade:arcade@localhost:5432/arcade"
            )

        else:
            raise RuntimeError(
                "DATABASE_URL must be configured "
                "outside the development environment."
            )

        self.cors_origins = [
            origin.strip()
            for origin in os.getenv("CORS_ORIGINS", "").split(",")
            if origin.strip()
        ]


settings = Settings()
