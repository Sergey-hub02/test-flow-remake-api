from fastapi import FastAPI
from app.routes import user, auth, storage

app = FastAPI(
    title="Test Flow API",
    description="API системы тестирования обучающихся Test Flow",
)

app.include_router(user.router, prefix="/api/v1/users")
app.include_router(auth.router, prefix="/api/v1/auth")
app.include_router(storage.router, prefix="/storage")
