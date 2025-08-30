import json
import asyncio
from datetime import datetime, timedelta
import httpx

# Simple in-memory cache for Cloudflare Workers
cache = {}

class Response:
    def __init__(self, body, status=200, headers=None):
        self.body = body
        self.status = status
        self.headers = headers or {}

def get_cached_data(key):
    """Get data from cache if not expired"""
    if key in cache:
        data, timestamp = cache[key]
        # Cache expires after 30 minutes
        if datetime.now() - timestamp < timedelta(minutes=30):
            return data
        else:
            del cache[key]
    return None

def set_cached_data(key, data):
    """Store data in cache with timestamp"""
    cache[key] = (data, datetime.now())

async def fetch_f1_data(endpoint):
    """Fetch data from Ergast API as fallback"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://ergast.com/api/f1/{endpoint}")
            return response.json()
    except Exception as e:
        return {"error": str(e)}

def handle_cors_headers():
    """Return CORS headers"""
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
        "Content-Type": "application/json"
    }

async def handle_health_check():
    """Health check endpoint"""
    return Response(
        json.dumps({
            "status": "healthy",
            "deployment": "cloudflare-workers",
            "timestamp": datetime.now().isoformat()
        }),
        headers=handle_cors_headers()
    )

async def handle_drivers():
    """Get drivers data"""
    cache_key = "drivers_2025"
    cached_data = get_cached_data(cache_key)
    
    if cached_data:
        return Response(
            json.dumps(cached_data),
            headers=handle_cors_headers()
        )
    
    # Fetch from Ergast API
    data = await fetch_f1_data("2025/drivers.json")
    
    if "error" not in data:
        # Transform data to match your API structure
        drivers = data.get("MRData", {}).get("DriverTable", {}).get("Drivers", [])
        transformed_data = {
            "drivers": drivers,
            "total": len(drivers),
            "season": 2025
        }
        set_cached_data(cache_key, transformed_data)
        return Response(
            json.dumps(transformed_data),
            headers=handle_cors_headers()
        )
    
    return Response(
        json.dumps({"error": "Failed to fetch drivers data"}),
        status=500,
        headers=handle_cors_headers()
    )

async def handle_standings():
    """Get driver standings"""
    cache_key = "standings_2025"
    cached_data = get_cached_data(cache_key)
    
    if cached_data:
        return Response(
            json.dumps(cached_data),
            headers=handle_cors_headers()
        )
    
    # Fetch from Ergast API
    data = await fetch_f1_data("current/driverStandings.json")
    
    if "error" not in data:
        standings_list = data.get("MRData", {}).get("StandingsTable", {}).get("StandingsLists", [])
        if standings_list:
            standings = standings_list[0].get("DriverStandings", [])
            transformed_data = {
                "standings": standings,
                "season": 2025,
                "round": standings_list[0].get("round", 0)
            }
            set_cached_data(cache_key, transformed_data)
            return Response(
                json.dumps(transformed_data),
                headers=handle_cors_headers()
            )
    
    return Response(
        json.dumps({"error": "Failed to fetch standings data"}),
        status=500,
        headers=handle_cors_headers()
    )

async def handle_next_race():
    """Get next race information"""
    cache_key = "next_race"
    cached_data = get_cached_data(cache_key)
    
    if cached_data:
        return Response(
            json.dumps(cached_data),
            headers=handle_cors_headers()
        )
    
    # Fetch from Ergast API
    data = await fetch_f1_data("current.json")
    
    if "error" not in data:
        races = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
        current_time = datetime.now()
        
        # Find next race
        next_race = None
        for race in races:
            race_date = datetime.strptime(race["date"], "%Y-%m-%d")
            if race_date > current_time:
                next_race = race
                break
        
        if next_race:
            # Calculate time remaining
            race_datetime = datetime.strptime(f"{next_race['date']} {next_race['time']}", "%Y-%m-%d %H:%M:%SZ")
            time_diff = race_datetime - current_time
            
            if time_diff.total_seconds() <= 0:
                time_remaining = {
                    "days": 0,
                    "hours": 0,
                    "minutes": 0,
                    "seconds": 0,
                    "message": "Race is happening now!"
                }
            else:
                days = time_diff.days
                hours = time_diff.seconds // 3600
                minutes = (time_diff.seconds % 3600) // 60
                seconds = time_diff.seconds % 60
                
                time_remaining = {
                    "days": days,
                    "hours": hours,
                    "minutes": minutes,
                    "seconds": seconds
                }
            
            transformed_data = {
                "race": next_race,
                "time_remaining": time_remaining,
                "is_live": time_remaining.get('message') == 'Race is happening now!'
            }
            
            set_cached_data(cache_key, transformed_data)
            return Response(
                json.dumps(transformed_data),
                headers=handle_cors_headers()
            )
    
    return Response(
        json.dumps({"error": "Failed to fetch next race data"}),
        status=500,
        headers=handle_cors_headers()
    )

async def handle_races():
    """Get all races for the season"""
    cache_key = "races_2025"
    cached_data = get_cached_data(cache_key)
    
    if cached_data:
        return Response(
            json.dumps(cached_data),
            headers=handle_cors_headers()
        )
    
    # Fetch from Ergast API
    data = await fetch_f1_data("2025.json")
    
    if "error" not in data:
        races = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
        transformed_data = {
            "races": races,
            "total": len(races),
            "season": 2025
        }
        set_cached_data(cache_key, transformed_data)
        return Response(
            json.dumps(transformed_data),
            headers=handle_cors_headers()
        )
    
    return Response(
        json.dumps({"error": "Failed to fetch races data"}),
        status=500,
        headers=handle_cors_headers()
    )

# Main handler for Cloudflare Workers
async def handle_request(request, env):
    """Main request handler for Cloudflare Workers"""
    url = request.url
    path = url.path
    method = request.method
    
    # Handle CORS preflight
    if method == "OPTIONS":
        return Response("", headers=handle_cors_headers())
    
    # Root endpoint
    if path == "/":
        return Response(
            json.dumps({
                "message": "FormulaHub API is running on Cloudflare Workers!",
                "docs": "API endpoints available",
                "version": "1.0.0",
                "deployment": "cloudflare-workers",
                "endpoints": [
                    "/api/health",
                    "/api/drivers",
                    "/api/standings", 
                    "/api/races",
                    "/api/races/next"
                ]
            }),
            headers=handle_cors_headers()
        )
    
    # API routes
    if path == "/api/health":
        return await handle_health_check()
    
    elif path == "/api/drivers":
        return await handle_drivers()
    
    elif path == "/api/standings":
        return await handle_standings()
    
    elif path == "/api/races":
        return await handle_races()
    
    elif path == "/api/races/next":
        return await handle_next_race()
    
    # 404 for unknown routes
    return Response(
        json.dumps({
            "error": "Not found",
            "path": path,
            "available_endpoints": [
                "/api/health",
                "/api/drivers",
                "/api/standings",
                "/api/races",
                "/api/races/next"
            ]
        }),
        status=404,
        headers=handle_cors_headers()
    )

# Export the handler for Cloudflare Workers
def fetch(request, env):
    """Entry point for Cloudflare Workers"""
    return asyncio.run(handle_request(request, env))
