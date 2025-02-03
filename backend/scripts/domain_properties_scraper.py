import json
import asyncio
import jmespath
from httpx import AsyncClient, Response
from parsel import Selector
from typing import List, Dict, Optional
import time
import os
import pandas as pd

client = AsyncClient(
    # enable http2
    http2=True,
    # add basic browser headers to minimize blocking chances
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
        phone: phone,
        agencyName: agencyName,
        propertyDeveloperName: propertyDeveloperName,
        agencyProfileUrl: agencyProfileUrl,
        propertyDeveloperUrl: propertyDeveloperUrl,
        loanfinder: loanfinder,
        agents: agents,
        features: features,
        structuredFeatures: structuredFeatures,
        schools: schoolCatchment.schools,
        suburbInsights: suburbInsights,
        gallery: gallery,
        faqs: faqs
        }""",
            data,
        )

        # Limit gallery slides to maximum 5 entries and modify image structure
        if result and "gallery" in result and "slides" in result["gallery"]:
            slides = result["gallery"]["slides"][:5]  # Limit to 5 slides

            # Modify each slide to only keep original image
            for slide in slides:
                if "images" in slide:
                    original = slide["images"].get("original", {})
                    slide["images"] = {"original": original}

            result["gallery"]["slides"] = slides

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
    return {"properties": [], "completed_suburbs": [], "last_suburb": None, "last_page": 1}


def save_to_json(data: Dict):
    """Save data to JSON file"""
    with open("domain_properties.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def has_more_pages(data: Dict) -> bool:
    """Check if there are more pages of results"""
    try:
        total_results = data.get("totalResults", 0)
        current_page = data.get("page", 1)
        results_per_page = len(data.get("listingsMap", {}))

        if results_per_page == 0:
            return False

        return (current_page * results_per_page) < total_results
    except Exception as e:
        print(f"Error checking for more pages: {e}")
        return False


async def scrape_properties_for_page(property_urls: List[str], batch_size: int = 10) -> List[Dict]:
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
                        print(f"\nSuccessfully scraped property:")
                        print(f"URL: {url}")
                        print(
                            f"Address: {property_data.get('streetNumber', '')} {property_data.get('street', '')}, {property_data.get('suburb', '')}"
                        )
                        print(f"Details: {property_data.get('beds', '')} beds, {property_data.get('baths', '')} baths")
                        print(f"Price: {property_data.get('price', 'Not specified')}")
                        print("-" * 50)
                else:
                    print(f"Failed to fetch property {url}: Status {response.status_code}")

            await asyncio.sleep(2)

        except Exception as e:
            print(f"Error processing batch: {e}")
            continue

    return page_properties


async def process_suburb(suburb: str, existing_data: Dict) -> None:
    """Process all pages for a single suburb"""
    base_url = f"https://www.domain.com.au/sale/{suburb}/?ptype=apartment-unit-flat,block-of-units,duplex,free-standing,new-apartments,new-home-designs,new-house-land,pent-house,semi-detached,studio,terrace,town-house,villa&establishedtype=established&ssubs=0"

    page = 1
    if existing_data["last_suburb"] == suburb:
        page = existing_data["last_page"]
        print(f"Resuming {suburb} from page {page}")

    while True:
        url = f"{base_url}&page={page}"
        print(f"\nProcessing {suburb} - Page {page}")

        try:
            response = await client.get(url)
            if response.status_code != 200:
                print(f"Failed to fetch page {page} for {suburb}: Status {response.status_code}")
                break

            data = parse_hidden_data(response)
            search_results = parse_search_page(data)

            if not search_results:
                print(f"No properties found on page {page} for {suburb}")
                break

            property_urls = [item["propertyUrl"] for item in search_results]

            # Filter out already scraped URLs
            existing_urls = {prop.get("scraped_url") for prop in existing_data["properties"]}
            new_urls = [url for url in property_urls if url not in existing_urls]

            if new_urls:
                page_properties = await scrape_properties_for_page(new_urls)
                existing_data["properties"].extend(page_properties)
                existing_data["last_suburb"] = suburb
                existing_data["last_page"] = page
                save_to_json(existing_data)
                print(f"Saved {len(page_properties)} new properties for {suburb} - Page {page}")

            if not has_more_pages(data):
                print(f"No more pages for {suburb}")
                break

            page += 1
            await asyncio.sleep(2)  # Delay between pages

        except Exception as e:
            print(f"Error processing page {page} for {suburb}: {e}")
            break

    existing_data["completed_suburbs"].append(suburb)
    existing_data["last_suburb"] = None
    existing_data["last_page"] = 1
    save_to_json(existing_data)


async def run():
    try:
        # Load suburbs from CSV
        suburbs_df = pd.read_csv("nsw_suburbs.csv")
        suburbs = suburbs_df["suburb"].tolist()

        # Load existing data
        existing_data = load_existing_data()

        # Filter out already completed suburbs
        remaining_suburbs = [s for s in suburbs if s not in existing_data["completed_suburbs"]]

        print(f"Starting scrape for {len(remaining_suburbs)} suburbs")

        for suburb in remaining_suburbs:
            print(f"\nStarting new suburb: {suburb}")
            await process_suburb(suburb, existing_data)
            print(f"Completed suburb: {suburb}")
            await asyncio.sleep(2)  # Delay between suburbs

        print(f"\nFinished scraping all suburbs. Total properties: {len(existing_data['properties'])}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        await client.aclose()


if __name__ == "__main__":
    asyncio.run(run())
