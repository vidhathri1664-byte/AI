from fastapi import FastAPI
from sqlalchemy import text

from app.database import SessionLocal
from app.routes.auth import router as auth_router
from app.routes.users import router as users_router

app = FastAPI(
    title="Enterprise Knowledge Assistant",
    description="Enterprise RAG platform for document question answering with citations",
    version="1.0.0",
)


app.include_router(auth_router)
app.include_router(users_router)

@app.get("/")
def root():
    return {"message": "Enterprise Knowledge Assistant API is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/db-health")
def database_health_check():
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        return {"database": "connected"}
    finally:
        db.close()


