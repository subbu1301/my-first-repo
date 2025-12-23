import asyncio
import json
from amadeus import search_multicity_india


async def main():
    print("Searching multi-city flights in India...\n")

    data = await search_multicity_india()

    # Pretty-print full response (large)
    print("RAW API RESPONSE:\n")
    print(json.dumps(data, indent=2))

    # Optional: extract readable summary
    print("\n\nSUMMARY:\n")

    for offer in data.get("data", []):
        price = offer["price"]["grandTotal"]
        currency = offer["price"]["currency"]
        print(f"Total Price: {price} {currency}")

        for idx, itin in enumerate(offer["itineraries"], start=1):
            print(f"  Itinerary {idx}:")
            for seg in itin["segments"]:
                print(
                    f"    {seg['departure']['iataCode']} → {seg['arrival']['iataCode']} | "
                    f"{seg['carrierCode']}{seg['number']} | "
                    f"{seg['departure']['at']} → {seg['arrival']['at']}"
                )

        print("-" * 60)


asyncio.run(main())
