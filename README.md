# Food Verse AI
Backend: `cd backend && pip install -r requirements.txt && uvicorn main:app --reload`
Frontend: `cd frontend && npm install && npm run dev` (proxies /api to :8000)
Vision is simulated (deterministic per image). Replace the logic in `backend/main.py` with a real model to go live.
