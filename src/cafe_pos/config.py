from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@localhost:5432/cafe_pos"
    app_name: str = "Cloud POS для мережі кав'ярень"

    class Config:
        env_file = ".env"


settings = Settings()

