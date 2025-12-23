import asyncio
import json
from amadeus import get_flight_status

async def main():
    print("🔍 Calling Flight Status API...")

    data = await get_flight_status(
        carrier_code="EK",
        flight_number="202",
        departure_date="2025-12-25"
    )

    print("✅ Raw API Response:")
    print(json.dumps(data, indent=2))

    if not data.get("data"):
        print("⚠️ No flight data returned (normal in test env).")
        return

    for flight in data["data"]:
        print(
            f"{flight['carrierCode']}{flight['flightNumber']} | "
            f"{flight['status']}"
        )

if __name__ == "__main__":
    asyncio.run(main())
