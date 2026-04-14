# Sillage

Sillage is a fragrance recommendation project that turns perfume metadata into searchable semantic profiles. The backend cleans a large Fragrantica dataset, builds text embeddings for each fragrance, stores them in Supabase with `pgvector`, and serves recommendation endpoints through FastAPI.

The goal was to make fragrance discovery feel more natural than exact keyword matching. Instead of requiring users to know a specific bottle, the system supports prompts like "warm vanilla woody date-night scent" and returns fragrances with similar note and accord profiles.

## What We Built

- A data-cleaning pipeline for a 24,063-row fragrance dataset
- An embedding generation and upload workflow using `sentence-transformers`
- A Supabase-backed vector search layer for similarity lookup
- A FastAPI API for free-text recommendation and fragrance-to-fragrance matching
- A React + TypeScript frontend workspace for the client application

## Recruiter Summary

This project demonstrates:

- Applied NLP: converting product metadata into semantic embeddings for search
- Recommendation systems: matching user intent and related products with vector similarity
- Data engineering: cleaning, reshaping, and preparing a large CSV dataset for downstream use
- Full-stack thinking: connecting a React frontend to a Python API and hosted vector database
- Practical product design: building around a real user problem, fragrance discovery

## How It Works

### 1. Dataset Preparation

The raw Fragrantica export is cleaned in [`backend/clean_data.py`](/C:/Users/kings/Sillage/fragranceproj/backend/clean_data.py). The script:

- standardizes column names
- fixes rating formatting issues
- combines accord columns into a single field
- preserves top, middle, and base note information
- creates an `embedding_text` string for each fragrance

That `embedding_text` becomes the semantic representation used for recommendations.

### 2. Embedding + Database Upload

[`backend/embed_and_upload.py`](/C:/Users/kings/Sillage/fragranceproj/backend/embed_and_upload.py) loads the cleaned dataset, generates embeddings with `all-MiniLM-L6-v2`, and uploads rows to Supabase in batches.

Each stored record includes:

- fragrance metadata
- accords and note breakdowns
- a generated embedding vector for similarity search

### 3. Recommendation API

[`backend/api.py`](/C:/Users/kings/Sillage/fragranceproj/backend/api.py) exposes two primary endpoints:

- `POST /search`
  Returns fragrances similar to a free-text description
- `POST /similar`
  Fuzzy-matches a fragrance name, then returns related fragrances using its stored embedding

The API uses:

- `FastAPI` for the service layer
- `SentenceTransformers` for text embeddings
- `Supabase` for storage and RPC access
- `thefuzz` for name matching
- `pgvector`-style similarity search through a Supabase RPC function

## Repository Structure

```text
fragranceproj/
├─ backend/
│  ├─ api.py                  # FastAPI recommendation service
│  ├─ clean_data.py           # dataset cleaning + embedding text generation
│  ├─ embed_and_upload.py     # embedding creation + Supabase upload
│  ├─ main.py                 # CLI prototype for note-based ranking
│  ├─ scoring.py              # earlier scoring-based recommendation logic
│  └─ data/
│     ├─ fragrantica_dataset.csv
│     └─ fragrances_clean.csv
└─ frontend/
   └─ src/
      └─ App.tsx
```

## Current State

The strongest completed work in this repository is the backend recommendation pipeline and vector-search API.

The frontend workspace is present and configured with React, TypeScript, and Vite, but the checked-in UI is still a starter scaffold rather than the final product interface. For recruiter review, the most representative engineering work is in the backend data, ML, and API layers.

## Tech Stack

- Python
- FastAPI
- Pandas
- Sentence Transformers
- Supabase
- React
- TypeScript
- Vite

## Running Locally

### Backend

From `backend/`, install the Python dependencies used by the scripts and API, then provide:

- `SUPABASE_URL`
- `SUPABASE_KEY`

Run the API with your preferred ASGI server, for example:

```bash
uvicorn api:app --reload
```

### Frontend

From `frontend/`:

```bash
npm install
npm run dev
```

## Highlights

- Processed a 24,063-item fragrance dataset into a vector-search-ready format
- Built a semantic search flow for subjective product discovery
- Added fuzzy name matching to improve retrieval when user input is imperfect
- Structured the project so data prep, embedding generation, and API serving are separate stages

## Future Improvements

- Replace the current frontend scaffold with the full search and results experience
- Add saved favorites and comparison views
- Improve evaluation with click-through or user preference feedback
- Add deployment configuration and environment setup documentation

## Why This Project Matters

Fragrance shopping is a good recommendation problem because people often describe what they want emotionally or sensorially, not by exact product names. This project shows how semantic embeddings and vector search can bridge that gap and create a more intuitive discovery experience.
