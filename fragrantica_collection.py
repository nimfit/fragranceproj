from fragrantica import Fragrance, fragrantica_scrape

import requests
from bs4 import BeautifulSoup

import time
import random
import json
import os
import pandas as pd

BATCH_SIZE = 10
MIN_DELAY = 5
MAX_DELAY = 10
SAVE_FILE = "scraped_fragrances.json"
HEADERS = {'User-Agent': 'Mozilla/5.0'}


def get_designer_list():
    url = "https://www.fragrantica.com/designers/"
   
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')

    designer_links = soup.select("div.designerlist a")
    designers = []
    for link in designer_links:
        href = link.get("href")
        if href and href.startswith("/designers/"):
            designer_url = "https://www.fragrantica.com" + href
            designer_name = href.replace("/designers/", "").replace(".html", "")
            designers.append((designer_name, designer_url))

    return designers


def extract_designerurls(designer_url):
    res = requests.get(designer_url, headers=HEADERS)
    soup = BeautifulSoup(res.text, 'html.parser')

    urls = []

    fragrance_links = soup.select('a[href^="/perfume/"]')
    for link in fragrance_links:
        href = link.get('href')
        if href and href.startswith('/perfume/'):
            full_url = f"https://www.fragrantica.com{href}"
            urls.append(full_url)

    return list(set(urls))  # Remove duplicates

def is_designer_fragrance(url, designer_name):
    return f"/perfume/{designer_name.strip()}/" in url

def clean_fragrance_batch(urls, designer_name):
    return [url for url in urls if is_designer_fragrance(url, designer_name)]


def batch_scrape_fragrantica(urls):
    fragrances = []
    for url in urls:
        try:
            frag = fragrantica_scrape(url)
            if frag.name.strip().lower() == "unknown":
                print(f"Blocked or invalid response at {url}, stopping early")
                break

            frag_dict = frag.to_dict()
            frag_dict["url"] = url
            fragrances.append(frag_dict)

            print(f"✔️ Scraped: {frag.name}")

            with open(SAVE_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(frag_dict) + "\n")


            time.sleep(random.uniform(8,15))



        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")
            break

    return fragrances

def save_data(data, filename=SAVE_FILE):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def load_data(filename=SAVE_FILE):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return []



if __name__ == "__main__":

    with open("scraped_fragrances.json", "r") as f:
        data = [json.loads(line) for line in f]

    df = pd.DataFrame(data)
    df.to_csv("fragrances.csv", index=False)
    print("✅ Exported to 'fragrances.csv'")
    """

    all_designers = get_designer_list()
    all_fragrances = load_data()
    scraped_urls = {f.get('url') for f in all_fragrances}


    for i in range(0, len(all_designers), BATCH_SIZE):
        batch = all_designers[i:i + BATCH_SIZE]
        print(f"📦 Processing batch {i // BATCH_SIZE + 1} of {len(all_designers) // BATCH_SIZE + 1}")

        for designer_name, url in batch:
            print(f"Scraping designer: {designer_name}")
            try:
              designer_urls = extract_designerurls(url)
              cleaned_urls = [u for u in clean_fragrance_batch(designer_urls, designer_name) if u not in scraped_urls]
              print(f"Found {len(cleaned_urls)} fragrances for {designer_name}")

              scraped_fragrances = batch_scrape_fragrantica(cleaned_urls)
              all_fragrances.extend(scraped_fragrances)

            except Exception as e:
                print(f"Error for {designer_name}: {e}")

            sleep_time = random.uniform(MIN_DELAY, MAX_DELAY)
            print(f"Sleeping {sleep_time:.2f} sec before next designer...")
            time.sleep(sleep_time)

        print("Batch saved. Cooling off before next batch...")
        time.sleep(random.uniform(30,60))

    print("All designer batches completed and saved")
    """
  




      
        

   





  





