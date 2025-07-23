from fastapi import FastAPI
from .routes import auth
from .database import engine, Base
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, chat, topics



app = FastAPI()

origins = [
    "http://localhost:3000",  # React dev server
    "http://127.0.0.1:3000",
    # add any deployment URLs here later (e.g., Netlify, Vercel)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["*"] for all (not recommended in prod)
    allow_credentials=True,
    allow_methods=["*"],     # allow all HTTP methods
    allow_headers=["*"],     # allow all headers
)

app.include_router(topics.router)
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
