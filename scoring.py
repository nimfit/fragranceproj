
import fragrantica
from fragrantica import fragrantica_scrape
import pandas as pd

def clean_csv(input_file, output_file):
    df = pd.read_csv(input_file)
    df = df.drop(columns=['gender', 'is_disc'])
    #clean more later
    df.to_csv(output_file, index=False)


def score_fragrances(input_file, user_likes):
    df = pd.read_csv(input_file)
    df['score'] = 0

    for index, row in df.iterrows():
        fragrance = fragrantica_scrape(row['url'])
        fragrance.set_score(user_likes)
        df['score'] = df['score'].astype(float)  
        df.at[index, 'score'] = float(fragrance.score)

    df.to_csv(input_file, index=False)
    print(f"Scoring complete. Updated scores saved to {input_file}")


'''
if __name__ == "__main__":
    input_file = "fragrances.csv"
    output_file = "cleaned_fragrances.csv"
    user_likes = ["aromatic", "citrus", "aquatic"]  # Example user preferences

    clean_csv(input_file, output_file)
    score_fragrances(output_file, user_likes)
    print("All operations completed successfully.")
    '''