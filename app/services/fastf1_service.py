import fastf1
import fastf1.ergast
import pandas as pd
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import logging
from app.core.config import settings

# Configure FastF1
fastf1.Cache.enable_cache(settings.fastf1_cache_dir)
fastf1.set_log_level('WARNING' if not settings.fastf1_verbose else 'INFO')

logger = logging.getLogger(__name__)

class FastF1Service:
    def __init__(self):
        self.current_season = settings.current_season
        self.supported_seasons = settings.supported_seasons
        self.ergast = fastf1.ergast.Ergast()
    
    async def get_drivers(self, season: int = None) -> List[Dict]:
        """Get all drivers for a specific season"""
        if season is None:
            season = self.current_season
            
        try:
            # Get drivers using the ergast API
            drivers_df = self.ergast.get_driver_info(season)
            drivers_list = []
            
            for _, driver in drivers_df.iterrows():
                driver_data = {
                    'driverId': driver['driverId'],
                    'givenName': driver['givenName'],
                    'familyName': driver['familyName'],
                    'nationality': driver['driverNationality'],
                    'permanentNumber': str(driver.get('driverNumber', '')),
                    'portraitUrl': f"/static/drivers/{driver['driverId']}.jpg",
                    'team': 'Unknown'  # We'll need to get this from constructor info
                }
                drivers_list.append(driver_data)
                
            return drivers_list
            
        except Exception as e:
            logger.error(f"Error fetching drivers for season {season}: {e}")
            return []
    
    async def get_standings(self, season: int = None, round_num: int = None) -> List[Dict]:
        """Get driver standings for a specific season and round"""
        if season is None:
            season = self.current_season
            
        try:
            # Get standings data using the ergast API
            if round_num:
                standings_response = self.ergast.get_driver_standings(season, round_num)
            else:
                # Get latest standings
                standings_response = self.ergast.get_driver_standings(season)
            
            standings_list = []
            
            # The response contains a list of dataframes, we want the first one
            standings_df = standings_response.content[0]
            
            for _, row in standings_df.iterrows():
                standing_data = {
                    'position': int(row['position']),
                    'points': float(row['points']),
                    'wins': int(row.get('wins', 0)),
                    'driver': {
                        'driverId': row['driverId'],
                        'givenName': row['givenName'],
                        'familyName': row['familyName'],
                        'nationality': row['driverNationality'],
                        'permanentNumber': str(row.get('driverNumber', '')),
                        'portraitUrl': f"/static/drivers/{row['driverId']}.jpg",
                        'team': row.get('constructorNames', ['Unknown'])[0] if row.get('constructorNames') else 'Unknown'
                    },
                    'constructor': {
                        'constructorId': row.get('constructorIds', ['unknown'])[0] if row.get('constructorIds') else 'unknown',
                        'name': row.get('constructorNames', ['Unknown'])[0] if row.get('constructorNames') else 'Unknown',
                        'nationality': row.get('constructorNationalities', ['Unknown'])[0] if row.get('constructorNationalities') else 'Unknown'
                    }
                }
                standings_list.append(standing_data)
                
            return standings_list
            
        except Exception as e:
            logger.error(f"Error fetching standings for season {season}: {e}")
            return []
    
    async def get_races(self, season: int = None) -> List[Dict]:
        """Get all races for a specific season"""
        if season is None:
            season = self.current_season
            
        try:
            # Get season schedule using the ergast API
            schedule_df = self.ergast.get_race_schedule(season)
            races = []
            
            for _, event in schedule_df.iterrows():
                race_data = {
                    'raceId': f"{season}_{event['raceName']}",
                    'season': season,
                    'round': int(event['round']),
                    'raceName': event['raceName'],
                    'circuitName': event['circuitName'],
                    'circuitId': event['circuitId'],
                    'date': event['raceDate'].strftime('%Y-%m-%d'),
                    'time': event['raceTime'].strftime('%H:%M:%SZ') if pd.notna(event['raceTime']) else '12:00:00Z',
                    'country': event['country'],
                    'locality': event['locality'],
                    'latitude': event.get('lat'),
                    'longitude': event.get('long')
                }
                races.append(race_data)
                
            return races
            
        except Exception as e:
            logger.error(f"Error fetching races for season {season}: {e}")
            return []
    
    async def get_next_race(self, season: int = None) -> Optional[Dict]:
        """Get the next upcoming race"""
        if season is None:
            season = self.current_season
            
        try:
            races = await self.get_races(season)
            current_time = datetime.now()
            
            for race in races:
                race_datetime = datetime.strptime(f"{race['date']} {race['time']}", '%Y-%m-%d %H:%M:%SZ')
                if race_datetime > current_time:
                    return race
                    
            return None
            
        except Exception as e:
            logger.error(f"Error fetching next race for season {season}: {e}")
            return None
    
    async def calculate_time_remaining(self, race: Dict) -> Dict:
        """Calculate time remaining until race start"""
        try:
            race_datetime = datetime.strptime(f"{race['date']} {race['time']}", '%Y-%m-%d %H:%M:%SZ')
            current_time = datetime.now()
            time_diff = race_datetime - current_time
            
            if time_diff.total_seconds() <= 0:
                return {
                    'days': 0,
                    'hours': 0,
                    'minutes': 0,
                    'seconds': 0,
                    'message': 'Race is happening now!'
                }
            
            days = time_diff.days
            hours = time_diff.seconds // 3600
            minutes = (time_diff.seconds % 3600) // 60
            seconds = time_diff.seconds % 60
            
            return {
                'days': days,
                'hours': hours,
                'minutes': minutes,
                'seconds': seconds
            }
            
        except Exception as e:
            logger.error(f"Error calculating time remaining: {e}")
            return {
                'days': 0,
                'hours': 0,
                'minutes': 0,
                'seconds': 0,
                'message': 'Error calculating time'
            }
    
    async def get_race_results(self, season: int, round_num: int) -> List[Dict]:
        """Get race results for a specific race"""
        try:
            results_df = self.ergast.get_race_results(season, round_num)
            results_list = []
            
            for _, row in results_df.iterrows():
                result_data = {
                    'position': int(row['position']) if pd.notna(row['position']) else 0,
                    'driver': {
                        'driverId': row['driverId'],
                        'givenName': row['givenName'],
                        'familyName': row['familyName'],
                        'nationality': row['nationality']
                    },
                    'constructor': {
                        'constructorId': row.get('constructorId', 'unknown'),
                        'name': row.get('constructorId', 'Unknown')
                    },
                    'status': row.get('status', 'Finished'),
                    'points': float(row.get('points', 0))
                }
                results_list.append(result_data)
                
            return results_list
            
        except Exception as e:
            logger.error(f"Error fetching race results: {e}")
            return []

# Global instance
fastf1_service = FastF1Service()
