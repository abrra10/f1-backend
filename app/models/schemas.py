from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Driver Models
class DriverBase(BaseModel):
    driver_id: str = Field(..., alias="driverId")
    given_name: str = Field(..., alias="givenName")
    family_name: str = Field(..., alias="familyName")
    nationality: str
    permanent_number: Optional[str] = Field(None, alias="permanentNumber")
    portrait_url: Optional[str] = Field(None, alias="portraitUrl")
    team: Optional[str] = None

class DriverResponse(DriverBase):
    class Config:
        populate_by_name = True

# Constructor/Team Models
class ConstructorBase(BaseModel):
    constructor_id: str = Field(..., alias="constructorId")
    name: str
    nationality: str

class ConstructorResponse(ConstructorBase):
    class Config:
        populate_by_name = True

# Standings Models
class DriverStandingBase(BaseModel):
    position: int
    points: float
    wins: int
    driver: DriverResponse
    constructor: ConstructorResponse

class DriverStandingResponse(DriverStandingBase):
    class Config:
        populate_by_name = True

# Race Models
class RaceBase(BaseModel):
    race_id: str = Field(..., alias="raceId")
    season: int
    round: int
    race_name: str = Field(..., alias="raceName")
    circuit_name: str = Field(..., alias="circuitName")
    circuit_id: str = Field(..., alias="circuitId")
    date: str
    time: Optional[str] = None
    country: str
    locality: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class RaceResponse(RaceBase):
    class Config:
        populate_by_name = True

# Next Race Models
class NextRaceInfo(BaseModel):
    race: RaceResponse
    time_remaining: dict
    is_live: bool = False

# API Response Models
class DriversResponse(BaseModel):
    drivers: List[DriverResponse]
    total: int
    season: int

class StandingsResponse(BaseModel):
    standings: List[DriverStandingResponse]
    season: int
    round: int

class RacesResponse(BaseModel):
    races: List[RaceResponse]
    season: int
    total: int

# Health Check Model
class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    fastf1_status: str
