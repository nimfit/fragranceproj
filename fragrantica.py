

import requests
from bs4 import BeautifulSoup




class Fragrance:
    def __init__(self, name, brand, accords=None, notes=None, rating=None, source='Fragrantica'):
        self.name = name
        self.brand = brand
        self.accords = accords if accords else []
        self.notes = notes if notes else {"head": [], "heart": [], "base": []}
        self.source = source
        self.score = 0
        self.rating = rating

    def set_score(self, user_likes):
        # Simple scoring logic — you can upgrade later
        score = 0
        if self.source == 'Fragrantica' or self.source == 'Basenotes':
            for note in self.notes.get('head', []):
                if note in user_likes:
                    score += 1
            for note in self.notes.get('heart', []):
                if note in user_likes:
                    score += 2
            for note in self.notes.get('base', []):
                if note in user_likes:
                    score += 3
        elif self.source == 'Parfumo':
            for note in self.notes.get('main', []):
                if note in user_likes:
                    score += 3
        self.score = score

    def to_dict(self):
        return {
            "name": self.name,
            "brand": self.brand,
            "accords": self.accords,
            "notes": self.notes,
            "rating": self.rating,
            "score": self.score,
            "source": self.source

        }
    
#Define the scraper function that tries to get data from fragrantica.com
def fragrantica_scrape(url):
    headers = {'User-Agent': 'Mozilla/5.0'} 
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract name
    name_tag = soup.find('h1', class_='text-center medium-text-left')
    name = name_tag.text.strip() if name_tag else "Unknown"

    # Extract brand
    brand_tag = soup.find('span', class_='vote-button-name')
    brand = brand_tag.text.strip() if brand_tag else "Unknown"

    # Extract accords
    accord_divs = soup.find_all("div", class_="accord-bar")
    accords = []
    for div in accord_divs:
        style = div.get("style", "")
        accord_name = div.text.strip()
        width = None
        if "width:" in style:
            try:
                width = float(style.split("width:")[1].split("%")[0].strip())
            except:
                width = None
        accords.append((accord_name, width))

    # Extract notes
    notes = {
        "head": [],
        "heart": [],
        "base": []
    }

    # Extract rating
    rating_tag = soup.find("span", itemprop="ratingValue")
    rating = float(rating_tag.text.strip()) if rating_tag else None


    # Try to extract from visual note blocks
    note_sections = soup.find_all("div", class_="cell small-12")
    try:
        note_block = note_sections[4]
        note_divs = note_block.find_all("div", class_="fragrance_note")
        current_section = "head"
        for note_div in note_divs:
            header = note_div.find_previous("h3")
            if header:
                header_text = header.text.lower()
                if "top" in header_text:
                    current_section = "head"
                elif "middle" in header_text:
                    current_section = "heart"
                elif "base" in header_text:
                    current_section = "base"
            note_name = note_div.text.strip().lower()
            notes[current_section].append(note_name)
    except IndexError:
        print("Couldn't locate visual notes section.")

    # Fallback: Extract notes from the description paragraph
    description_tag = soup.find("div", itemprop="description")
    if description_tag:
        desc_text = description_tag.get_text(separator=" ", strip=True)

        import re
        def split_notes(raw):
            return [note.strip() for note in re.split(r",| and ", raw)] if raw else []

        match_top = re.search(r"Top notes are (.*?);", desc_text)
        match_middle = re.search(r"middle notes are (.*?);", desc_text)
        match_base = re.search(r"base notes are (.*?)(\.|$)", desc_text)

        if match_top:
            notes["head"] = split_notes(match_top.group(1))
        if match_middle:
            notes["heart"] = split_notes(match_middle.group(1))
        if match_base:
            notes["base"] = split_notes(match_base.group(1))

    # Create and return the Fragrance object
    return Fragrance(name=name, brand=brand, accords=accords, notes=notes, rating=rating, source="Fragrantica")



