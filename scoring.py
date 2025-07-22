
import fragrantica
from fragrantica import fragrantica_scrape
import pandas as pd

def clean_csv(input_file, output_file):
    df = pd.read_csv(input_file)
    df.drop(['gender', 'is_disc'], axis=1, inplace=True) # Remove unnecessary columns
# Filter only rows that have data
    valid_frags = df[df['notes'].notnull() & df['accords'].notnull()]
    valid_frags = valid_frags[valid_frags['notes'] != "{'head': [], 'heart': [], 'base': []}"]

    valid_frags.to_csv(output_file, index=False)
    print(f"CSV cleaned and saved to {output_file}")


def score_fragrances(input_file, user_likes):
    df = pd.read_csv(input_file)
    df['score'] = 0

    for index, row in df.iterrows():
        fragrance = fragrantica_scrape(row['url'])
        #Set the score based on user preferences
        fragrance.set_score(user_likes)

        df['score'] = df['score'].astype(float)  
        df.at[index, 'score'] = float(fragrance.score)

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
        else:
            return None

if __name__ == "__main__":
    input_file = "fragrances.csv"
    output_file = "fragrances_cache.csv"

    clean_csv(input_file, output_file)


