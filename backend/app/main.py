from fastapi import FastAPI
from .routes import auth
from .database import engine, Base


app = FastAPI()
app.include_router(auth.router)

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Hybrid Medical Chatbot API!"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
