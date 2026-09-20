from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from sqlalchemy import text

from cafe_pos.config import settings
from cafe_pos.database import engine, Base
from cafe_pos import models  # noqa: F401
from cafe_pos.api import auth, users, products

app = FastAPI(title=settings.app_name)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(products.router)

app.mount(
    "/app",
    StaticFiles(directory=Path(__file__).parent / "static", html=True),
    name="static",
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


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
