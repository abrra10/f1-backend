from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.models.schemas import RacesResponse, RaceResponse, NextRaceInfo
from app.services.fastf1_service import fastf1_service
from app.services.cache_service import cache_service

router = APIRouter()

@router.get("/", response_model=RacesResponse)
async def get_races(season: Optional[int] = Query(None, description="Season year")):
    """Get all races for a specific season"""
    try:
        # Check cache first
        cache_key = f"races:{season or 'current'}"
        cached_data = await cache_service.get(cache_key)
        
        if cached_data:
            return RacesResponse(**cached_data)
        
        # Fetch from FastF1
        races_data = await fastf1_service.get_races(season)
        
        if not races_data:
            raise HTTPException(status_code=404, detail="No races found for this season")
        
        response_data = {
            "races": races_data,
            "season": season or fastf1_service.current_season,
            "total": len(races_data)
        }
        
        # Cache the response
        await cache_service.set(cache_key, response_data, ttl=7200)  # 2 hours cache
        
        return RacesResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching races: {str(e)}")

@router.get("/next", response_model=NextRaceInfo)
async def get_next_race(season: Optional[int] = Query(None, description="Season year")):
    """Get the next upcoming race with countdown"""
    try:
        # Check cache first (shorter TTL for next race as it changes frequently)
        cache_key = f"next_race:{season or 'current'}"
        cached_data = await cache_service.get(cache_key)
        
        if cached_data:
            return NextRaceInfo(**cached_data)
        
        # Fetch next race
        next_race = await fastf1_service.get_next_race(season)
        
        if not next_race:
            raise HTTPException(status_code=404, detail="No upcoming races found")
        
        # Calculate time remaining
        time_remaining = await fastf1_service.calculate_time_remaining(next_race)
        
        response_data = {
            "race": next_race,
            "time_remaining": time_remaining,
            "is_live": time_remaining.get('message') == 'Race is happening now!'
        }
        
        # Cache the response (short TTL for next race)
        await cache_service.set(cache_key, response_data, ttl=300)  # 5 minutes cache
        
        return NextRaceInfo(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching next race: {str(e)}")

@router.get("/{race_id}", response_model=RaceResponse)
async def get_race(race_id: str, season: Optional[int] = Query(None, description="Season year")):
    """Get specific race information"""
    try:
        # Check cache first
        cache_key = f"race:{race_id}:{season or 'current'}"
        cached_data = await cache_service.get(cache_key)
        
        if cached_data:
            return RaceResponse(**cached_data)
        
        # Fetch all races and find the specific one
        races_data = await fastf1_service.get_races(season)
        
        race = next((r for r in races_data if r['raceId'] == race_id), None)
        
        if not race:
            raise HTTPException(status_code=404, detail=f"Race {race_id} not found")
        
        # Cache the response
        await cache_service.set(cache_key, race, ttl=7200)  # 2 hours cache
        
        return RaceResponse(**race)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching race: {str(e)}")

@router.get("/{race_id}/results")
async def get_race_results(
    race_id: str,
    season: Optional[int] = Query(None, description="Season year")
):
    """Get race results for a specific race"""
    try:
        # Check cache first
        cache_key = f"race_results:{race_id}:{season or 'current'}"
        cached_data = await cache_service.get(cache_key)
        
        if cached_data:
            return cached_data
        
        # Parse race_id to get round number
        # Assuming race_id format: "2024_Australian_Grand_Prix"
        races_data = await fastf1_service.get_races(season)
        race = next((r for r in races_data if r['raceId'] == race_id), None)
        
        if not race:
            raise HTTPException(status_code=404, detail=f"Race {race_id} not found")
        
        # Get race results
        results = await fastf1_service.get_race_results(race['season'], race['round'])
        
        if not results:
            raise HTTPException(status_code=404, detail="No results found for this race")
        
        # Cache the response
        await cache_service.set(cache_key, results, ttl=3600)  # 1 hour cache
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching race results: {str(e)}")
