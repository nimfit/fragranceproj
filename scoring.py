
import fragrantica
from fragrantica import fragrantica_scrape
import pandas as pd
import ast
import math

def clean_csv(input_file, output_file):
    df = pd.read_csv(input_file)
    df.drop(['gender', 'is_disc'], axis=1, inplace=True) # Remove unnecessary columns
# Filter only rows that have data
    valid_frags = df[df['notes'].notnull() & df['accords'].notnull()]
    valid_frags = valid_frags[valid_frags['notes'] != "{'head': [], 'heart': [], 'base': []}"]

    valid_frags.to_csv(output_file, index=False)
    print(f"CSV cleaned and saved to {output_file}")

def score_single_fragrance(notes, accords, user_likes):
    user_likes = [x.lower() for x in user_likes]
    score = 0

    note_weights = {'head': 1, 'heart': 2, 'base': 3}

    # Score notes
    for note_type, weight in note_weights.items():
        for note in notes.get(note_type, []):
            if note.lower() in user_likes:
                score += weight

    # Score accords
    for accord, intensity in accords:
        if accord.lower() in user_likes:
            score += float(intensity) * 0.05

    return score


def score_fragrances(input_file, user_likes):
    df = pd.read_csv(input_file)
    df['score'] = 0
    #scores each fragrance based on the cached file
    cache_df = load_cache()
    for index, row in df.iterrows():
        fragrance_data = get_fragrance_data(row, cache_df)
        
        accords = ast.literal_eval(fragrance_data['accords']) if fragrance_data['accords'] else []
        notes = ast.literal_eval(fragrance_data['notes']) if fragrance_data['notes'] else {}
        try:
            rating = float(fragrance_data['rating']) if fragrance_data['rating'] else 0
        except (ValueError, TypeError):
            rating = 0
        score = 0
        score = score_single_fragrance(notes, accords, user_likes)
        df['score'] = df['score'].astype(float)
        new_score = math.trunc(score * 1000) / 1000
        df.at[index, 'score'] = new_score
     
    df.to_csv(input_file, index=False)
    print(f"Scoring complete. Updated scores saved to {input_file}")


def load_cache(cache_path="fragrance_cache.csv"):
    try:
        return pd.read_csv(cache_path)
    except FileNotFoundError:
        
        return pd.DataFrame(columns=['name', 'brand', 'accords', 'notes', 'rating', 'score', 'source', 'url'])

def update_cache(new_data, cache_path="fragrance_cache.csv"):
    cache = load_cache(cache_path)
    updated_cache = pd.concat([cache, new_data], ignore_index=True).drop_duplicates(subset='url')

    updated_cache = updated_cache[['name', 'brand', 'accords', 'notes', 'rating', 'score', 'source', 'url']]
    updated_cache.to_csv(cache_path, index=False)

def get_fragrance_data(row, cache_df):
    cached = cache_df[cache_df['url'] == row['url']]
    if not cached.empty:
        return cached.iloc[0]  # Return cached row 
    else:
        fragrance = fragrantica_scrape(row['url'])
       
        if fragrance.notes.get('head') or fragrance.accords:
            new_row = {
                'name': row.get('name', ''),
                'brand': row.get('brand', ''),
                'accords': str(fragrance.accords),
                'notes': str(fragrance.notes),
                'rating': getattr(fragrance, 'rating', ''),  
                'score': getattr(fragrance, 'score', ''),
                'source': getattr(fragrance, 'source', ''),
                'url': row['url']
            }
            update_cache(pd.DataFrame([new_row]))
            return new_row
        elif fragrance is None:
            print(f"Scrape failed for URL: {row['url']}")
            return None

if __name__ == "__main__":
    input_file = "fragrances.csv"
    output_file = "fragrances_cache.csv"

    clean_csv(input_file, output_file)
    
