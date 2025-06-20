from fragrantica import Fragrance, fragrantica_scrape

urls = [
    "https://www.fragrantica.com/perfume/Gulf-Orchid/Mango-Ice-103445.html",
    "https://www.fragrantica.com/perfume/L-Occitane-en-Provence/Notre-Flore-Cedar-2009.html#cc2611673",
    "https://www.fragrantica.com/perfume/L-Occitane-en-Provence/Neroli-Orchidee-24457.html",
    "https://www.fragrantica.com/perfume/BDK-Parfums/Rouge-Smoking-51468.html#cc2611662",
    "https://www.fragrantica.com/perfume/Louis-Vuitton/Imagination-67370.html#cc2611658"
]

def batch_scrape_fragranntica(urls):
    fragrances = []
    for url in urls:
        try:
            frag = fragrantica_scrape(url)
            fragrances.append(frag)
            print(f"✔️ Scraped: {frag.name}")
        except Exception as e:
            print(f"❌ Failed to scrape {url}: {e}")
    return fragrances

if __name__ == "__main__":
    scraped_fragrances = batch_scrape_fragranntica(urls)
    for sf in scraped_fragrances:
        print(sf.to_dict())





