from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.models.schemas import StandingsResponse, DriverStandingResponse
from app.services.fastf1_service import fastf1_service
from app.services.cache_service import cache_service

router = APIRouter()

@router.get("/", response_model=StandingsResponse)
async def get_standings(
    season: Optional[int] = Query(None, description="Season year"),
    round_num: Optional[int] = Query(None, description="Round number")
):
    """Get driver standings for a specific season and round"""
    try:
        # Check cache first
        cache_key = f"standings:{season or 'current'}:{round_num or 'latest'}"
        cached_data = await cache_service.get(cache_key)
        
        if cached_data:
            return StandingsResponse(**cached_data)
        
        # Fetch from FastF1
        standings_data = await fastf1_service.get_standings(season, round_num)
        
        if not standings_data:
            raise HTTPException(status_code=404, detail="No standings found for this season/round")
        
        response_data = {
            "standings": standings_data,
            "season": season or fastf1_service.current_season,
            "round": round_num or 0  # 0 indicates latest standings
        }
        
        # Cache the response (shorter TTL for standings as they change more frequently)
        await cache_service.set(cache_key, response_data, ttl=1800)  # 30 minutes cache
        
        return StandingsResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching standings: {str(e)}")

@router.get("/driver/{driver_id}", response_model=DriverStandingResponse)
async def get_driver_standing(
    driver_id: str,
    season: Optional[int] = Query(None, description="Season year"),
    round_num: Optional[int] = Query(None, description="Round number")
):
    """Get specific driver's standing"""
    try:
        # Check cache first
        cache_key = f"driver_standing:{driver_id}:{season or 'current'}:{round_num or 'latest'}"
        cached_data = await cache_service.get(cache_key)
        
        if cached_data:
            return DriverStandingResponse(**cached_data)
        
        # Fetch all standings and find the specific driver
        standings_data = await fastf1_service.get_standings(season, round_num)
        
        driver_standing = next((s for s in standings_data if s['driver']['driverId'] == driver_id), None)
        
        if not driver_standing:
            raise HTTPException(status_code=404, detail=f"Standing for driver {driver_id} not found")
        
        # Cache the response
        await cache_service.set(cache_key, driver_standing, ttl=1800)  # 30 minutes cache
        
        return DriverStandingResponse(**driver_standing)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching driver standing: {str(e)}")
