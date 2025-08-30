from fastapi import APIRouter, HTTPException
from app.models.schemas import HealthResponse
from app.services.fastf1_service import fastf1_service
from datetime import datetime
import fastf1.ergast

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Test FastF1 connection
        fastf1_status = "healthy"
        try:
            # Try to get basic drivers info to test FastF1
            ergast = fastf1.ergast.Ergast()
            ergast.get_driver_info(2025)
        except Exception as e:
            fastf1_status = f"error: {str(e)}"
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now(),
            version="1.0.0",
            fastf1_status=fastf1_status
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")
