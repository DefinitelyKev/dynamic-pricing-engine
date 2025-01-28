from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    PROJECT_NAME: str = "Dynamic Pricing Engine"
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/dynamic_pricing"

    class Config:
        case_sensitive = True


settings = Settings()
