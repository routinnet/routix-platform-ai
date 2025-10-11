from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from src.core.database import create_tables, AsyncSessionLocal
from src.api.v1.api import api_router
from src.core.config import settings
from src.core.seed_data import seed_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting Routix API...")
    await create_tables()
    
    # Seed database with initial data
    async with AsyncSessionLocal() as db:
        await seed_database(db)
    
    print("Database initialized and seeded")
    yield
    # Shutdown
    print("Shutting down Routix API...")


app = FastAPI(
    title="Routix API",
    description="AI-Powered Thumbnail Generation Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Static files for uploads
if not os.path.exists("uploads"):
    os.makedirs("uploads")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Routix API is running"}

@app.get("/")
async def root():
    return {
        "message": "Welcome to Routix API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
