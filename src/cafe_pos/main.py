from fastapi import FastAPI
from sqlalchemy import text

from cafe_pos.config import settings
from cafe_pos.database import engine

app = FastAPI(title=settings.app_name)


@app.get("/")
def read_root():
    return {"message": settings.app_name, "status": "running"}


@app.get("/health/db")
def check_db_connection():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"database": "connected"}
    except Exception as e:
        return {"database": "error", "detail": str(e)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("cafe_pos.main:app", host="127.0.0.1", port=8000, reload=True)
