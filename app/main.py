from fastapi import FastAPI

app = FastAPI(
    title="Test Flow API",
    description="API системы тестирования обучающихся Test Flow",
)


@app.get("/")
def root():
    return {"message": "API запущено!"}
