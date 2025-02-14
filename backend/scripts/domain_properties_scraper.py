import json
import asyncio
import jmespath
from httpx import AsyncClient, Response
from parsel import Selector
from typing import List, Dict, Optional
import os

client = AsyncClient(
    # enable http2
    http2=True,
    headers={
        "accept-language": "en-US,en;q=0.9",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "accept-language": "en-US;en;q=0.9",
        "accept-encoding": "gzip, deflate, br",
    },
    timeout=30.0,  # Add timeout to prevent hanging
)


def parse_search_page(data: Dict) -> List[Dict]:
    """Parse search pages data and extract property URLs"""
    if not data:
        return []

    listings_map = data.get("listingsMap", {})
    result = []

    for listing_id in listings_map.keys():
        item = listings_map[listing_id]
        if "listingModel" in item and "url" in item["listingModel"]:
            property_url = f"https://www.domain.com.au{item['listingModel']['url']}"
            result.append({"id": listing_id, "listingType": item.get("listingType"), "propertyUrl": property_url})

    return result


def parse_property_page(data: Dict) -> Optional[Dict]:
    """Parse detailed property data"""
    if not data:
        return None

    try:
        result = jmespath.search(
            """{
        listingId: listingId,
        listingUrl: listingUrl,
        unitNumber: unitNumber,
        streetNumber: streetNumber,
        street: street,
        suburb: suburb,
        postcode: postcode,
        createdOn: createdOn,
        propertyType: propertyType,
        beds: listingSummary.beds,
        baths: listingSummary.baths,
        parking: listingSummary.parking,
        price: listingSummary.title,
        listingSummary: listingSummary,
        loanfinder: loanfinder,
        features: features,
        structuredFeatures: structuredFeatures,
        suburbInsights: suburbInsights,
        schools: schoolCatchment.schools,
        gallery: gallery
        }""",
            data,
        )

        # Limit gallery slides to maximum 5 entries and keep only image urls
        if result and "gallery" in result and "slides" in result["gallery"]:
            slides = result["gallery"]["slides"][:5]  # Limit to 5 slides

            image_urls = []
            for slide in slides:
                if "images" in slide:
                    original = slide["images"].get("original", {})
                    image_urls.append(original.get("url", ""))

            result["gallery"] = image_urls

        return result
    except Exception as e:
        print(f"Error parsing property page: {e}")
        return None


def parse_hidden_data(response: Response) -> Dict:
    """Parse JSON data from script tags"""
    selector = Selector(response.text)
    script = selector.xpath("//script[@id='__NEXT_DATA__']/text()").get()

    if not script:
        raise ValueError("Could not find __NEXT_DATA__ script tag")

    data = json.loads(script)
    return data["props"]["pageProps"]["componentProps"]


def load_existing_data() -> Dict:
    """Load existing data from JSON file if it exists"""
    if os.path.exists("domain_properties.json"):
        with open("domain_properties.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {"properties": [], "completed_price_ranges": []}


def save_to_json(data: Dict):
    """Save data to JSON file"""
    with open("domain_properties.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def has_more_pages(data: Dict, page: int) -> bool:
    """Check if there are more pages of results"""

    PROPERTIES_PER_PAGE = 20
    try:
        # Getting total pages by ceiling property count division
        property_count = sum(data["propertyCounts"].values())
        return page <= -(property_count // -PROPERTIES_PER_PAGE)

    except Exception as e:
        print(f"Error checking for more pages: {e}")
        return False


async def scrape_properties_for_page(property_urls: List[str], batch_size: int = 20) -> List[Dict]:
    """Scrape detailed property data for a single page's worth of properties"""
    page_properties = []

    for i in range(0, len(property_urls), batch_size):
        batch_urls = property_urls[i : i + batch_size]
        tasks = [client.get(url) for url in batch_urls]

        try:
            responses = await asyncio.gather(*tasks)
            for response, url in zip(responses, batch_urls):
                if response.status_code == 200:
                    data = parse_hidden_data(response)
                    property_data = parse_property_page(data)
                    if property_data:
                        property_data["scraped_url"] = url
                        page_properties.append(property_data)
                else:
                    print(f"Failed to fetch property {url}: Status {response.status_code}")

            await asyncio.sleep(1)

        except Exception as e:
            print(f"Error processing batch: {e}")
            continue

    return page_properties


async def process_price_range(low_price: str, high_price: str, existing_data: Dict) -> None:
    """Process all pages for a single suburb"""
    base_url = f"https://www.domain.com.au/sale/?ptype=house&price={low_price}-{high_price}&establishedtype=established&ssubs=0&sort=price-asc&state=nsw"

    page = 1
    while True:
        url = f"{base_url}&page={page}"
        print(f"\nProcessing ${low_price} - ${high_price} - Page {page}")

        try:
            response = await client.get(url)
            if response.status_code != 200:
                print(f"Failed to fetch page {page} for ${low_price} - ${high_price}: Status {response.status_code}")
                break

            data = parse_hidden_data(response)
            search_results = parse_search_page(data)

            if not search_results:
                print(f"No properties found on page {page} for range ${low_price} - ${high_price}")
                break

            # Filter out already scraped URLs
            property_urls = [item["propertyUrl"] for item in search_results]
            existing_urls = {prop.get("scraped_url") for prop in existing_data["properties"]}
            new_urls = [url for url in property_urls if url not in existing_urls]

            if new_urls:
                page_properties = await scrape_properties_for_page(new_urls)
                existing_data["properties"].extend(page_properties)
                save_to_json(existing_data)
                print(f"Saved {len(page_properties)} new properties for range ${low_price} - ${high_price}")

            page += 1

            if not has_more_pages(data, page):
                print(f"No more pages for range ${low_price} - ${high_price}")
                break

            await asyncio.sleep(1)  # Delay between pages

        except Exception as e:
            print(f"Error processing page {page} for range ${low_price} - ${high_price}: {e}")
            break

    existing_data["completed_price_ranges"].append(f"{low_price}-{high_price}")
    save_to_json(existing_data)


async def run():
    try:
        existing_data = load_existing_data()

        low_price = 0
        for high_price in range(50000, 12000000, 50000):
            await process_price_range(str(low_price), str(high_price), existing_data)
            low_price = high_price
            await asyncio.sleep(1)

        print(f"\nFinished scraping all properties. Total properties: {len(existing_data['properties'])}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        await client.aclose()


if __name__ == "__main__":
    asyncio.run(run())
