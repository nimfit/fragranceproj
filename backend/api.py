# FastAPI backend for the Cologne Recommender.
# Two endpoints:
#   POST /search  — embed a text query, find similar colognes
#   POST /similar — find a cologne by name, return similar ones

#User types in React chat
 #       ↓
#React sends HTTP request to FastAPI
 #       ↓
#FastAPI runs Python — embeds the query,
#searches Supabase with cosine similarity
  #      ↓
#FastAPI sends back JSON results
 #       ↓
#React receives JSON and renders the cologne cards


from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from supabase import create_client
from dotenv import load_dotenv
from thefuzz import process
import os
import re

# ── Startup
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("Missing SUPABASE_URL or SUPABASE_KEY in .env file!")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

model = SentenceTransformer('all-MiniLM-L6-v2')

# We load all names once
response = supabase.table("colognes").select("id, name, brand").limit(300000).execute()
all_colognes = response.data
print(f"[startup] Ready — {len(all_colognes)} colognes loaded\n")

# ── App setup
app = FastAPI()

# CORS — allows our React frontend to call this API
# In production we'll lock this down to our real domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request models
class SearchRequest(BaseModel):
    # "Find me something warm and woody with vanilla"
    query: str
    limit: int = 10

class SimilarRequest(BaseModel):
    # "Dior Sauvage"
    cologne_name: str
    limit: int = 10

# ── Helper ────────────────────────────────────────────────────
def run_similarity_search(embedding: list, limit: int):
    """
    Takes a vector and returns the most similar colognes from Supabase.
    Uses the pgvector cosine similarity index we created in Task 2.
    """
    result = supabase.rpc("match_colognes", {
        "query_embedding": embedding,
        "match_count": limit
    }).execute()
    return result.data

def check_valid_input(text: str) -> bool:
    """
    Checks for input
    """
    return bool(re.search(r"[a-zA-Z]", text))



# ── Routes
@app.get("/")
def root():
    return {"status": "Cologne Recommender API is running"}


@app.post("/search")
def search(req: SearchRequest):
    """
    Embed the user's free-text query and return the most similar colognes.
    Example: { "query": "warm vanilla spicy oriental" }
    """

    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    if not check_valid_input(req.query):
     raise HTTPException(status_code=400, detail="Query must contain letters")


    # Convert the user's text into a vector
    embedding = model.encode(req.query).tolist()

    results = run_similarity_search(embedding, req.limit)

    if not results:
        raise HTTPException(status_code=404, detail="No similar colognes found")

    return {"results": results}


@app.post("/similar")
def similar(req: SimilarRequest):
    """
    Find a cologne by name (fuzzy matched) and return similar colognes.
    Example: { "cologne_name": "Dior Sauvage" }
    """

    if not req.cologne_name.strip():
        raise HTTPException(status_code=400, detail="Cologne name cannot be empty")
    
    if not check_valid_input(req.cologne_name):
        raise HTTPException(status_code=400, detail="Query must contain letters")


    name_lookup = {f"{c['brand']} {c['name']}": c['id'] for c in all_colognes}

    best_match, score = process.extractOne(req.cologne_name, name_lookup.keys())

    if score < 50:
        raise HTTPException(status_code=404, detail=f"Could not find a cologne matching '{req.cologne_name}'")

    cologne_id = name_lookup[best_match]

    # Fetch that cologne's stored embedding from Supabase
    cologne = supabase.table("colognes").select("name, brand, embedding").eq("id", cologne_id).single().execute()

    if not cologne.data or not cologne.data.get("embedding"):
        raise HTTPException(status_code=404, detail="Cologne found but has no embedding")

    print(f"[/similar] Found '{cologne.data['name']}' by '{cologne.data['brand']}', searching for similar...")


    embedding = cologne.data["embedding"]
    results = run_similarity_search(embedding, req.limit)

    results = [
        c for c in results
        if c["similarity"] < 1
    ]
    #removes the fragrances
   
    print(f"[/similar] Returning {len(results)} results")
    return {
        "matched": best_match,
        "results": results
    }
