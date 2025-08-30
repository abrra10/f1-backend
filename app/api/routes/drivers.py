from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.models.schemas import DriversResponse, DriverResponse
from app.services.fastf1_service import fastf1_service
from app.services.cache_service import cache_service

router = APIRouter()

@router.get("/", response_model=DriversResponse)
async def get_drivers(season: Optional[int] = Query(None, description="Season year")):
    """Get all drivers for a specific season"""
    try:
        # Check cache first
        cache_key = f"drivers:{season or 'current'}"
        cached_data = await cache_service.get(cache_key)
        
        if cached_data:
            return DriversResponse(**cached_data)
        
        # Fetch from FastF1
        drivers_data = await fastf1_service.get_drivers(season)
        
        if not drivers_data:
            raise HTTPException(status_code=404, detail="No drivers found for this season")
        
        response_data = {
            "drivers": drivers_data,
            "total": len(drivers_data),
            "season": season or fastf1_service.current_season
        }
        
        # Cache the response
        await cache_service.set(cache_key, response_data, ttl=3600)  # 1 hour cache
        
        return DriversResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching drivers: {str(e)}")

@router.get("/{driver_id}", response_model=DriverResponse)
async def get_driver(driver_id: str, season: Optional[int] = Query(None, description="Season year")):
    """Get specific driver information"""
    try:
        # Check cache first
        cache_key = f"driver:{driver_id}:{season or 'current'}"
        cached_data = await cache_service.get(cache_key)
        
        if cached_data:
            return DriverResponse(**cached_data)
        
        # Fetch all drivers and find the specific one
        drivers_data = await fastf1_service.get_drivers(season)
        
        driver = next((d for d in drivers_data if d['driverId'] == driver_id), None)
        
        if not driver:
            raise HTTPException(status_code=404, detail=f"Driver {driver_id} not found")
        
        # Cache the response
        await cache_service.set(cache_key, driver, ttl=3600)  # 1 hour cache
        
        return DriverResponse(**driver)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching driver: {str(e)}")
