
# FINDIT AI — Project Skill Guide

## Project Goal
Help people recover lost belongings without requiring a photo.
Users can submit text descriptions, category, approximate location,
and time. Photos are optional.

## Architecture
- main.py: FastAPI endpoints, JSON-backed report loading, and static UI hosting.
- model.py: Text similarity and match scoring.
- tools.py: Local JSON persistence and image-reference checks.
- requirements.txt: Python dependencies.
- static/: Browser application.
- data/reports.json: Local demo reports.

## Matching
The current demo uses deterministic token-overlap matching; it does not load an
embedding model or understand semantic meaning. It compares description (60%),
category (20%), location (12%), and reported date (8%). Missing date values are
excluded from the score normalization. Scores are suggestions, not validated
accuracy measurements.

## Matching Weights
- Description similarity: 60%
- Category: 20%
- Location: 12%
- Time: 8%

These weights are configurable demo heuristics, not validated
accuracy measurements.

## Run the Project
1. Install Python 3.10 or later.
2. Create and activate a virtual environment.
3. Install requirements.txt.
4. Start the server using:
   uvicorn main:app --reload
5. Open http://127.0.0.1:8000/docs

## Test Scenario
1. Submit a lost black wallet report without an image.
2. Submit a found black wallet report with a similar description.
3. Request the lost report's matches.
4. Check the score signals and verify ownership separately.

## Current Limitations
- JSON storage is intended for local demos.
- No user authentication or private messaging yet.
- No actual image upload or image-recognition system yet.
- No live GPS or map integration yet.
- Match results are suggestions, not proof of ownership.

## Before Public Deployment
Use a real database, authentication, rate limiting, secure image
storage, privacy controls, abuse reporting, and safe contact methods.
