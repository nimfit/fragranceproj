import fragrantica_collection
import scoring
from fragrantica import fragrantica_scrape
import pandas as pd

def main():
    #Asks for user preferences
    user_likes = input("Enter your preferred fragrance notes (comma-separated): ").split(',')
    user_likes = [note.strip().lower() for note in user_likes if note.strip()]

    # Score the fragrances based on user preferences
    print("Scoring the fragrances...")
    scoring.score_fragrances("cleaned_fragrances.csv", user_likes)

    print("Based off of your preferences, the top 5 fragrances for you are:")
    df = pd.read_csv("cleaned_fragrances.csv")
    top_fragrances = df.nlargest(5, 'score')

    for index, row in top_fragrances.iterrows():
        print(f"{index + 1}. {row['name']} by {row['brand']} - Score: {row['score']:.2f}")

if __name__ == "__main__":
    main()
    """
    This script collects fragrance data from Fragrantica, cleans it, and scores it based on user preferences.
    It then outputs the top 5 fragrances that match the user's preferences.
    """

