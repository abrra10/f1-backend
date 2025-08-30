from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
from app.api.routes import drivers, standings, races, health
# from app.core.config import settings

app = FastAPI(
    title="FormulaHub API",
    description="FastAPI backend for FormulaHub with FastF1 integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(drivers.router, prefix="/api/drivers", tags=["drivers"])
app.include_router(standings.router, prefix="/api/standings", tags=["standings"])
app.include_router(races.router, prefix="/api/races", tags=["races"])

@app.get("/")
async def root():
    return {
        "message": "FormulaHub API is running!",
        "docs": "/docs",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
