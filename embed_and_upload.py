
# This script does 3 things:
#   1. Loads all 24,063 colognes from our cleaned CSV
#   2. Converts each cologne's embedding_text into a vector
#      using a lightweight AI model (all-MiniLM-L6-v2)
#   3. Uploads everything to Supabase in batches of 100
#
# Run this ONCE to seed the database. Don't run it again
# unless you drop and recreate the table.

import pandas as pd
from sentence_transformers import SentenceTransformer
from supabase import create_client
from dotenv import load_dotenv
import os
import time


# load env variables from .env file
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("Missing SUPABASE_URL or SUPABASE_KEY in .env file")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
df = pd.read_csv('data/fragrances_clean.csv',encoding = 'utf-8')
df = df.where(pd.notna(df),None)

model = SentenceTransformer('all-MiniLM-L6-v2')

BATCH_SIZE = 100
total = len(df)
success_count = 0
error_count = 0

for i in range(0, total, BATCH_SIZE):
    # Grab the next batch of rows
    batch = df.iloc[i:i + BATCH_SIZE]

    # Build the list of embedding texts for this batch
    texts = batch['embedding_text'].fillna('').tolist()

    # Convert texts to vectors all at once (faster than one at a time)
    embeddings = model.encode(texts, show_progress_bar=False)

    # Build the list of rows to insert into Supabase
    rows = []
    for j, (_, row) in enumerate(batch.iterrows()):
        rows.append({
            "url":            row['url'],
            "name":           row['name'],
            "brand":          row['brand'],
            "country":        row['country'],
            "gender":         row['gender'],
            "rating":         row['rating'],
            "rating_count": int(row['rating_count']) if pd.notna(row['rating_count']) and row['rating_count'] else None,
            "year": int(row['year']) if pd.notna(row['year']) and row['year'] else None,
            "notes_top":      row['notes_top'],
            "notes_middle":   row['notes_middle'],
            "notes_base":     row['notes_base'],
            "accords":        row['accords'],
            "embedding_text": row['embedding_text'],
            # Convert numpy array to plain Python list for Supabase
            "embedding":      embeddings[j].tolist()
        })

    # Upload this batch to Supabase
    try:
        supabase.table("colognes").upsert(rows).execute()
        success_count += len(rows)
        print(f"  Uploaded batch {i // BATCH_SIZE + 1} — "
              f"{min(i + BATCH_SIZE, total)}/{total} colognes "
              f"({int(min(i + BATCH_SIZE, total) / total * 100)}%)")
    except Exception as e:
        error_count += len(rows)
        print(f"  ERROR on batch {i // BATCH_SIZE + 1}: {e}")

    # Small pause between batches to avoid overwhelming the API
    time.sleep(0.5)