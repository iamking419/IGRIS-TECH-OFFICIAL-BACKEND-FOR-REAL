import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from routes import contact, ecosystem, projects, reviews

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "Igris Tech Official Backend")
DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")

# Parse CORS Origins from environment (default to allow-all for easier frontend testing)
cors_origins_raw = os.getenv("CORS_ORIGINS", "*")
if cors_origins_raw.strip() == "*":
    origins = ["*"]
else:
    origins = [origin.strip() for origin in cors_origins_raw.split(",") if origin.strip()]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize tables if not existing
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=APP_NAME,
    description="Official minimal FastAPI backend powering Igris Tech projects, ecosystem, reviews, and inquiries.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------------------------------------------
# Base & Health Endpoints
# -----------------------------------------------------------------------------

@app.get("/", tags=["Health"])
def root():
    return {
        "app": APP_NAME,
        "status": "online",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}


# -----------------------------------------------------------------------------
# Register Feature Routers (/api/v1/...)
# -----------------------------------------------------------------------------

app.include_router(projects.router)
app.include_router(ecosystem.router)
app.include_router(reviews.router)
app.include_router(contact.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=DEBUG)
