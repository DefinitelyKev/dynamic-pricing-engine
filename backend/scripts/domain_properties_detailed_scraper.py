import json
import asyncio
from httpx import AsyncClient, Response
from parsel import Selector
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse, unquote
import re

client = AsyncClient(
    http2=True,
    headers={
        "accept-language": "en-US,en;q=0.9",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "accept-encoding": "gzip, deflate, br",
    },
)


def extract_property_path(url: str) -> Optional[str]:
    """Extract the property path from a Domain.com.au URL."""
    try:
        parsed = urlparse(url)
        path = parsed.path
        # Remove the listing ID from the end if it exists
        path = re.sub(r"-\d+$", "", path.rstrip("/"))
        # Remove leading slash if present
        return path.lstrip("/")
    except Exception as e:
        print(f"Error extracting property path from {url}: {e}")
        return None


def parse_property_page(data: Dict, suburb_insights: Dict) -> Optional[Dict]:
    """Parse property data from Apollo state and add suburb insights"""
    parsed_data = parse_property_page_base(data)

    if parsed_data:
        # Add suburb insights to the parsed data
        parsed_data["suburbInsights"] = suburb_insights

    return parsed_data


def parse_property_page_base(data: Dict) -> Optional[Dict]:
    """Base parser function from the original scraper"""
    if not data or not data.get("__APOLLO_STATE__"):
        return None

    apollo_state = data["__APOLLO_STATE__"]
    property_key = next((key for key in apollo_state.keys() if key.startswith("Property:")), None)

    if not property_key:
        return None

    # Rest of your existing parse_property_page function...
    # [Previous implementation remains the same]
    property_data = apollo_state[property_key]

    listing = property_data.get("listings", [{}])[0] if property_data.get("listings") else {}
    valuation = property_data.get("valuation", {})
    media = property_data.get('media({"categories":["IMAGE"]})', [])

    images = list(dict.fromkeys([img.get("url") for img in media if img.get("url")]))[:5]

    address = property_data.get("address", {})
    suburb_data = address.get("suburb", {})

    schools = []
    for school in property_data.get("schools", [])[:4]:
        school_data = school.get("school", {})
        profile = school_data.get("profile") or {}
        schools.append(
            {
                "name": school_data.get("name"),
                "type": school_data.get("schoolType"),
                "sector": school_data.get("schoolSector"),
                "gender": school_data.get("gender"),
                "suburb": school_data.get("suburb"),
                "distance": round(school.get("distance", 0), 2),
                "yearRange": profile.get("yearRange"),
            }
        )

    timeline = []
    for event in property_data.get("timeline", []):
        if event.get("isMajorEvent"):
            agency_profile = event.get("agency") or {}
            timeline.append(
                {
                    "eventPrice": event.get("eventPrice"),
                    "eventDate": event.get("eventDate"),
                    "agency": agency_profile.get("name"),
                    "category": event.get("category"),
                    "daysOnMarket": event.get("daysOnMarket"),
                    "priceDescription": event.get("priceDescription"),
                }
            )

    location_profile = property_data.get("locationProfile") or {}
    location_data = location_profile.get("data", {})

    market_stats = {
        "apartmentsAndUnits": {
            "forRent": location_data.get("apartmentsAndUnitsForRent", 0),
            "forSale": location_data.get("apartmentsAndUnitsForSale", 0),
        },
        "houses": {
            "forRent": location_data.get("housesForRent", 0),
            "forSale": location_data.get("housesForSale", 0),
        },
        "townhouses": {
            "forRent": location_data.get("townhousesForRent", 0),
            "forSale": location_data.get("townhousesForSale", 0),
        },
    }

    geolocation = address.get("geolocation")

    return {
        "propertyId": property_data.get("propertyId"),
        "type": property_data.get("type"),
        "category": property_data.get("category"),
        "specifications": {
            "bedrooms": property_data.get("bedrooms"),
            "bathrooms": property_data.get("bathrooms"),
            "parkingSpaces": property_data.get("parkingSpaces"),
            "internal_area": property_data.get('internalArea({"unit":"SQUARE_METERS"})'),
            "land_area": property_data.get('landArea({"unit":"SQUARE_METERS"})'),
        },
        "address": {
            "displayAddress": address.get("displayAddress"),
            "postcode": address.get("postcode"),
            "suburbName": address.get("suburbName"),
            "state": address.get("state"),
            "unitNumber": address.get("unitNumber"),
            "streetNumber": address.get("streetNumber"),
            "streetName": address.get("streetName"),
            "streetType": address.get("streetTypeLong"),
            "geolocation": (
                {"latitude": geolocation.get("latitude"), "longitude": geolocation.get("longitude")}
                if geolocation
                else None
            ),
        },
        "location": {
            "suburb": {
                "name": suburb_data.get("name"),
                "state": suburb_data.get("state"),
                "region": suburb_data.get("region"),
                "area": suburb_data.get("area"),
                "postcode": suburb_data.get("postcode"),
            },
            "surroundingSuburbs": [
                s.get("name") for s in property_data.get("locationProfile", {}).get("surroundingSuburbs", [])
            ],
        },
        "marketStats": market_stats,
        "listing": {
            "id": listing.get("listingId"),
            "url": listing.get("seoUrl"),
            "status": listing.get("status"),
            "type": listing.get("type"),
            "displayPrice": listing.get("priceDetails", {}).get("displayPrice"),
        },
        "valuation": {
            "lowerPrice": valuation.get("lowerPrice"),
            "midPrice": valuation.get("midPrice"),
            "upperPrice": valuation.get("upperPrice"),
            "confidence": valuation.get("priceConfidence"),
            "date": valuation.get("date"),
        },
        "timeline": timeline,
        "schools": schools,
        "images": images,
    }


def parse_hidden_data(response: Response) -> Dict:
    """Parse JSON data from script tags"""
    selector = Selector(response.text)
    script = selector.xpath("//script[@id='__NEXT_DATA__']/text()").get()

    if script is None:
        raise ValueError("Could not find __NEXT_DATA__ script tag")

    data = json.loads(script)

    # Navigate to the pageProps which contains the Apollo state
    if "props" in data and "pageProps" in data["props"]:
        return data["props"]["pageProps"]

    raise ValueError("Unexpected data structure in __NEXT_DATA__")


async def scrape_property_profiles(properties: List[Dict]) -> Tuple[List[Dict], List[str]]:
    """Scrape detailed property data and track failed URLs"""
    detailed_properties = []
    failed_urls = []

    for property_data in properties:
        listing_url = property_data.get("listingUrl")
        if not listing_url:
            continue

        property_path = extract_property_path(listing_url)
        if not property_path:
            failed_urls.append(listing_url)
            continue

        profile_url = f"https://www.domain.com.au/property-profile/{property_path}"

        try:
            response = await client.get(profile_url)
            if response.status_code != 200:
                failed_urls.append(listing_url)
                print(f"Failed to fetch {profile_url}: Status code {response.status_code}")
                continue

            data = parse_hidden_data(response)
            suburb_insights = property_data.get("suburbInsights", {})
            parsed_data = parse_property_page(data, suburb_insights)

            if parsed_data:
                parsed_data["original_listing_url"] = listing_url
                detailed_properties.append(parsed_data)
                print(f"Successfully scraped property profile: {profile_url}")
            else:
                failed_urls.append(listing_url)
                print(f"Failed to parse property data: {profile_url}")

        except Exception as e:
            failed_urls.append(listing_url)
            print(f"Error processing {profile_url}: {e}")

    return detailed_properties, failed_urls


async def main():
    # Load the original properties data
    with open("domain_properties.json", "r") as f:
        properties_data = json.load(f)

    properties = properties_data.get("properties", [])
    print(f"Loaded {len(properties)} properties from domain_properties.json")

    # Scrape detailed property data
    detailed_properties, failed_urls = await scrape_property_profiles(properties)

    # Save the detailed property data
    with open("domain_properties_detailed.json", "w") as f:
        json.dump({"properties": detailed_properties}, f, indent=2)

    # Save the failed URLs
    with open("failed_urls.json", "w") as f:
        json.dump({"failed_urls": failed_urls}, f, indent=2)

    print(f"\nProcess completed:")
    print(f"Successfully scraped {len(detailed_properties)} properties")
    print(f"Failed to scrape {len(failed_urls)} properties")
    print("Results saved to domain_properties_detailed.json")
    print("Failed URLs saved to failed_urls.json")


if __name__ == "__main__":
    asyncio.run(main())
