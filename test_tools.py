import os
import asyncio
import httpx
from dotenv import load_dotenv
from datetime import datetime, timedelta, UTC

load_dotenv()

BASE_V1 = "https://test.api.amadeus.com/v1"


# -----------------------
# TOKEN
# -----------------------
async def get_token():
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            "https://test.api.amadeus.com/v1/security/oauth2/token",
            data={
                "grant_type": "client_credentials",
                "client_id": os.getenv("AMADEUS_CLIENT_ID"),
                "client_secret": os.getenv("AMADEUS_CLIENT_SECRET"),
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        r.raise_for_status()
        return r.json()["access_token"]


# -----------------------
# TEST 1: TOKEN
# -----------------------
async def test_token():
    token = await get_token()
    print(" TOKEN OK:", token[:20], "...")


# -----------------------
# TEST 2: HOTELS BY CITY
# -----------------------
async def test_hotels_by_city():
    token = await get_token()
    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(
            f"{BASE_V1}/reference-data/locations/hotels/by-city",
            headers=headers,
            params={"cityCode": "BLR"},
        )
        r.raise_for_status()
        data = r.json()
        print(" HOTELS BY CITY OK")
        print("Count:", data["meta"]["count"])


# -----------------------
# TEST 3: TRANSFER SEARCH
# -----------------------
async def test_transfer_search():
    token = await get_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    future_time = (
        datetime.now(UTC) + timedelta(days=5)
    ).strftime("%Y-%m-%dT%H:%M:%S")

    body = {
        "startLocationCode": "BLR",
        "endLocationCode": "BLR",
        "startDateTime": future_time,
        "passengers": 1,
        "transferType": "PRIVATE",
    }

    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            f"{BASE_V1}/shopping/transfer-offers",
            headers=headers,
            json=body,
        )
        r.raise_for_status()
        data = r.json()
        print(" TRANSFER SEARCH OK")
        print("Offers:", len(data.get("data", [])))


# -----------------------
# TEST 4: AIR TRAFFIC (WORKING ANALYTICS)
# -----------------------
async def test_air_traffic_traveled():
    token = await get_token()
    headers = {"Authorization": f"Bearer {token}"}

    params = {
        "originCityCode": "BLR",
        "period": "2025-01",
        "max": 5,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(
            f"{BASE_V1}/travel/analytics/air-traffic/traveled",
            headers=headers,
            params=params,
        )
        r.raise_for_status()
        print(" AIR TRAFFIC TRAVELED OK")
        print(r.json())


# -----------------------
# TEST 5: BUSIEST PERIOD (SAFE HANDLING)
# -----------------------
async def test_busiest_travel_period():
    token = await get_token()
    headers = {"Authorization": f"Bearer {token}"}

    params = {
        "originCityCode": "BLR",
        "destinationCityCode": "DXB",
        "period": "2025-01",
    }

    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(
            f"{BASE_V1}/travel/analytics/air-traffic/busiest-period",
            headers=headers,
            params=params,
        )

        # Sandbox limitation handling
        if r.status_code == 400:
            print(" BUSIEST PERIOD not supported in TEST environment")
            print(r.json())
            return

        r.raise_for_status()
        print(" BUSIEST TRAVEL PERIOD OK")
        print(r.json())


# -----------------------
# MAIN
# -----------------------
async def main():
    await test_token()
    await test_hotels_by_city()
    await test_transfer_search()
    await test_air_traffic_traveled()
    await test_busiest_travel_period()


if __name__ == "__main__":
    asyncio.run(main())
