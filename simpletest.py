import os
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from dotenv import load_dotenv

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}
load_dotenv()
google_cse_id = os.getenv("GOOGLE_CSE_ID")
google_cse_api_key = os.getenv("GOOGLE_CSE_API_KEY")

async def fetch_url(url, headers):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()  # Ensure we raise an exception for HTTP errors
                return await response.text()  # Get the text content of the response
    except aiohttp.ClientError as e:
        print(f"Client error occurred while fetching {url}: {e}")
        return None
    except asyncio.TimeoutError:
        print(f"Request timed out for {url}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while fetching {url}: {e}")
        return None

def extract_hyperlinks(cse_response):
    items = cse_response.get('items', [])
    links = [item['link'] for item in items if 'link' in item]
    return links

async def scrape_google(query):
    htmls_text = []
    service = build("customsearch", "v1", developerKey=google_cse_api_key)
    res = service.cse().list(q=query, cx=google_cse_id, num=10).execute()
    links = extract_hyperlinks(res)
    
    for item in links:
        try:
            response_text = await fetch_url(item, headers)
            if response_text is None:
                continue  # Skip processing if fetch_url failed
            
            # Parse the HTML content
            soup = BeautifulSoup(response_text, "html.parser")
            page_text = soup.get_text(separator="\n", strip=True)
            
            htmls_dict = {"url": item, "text": page_text}
            htmls_text.append(htmls_dict)
        
        except Exception as e:
            print(f"An error occurred while processing {item}: {e}")
            continue  # Continue with the next link even if there's an error
    
    return htmls_text

async def main():
    query = "What is the capital of France?"
    results = await scrape_google(query)
    for result in results:
        print(result)

if __name__ == "__main__":
    asyncio.run(main())
