import asyncio
import json
from amadeus import get_airline_routes


async def main():
    print("Fetching airline routes for EK...\n")

    response = await get_airline_routes("EK")

    # DEBUG: show full response structure
    print("Raw response:")
    print(json.dumps(response, indent=2))

    routes = response.get("data", [])

    if not routes:
        print("\n No routes returned (normal in test env)")
        return

    print("\n Routes:")
    for route in routes:
        origin = route.get("originCode")
        destination = route.get("destinationCode")
        print(f" {origin} → {destination}")


if __name__ == "__main__":
    asyncio.run(main())
