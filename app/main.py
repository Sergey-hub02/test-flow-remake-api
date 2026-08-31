from fastapi import FastAPI
from app.routes import user

app = FastAPI(
    title="Test Flow API",
    description="API системы тестирования обучающихся Test Flow",
)

app.include_router(user.router, prefix="/api/v1/users")
