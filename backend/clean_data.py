import pandas as pd

# ============================================================
# Takes the raw Fragrantica CSV (semicolon-separated) and:
#   1. Renames columns to clean snake_case names
#   2. Fixes European decimal ratings (1,42 -> 1.42)
#   3. Drops rows with no name/brand or no notes at all
#   4. Combines the 5 accord columns into one string
#   5. Builds an "embedding_text" field per cologne — this is
#      the rich text string we'll turn into a vector later
#   6. Saves the cleaned data to data/fragrances_clean.csv
#   7. Lets you search for any cologne by name to verify data
# ============================================================

print("[1/4] Loading dataset...")
df = pd.read_csv(
    'data/fragrantica_dataset.csv',
    sep=';',                        # File uses semicolons not commas
    encoding='utf-8',
    encoding_errors='replace'       # Handle special characters like é, ü
)
print(f"  Loaded {len(df)} rows, {len(df.columns)} columns")
print(f"  Columns: {df.columns.tolist()}")

print("[2/4] Cleaning data...")

# Rename all columns to consistent snake_case so they're easier to work with
df = df.rename(columns={
    'Perfume': 'name',
    'Brand': 'brand',
    'Country': 'country',
    'Gender': 'gender',
    'Rating Value': 'rating',
    'Rating Count': 'rating_count',
    'Year': 'year',
    'Top': 'notes_top',
    'Middle': 'notes_middle',
    'Base': 'notes_base',
    'Perfumer1': 'perfumer1',
    'Perfumer2': 'perfumer2',
    'mainaccord1': 'accord1',
    'mainaccord2': 'accord2',
    'mainaccord3': 'accord3',
    'mainaccord4': 'accord4',
    'mainaccord5': 'accord5',
})

# Fix European decimal format: "1,42" -> 1.42 so it reads as a real number
df['rating'] = df['rating'].astype(str).str.replace(',', '.', regex=False)
df['rating'] = pd.to_numeric(df['rating'], errors='coerce')

# Drop rows missing a name or brand — useless without these
before = len(df)
df = df[df['name'].notna() & df['brand'].notna()]
print(f"  Dropped {before - len(df)} rows missing name/brand")

# Drop rows with absolutely no notes in any category
before = len(df)
df = df[df['notes_top'].notna() | df['notes_middle'].notna() | df['notes_base'].notna()]
print(f"  Dropped {before - len(df)} rows with no notes")

# Strip extra whitespace from name and brand
df['name'] = df['name'].str.strip()
df['brand'] = df['brand'].str.strip()

# Combine the 5 separate accord columns into one comma-separated string
# e.g. accord1="woody", accord2="amber" -> accords="woody, amber"
def combine_accords(row):
    accords = [row.get(f'accord{i}', '') for i in range(1, 6)]
    accords = [a for a in accords if pd.notna(a) and str(a).strip() != '']
    return ', '.join(accords)

df['accords'] = df.apply(combine_accords, axis=1)

# Build the embedding text for each cologne
# This single string is what gets converted into a vector later
# The richer this text is, the better the similarity results will be
def build_embedding_text(row):
    parts = []
    parts.append(f"{row['name']} by {row['brand']}")
    if pd.notna(row.get('accords')) and row['accords']:
        parts.append(f"Accords: {row['accords']}")
    if pd.notna(row.get('notes_top')) and str(row['notes_top']).strip():
        parts.append(f"Top notes: {row['notes_top']}")
    if pd.notna(row.get('notes_middle')) and str(row['notes_middle']).strip():
        parts.append(f"Middle notes: {row['notes_middle']}")
    if pd.notna(row.get('notes_base')) and str(row['notes_base']).strip():
        parts.append(f"Base notes: {row['notes_base']}")
    return '. '.join(parts)

df['embedding_text'] = df.apply(build_embedding_text, axis=1)

print("[3/4] Keeping only useful columns...")
df_clean = df[[
    'url', 'name', 'brand', 'country', 'gender',
    'rating', 'rating_count', 'year',
    'notes_top', 'notes_middle', 'notes_base',
    'accords', 'embedding_text'
]].copy()

print("[4/4] Saving cleaned dataset...")
df_clean.to_csv('data/fragrances_clean.csv', index=False, encoding='utf-8')
print(f"  Done! Saved {len(df_clean)} colognes to data/fragrances_clean.csv")

# ============================================================
# SEARCH TEST — verify a specific cologne is in the dataset
# Change the search term below to look up any cologne you want
# ============================================================
print("\n" + "="*50)
print("SEARCH TEST")
print("="*50)

search_term = "sauvage"   # <-- change this to search for any cologne

# Case-insensitive search across both name and brand
results = df_clean[
    df_clean['name'].str.contains(search_term, case=False, na=False) |
    df_clean['brand'].str.contains(search_term, case=False, na=False)
]

if results.empty:
    print(f"  No results found for '{search_term}'")
else:
    print(f"  Found {len(results)} result(s) for '{search_term}':\n")
    for _, row in results.iterrows():
        print(f"  NAME:    {row['name']}")
        print(f"  BRAND:   {row['brand']}")
        print(f"  RATING:  {row['rating']}")
        print(f"  ACCORDS: {row['accords']}")
        print(f"  TOP:     {row['notes_top']}")
        print(f"  MIDDLE:  {row['notes_middle']}")
        print(f"  BASE:    {row['notes_base']}")
        print(f"  EMBED:   {row['embedding_text']}")
        print()