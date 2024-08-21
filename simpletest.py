import requests
from bs4 import BeautifulSoup
from googleapiclient.discovery import build

google_cse_id = os.getenv("GOOGLE_CSE_ID")
google_cse_api_key = os.getenv("GOOGLE_CSE_API_KEY")


def extract_hyperlinks(cse_response):
    items = cse_response.get('items', [])
    links = [item['link'] for item in items if 'link' in item]
    return links


def scrape_google(query):
    htmls = [""]
    htmls_text = [""]
    service = build("customsearch", "v1", developerKey=google_cse_api_key)
    res = service.cse().list(q=query, cx=google_cse_id, num=10).execute()
    links = extract_hyperlinks(res)
    for items in links:
        try:
            response = requests.get(items)
            response.raise_for_status()
            content_type = response.headers.get('Content-Type', '')
            if "text" in content_type.lower():
                soup = BeautifulSoup(response.text,"html")
                text = soup.get_text(separator="\n", strip=True)
                htmls_text.append(text)
            else :
                htmls_text.append(f"Wrong content type: {content_type}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve {items}: {e}")
            htmls_text.append(f"Failed to retrieve {items}: {e}")
    return htmls_text

