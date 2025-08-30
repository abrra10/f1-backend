#!/usr/bin/env python3
"""
Simple test script for FormulaHub FastAPI Backend
"""

import asyncio
import httpx
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

async def test_endpoint(client, endpoint, description):
    """Test a single endpoint"""
    try:
        print(f"\n🔍 Testing {description}...")
        response = await client.get(f"{BASE_URL}{endpoint}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {description} - Status: {response.status_code}")
            print(f"   📊 Response keys: {list(data.keys()) if isinstance(data, dict) else 'Array response'}")
            if isinstance(data, dict) and 'total' in data:
                print(f"   📈 Total items: {data['total']}")
        else:
            print(f"❌ {description} - Status: {response.status_code}")
            print(f"   📝 Error: {response.text}")
            
    except Exception as e:
        print(f"❌ {description} - Error: {str(e)}")

async def main():
    """Run all API tests"""
    print("🚀 FormulaHub FastAPI Backend Test Suite")
    print("=" * 50)
    print(f"📍 Base URL: {BASE_URL}")
    print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test health endpoint
        await test_endpoint(client, "/api/health", "Health Check")
        
        # Test drivers endpoint
        await test_endpoint(client, "/api/drivers/", "Drivers List")
        
        # Test standings endpoint
        await test_endpoint(client, "/api/standings/", "Driver Standings")
        
        # Test races endpoint
        await test_endpoint(client, "/api/races/", "Races List")
        
        # Test next race endpoint
        await test_endpoint(client, "/api/races/next", "Next Race")
        
        # Test root endpoint
        await test_endpoint(client, "/", "Root Endpoint")
    
    print("\n" + "=" * 50)
    print("🏁 Test suite completed!")
    print("📚 API Documentation: http://localhost:8000/docs")

if __name__ == "__main__":
    asyncio.run(main())
