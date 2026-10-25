# Personalized Travel Itinerary Planner — WanderWise

A Streamlit capstone demo for personalized destination recommendations, day-by-day itinerary generation, activity swaps, local trip history, and PDF export.

## Features
- Trip preference capture: destination/vibe, dates, duration, budget, party, pace, interests, currency
- Top-three destination matching using bundled demo profiles and preference scoring
- Day-wise itinerary with time slots, activity estimates, running total, and area-cluster labels
- Swap a single activity or regenerate one day without replacing the rest of the trip
- Save multiple trips to local JSON and export printable PDF guides with a pre-travel checklist
- Works without API keys or a database

## Requirements
- Python 3.9+
- Windows/macOS/Linux

## Run locally
```bash
python -m venv venv
# Windows PowerShell:
.env\Scripts\Activate.ps1
# macOS/Linux:
source venv/bin/activate

python -m pip install -r requirements.txt
python -m streamlit run app.py
```

If PowerShell blocks environment activation, run:
```powershell
.env\Scripts\python.exe -m pip install -r requirements.txt
.env\Scripts\python.exe -m streamlit run app.py
```

## Deploy on Streamlit Community Cloud
1. Push this folder to a GitHub repository.
2. Sign in to Streamlit Community Cloud and choose **Create app**.
3. Select your repository, branch, and `app.py`.
4. Deploy.

## Important scope notes
- This starter uses bundled example destinations and heuristic matching; it does not fetch live weather, maps, restaurant availability, ticket prices, or route times.
- Activity costs are approximate illustrative estimates. They exclude many trip costs such as accommodation and transport.
- JSON trip history is local/demo persistence. Files on hosted app instances may not be durable across restarts or redeployments. Use Supabase or another persistent store for production.
- The optional provider/key fields are a UI placeholder; the current version does not send requests to Gemini or Groq. Never commit API keys.
