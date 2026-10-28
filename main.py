"""Food Verse AI backend. Vision is simulated: results are deterministic per image
(seeded by a hash of the bytes); freshness also uses real pixel statistics.
Swap the endpoint logic for a real vision model/API when ready."""
import hashlib, io, random
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image

app = FastAPI(title="Food Verse AI")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def rng(data: bytes): return random.Random(int(hashlib.sha256(data).hexdigest(), 16))

FOODS = [
 {"name": "Paneer Butter Masala with Naan", "cuisine": "North Indian", "kcal": 640, "protein": 24, "carbs": 58, "fat": 34, "fiber": 5,
  "ingredients": [("Paneer", 120), ("Tomato-cashew gravy", 150), ("Butter & cream", 30), ("Naan", 90)]},
 {"name": "Masala Dosa with Sambar", "cuisine": "South Indian", "kcal": 410, "protein": 11, "carbs": 62, "fat": 13, "fiber": 6,
  "ingredients": [("Rice-lentil batter", 120), ("Spiced potato", 100), ("Sambar", 150), ("Coconut chutney", 40)]},
 {"name": "Chicken Caesar Salad", "cuisine": "American", "kcal": 480, "protein": 36, "carbs": 18, "fat": 29, "fiber": 4,
  "ingredients": [("Grilled chicken", 130), ("Romaine", 90), ("Parmesan", 20), ("Croutons", 25), ("Caesar dressing", 30)]},
 {"name": "Veg Biryani with Raita", "cuisine": "Indian", "kcal": 520, "protein": 13, "carbs": 84, "fat": 15, "fiber": 7,
  "ingredients": [("Basmati rice", 180), ("Mixed vegetables", 110), ("Fried onion", 20), ("Curd raita", 80)]},
 {"name": "Avocado Toast with Egg", "cuisine": "Cafe", "kcal": 370, "protein": 15, "carbs": 33, "fat": 21, "fiber": 9,
  "ingredients": [("Sourdough", 70), ("Avocado", 80), ("Poached egg", 50), ("Chili flakes", 1)]},
]

@app.post("/api/analyze/food")
async def food(file: UploadFile = File(...)):
    data = await file.read(); r = rng(data)
    f = r.choice(FOODS); k = r.uniform(0.9, 1.15)
    return {"name": f["name"], "cuisine": f["cuisine"], "confidence": round(r.uniform(.86, .98), 2),
            "macros": {m: round(f[m] * k) for m in ("kcal", "protein", "carbs", "fat", "fiber")},
            "ingredients": [{"name": n, "grams": round(g * k)} for n, g in f["ingredients"]],
            "note": "Estimates assume a standard restaurant portion; adjust for your serving."}

REASONS = {
 "Fresh": ["Colour is uniform with no brown or grey patches.", "Surface looks firm; no visible moisture pooling or mould.", "Low enzymatic browning, so polyphenol oxidation is minimal."],
 "Consume Soon": ["Early browning/dulling suggests oxidation has begun.", "Small soft spots hint at cell-wall breakdown (pectin loss).", "Eat within 24-48h or cook/freeze to stop further decline."],
 "Spoiled": ["Dark or grey patches indicate advanced decay or mould growth.", "Surface sheen/slime suggests bacterial biofilm (e.g. Pseudomonas).", "Discard. Cooking does not remove all toxins from mould or bacteria."]}

@app.post("/api/analyze/freshness")
async def freshness(file: UploadFile = File(...), category: str = Form("produce")):
    data = await file.read(); r = rng(data)
    try:  # real heuristic: share of dark/brownish pixels
        px = list(Image.open(io.BytesIO(data)).convert("RGB").resize((48, 48)).getdata())
        dark = sum(1 for R, G, B in px if max(R, G, B) < 90 or (R > G > B and R < 150 and G < 110)) / len(px)
    except Exception: dark = r.random() * .5
    score = max(2, min(98, round(100 - dark * 160 + r.uniform(-6, 6))))
    verdict = "Fresh" if score >= 70 else "Consume Soon" if score >= 40 else "Spoiled"
    shelf = {"Fresh": "3-5 days refrigerated", "Consume Soon": "Within 1-2 days", "Spoiled": "Do not eat"}[verdict]
    return {"category": category, "score": score, "verdict": verdict, "shelf_life": shelf,
            "darkPixelRatio": round(dark, 2), "reasons": REASONS[verdict]}

CHECKS = [("Hair restraints / caps worn", "Staff"), ("Gloves in use and unsoiled", "Handling"), ("Raw and cooked foods separated", "Cross-contamination"),
          ("Colour-coded cutting boards", "Cross-contamination"), ("Work surfaces clean and dry", "Sanitation"), ("Handwash station accessible", "Sanitation"),
          ("Food labelled and dated", "Storage"), ("Waste bins covered", "Pest control"), ("Cold storage below 5°C visible", "Temperature"), ("Floors clear of spills/clutter", "Safety")]

@app.post("/api/analyze/hygiene")
async def hygiene(file: UploadFile = File(...)):
    data = await file.read(); r = rng(data)
    items = [{"check": c, "area": a, "status": r.choices(["pass", "warn", "fail"], [6, 2, 2])[0]} for c, a in CHECKS]
    pts = {"pass": 1, "warn": .5, "fail": 0}
    score = round(100 * sum(pts[i["status"]] for i in items) / len(items))
    return {"score": score, "grade": "A" if score >= 85 else "B" if score >= 70 else "C" if score >= 50 else "D",
            "items": items, "actions": [f"Fix: {i['check']}" for i in items if i["status"] == "fail"] or ["No critical violations found."],
            "frames_scanned": 1 if (file.content_type or "").startswith("image") else 24}

MEALS = [  # name, slot, tags, kcal, protein, items
 ("Vegetable poha with peanuts", "Breakfast", "vegan", 350, 9, ["poha", "peanuts", "onion", "peas"]),
 ("Greek yogurt, berries, oats", "Breakfast", "veg", 380, 22, ["yogurt", "berries", "oats"]),
 ("Egg bhurji with toast", "Breakfast", "nonveg", 400, 22, ["eggs", "bread", "onion", "tomato"]),
 ("Besan chilla with mint chutney", "Breakfast", "vegan", 330, 16, ["gram flour", "onion", "mint"]),
 ("Dal tadka, brown rice, salad", "Lunch", "vegan", 560, 22, ["lentils", "brown rice", "cucumber", "tomato"]),
 ("Paneer tikka wrap", "Lunch", "veg", 540, 28, ["paneer", "wheat roti", "bell pepper", "yogurt"]),
 ("Grilled chicken quinoa bowl", "Lunch", "nonveg", 590, 42, ["chicken", "quinoa", "spinach", "olive oil"]),
 ("Chickpea spinach curry, roti", "Lunch", "vegan", 520, 20, ["chickpeas", "spinach", "wheat roti", "tomato"]),
 ("Vegetable khichdi, curd", "Dinner", "veg", 480, 18, ["rice", "lentils", "mixed vegetables", "yogurt"]),
 ("Baked fish, sauteed greens", "Dinner", "nonveg", 500, 38, ["fish", "spinach", "olive oil", "lemon"]),
 ("Tofu stir fry with noodles", "Dinner", "vegan", 510, 24, ["tofu", "noodles", "bell pepper", "soy sauce"]),
 ("Mixed veg soup and sprouts salad", "Dinner", "vegan", 360, 17, ["mixed vegetables", "sprouts", "lemon"]),
]
RANK = {"vegan": 0, "veg": 1, "nonveg": 2}

class PlanReq(BaseModel):
    diet: str = "veg"; goal: str = "maintain"; calories: int = 2000; days: int = 7
    allergies: list[str] = []; dislikes: list[str] = []; seed: int = 0

@app.post("/api/mealplan")
def mealplan(q: PlanReq):
    bad = [a.lower() for a in q.allergies + q.dislikes]
    ok = lambda m: RANK[m[2]] <= RANK[q.diet] and not any(a in " ".join(m[5]) or a in m[0].lower() for a in bad)
    pool = {s: [m for m in MEALS if m[1] == s and ok(m)] or [m for m in MEALS if m[1] == s and m[2] == "vegan"] for s in ("Breakfast", "Lunch", "Dinner")}
    target = q.calories + {"lose": -400, "gain": 400}.get(q.goal, 0); r = random.Random(q.seed); plan, groceries = [], {}
    for d in range(q.days):
        day = [r.choice(pool[s]) for s in pool]; k = target / sum(m[3] for m in day)
        plan.append({"day": d + 1, "total_kcal": target, "meals": [{"slot": m[1], "name": m[0], "kcal": round(m[3] * k), "protein": round(m[4] * k), "portion": f"{k:.1f}x"} for m in day]})
        for m in day:
            for it in m[5]: groceries[it] = groceries.get(it, 0) + 1
    return {"target_kcal": target, "plan": plan, "grocery": sorted(({"item": k, "uses": v} for k, v in groceries.items()), key=lambda x: x["item"])}

RECIPES = [
 {"id": "dal", "title": "Dal Tadka", "time": "35 min", "ingredients": ["toor dal", "onion", "tomato", "garlic", "cumin", "ghee", "turmeric"],
  "steps": ["Rinse 1 cup dal; pressure cook with turmeric and 3 cups water for 4 whistles.", "Heat ghee, crackle cumin, then saute chopped onion and garlic until golden.", "Add tomato and cook until it breaks down into a paste.", "Mash the dal, stir in the masala, simmer 5 minutes and adjust salt.", "Finish with a fresh ghee-cumin tadka and serve with rice."]},
 {"id": "pasta", "title": "Garlic Tomato Pasta", "time": "20 min", "ingredients": ["pasta", "tomato", "garlic", "olive oil", "basil", "chili flakes"],
  "steps": ["Boil pasta in well-salted water until al dente; save a cup of pasta water.", "Warm olive oil and gently cook sliced garlic until fragrant, not brown.", "Add crushed tomato and chili; simmer 8 minutes.", "Toss pasta in the sauce with splashes of pasta water until glossy.", "Tear in basil and serve."]},
 {"id": "omelette", "title": "Masala Omelette", "time": "10 min", "ingredients": ["eggs", "onion", "green chili", "coriander", "butter"],
  "steps": ["Whisk eggs with salt, chopped onion, chili and coriander.", "Melt butter in a pan on medium heat.", "Pour the mix and let the edges set for 1 minute.", "Fold and cook 1 more minute until just set."]},
]
SUBS = {"butter": "ghee, olive oil or coconut oil (use 3/4 the amount of oil)", "egg": "1/4 cup mashed banana or 1 tbsp ground flax + 3 tbsp water per egg",
 "cream": "cashew paste or full-fat yogurt (add off the heat to avoid splitting)", "milk": "oat, soy or almond milk 1:1", "yogurt": "hung curd, or coconut yogurt for vegan",
 "paneer": "firm tofu or halloumi", "ghee": "butter or neutral oil + a pinch of cumin", "garlic": "asafoetida (hing), a pinch, or garlic powder (1/4 tsp per clove)",
 "tomato": "tamarind paste or 2 tbsp tomato puree per tomato", "basil": "oregano or fresh spinach plus a little mint", "toor dal": "moong or masoor dal (cooks faster)",
 "pasta": "rice noodles, zucchini noodles or any small-cut millet pasta", "onion": "shallots, leek whites, or 1/4 tsp onion powder per 1/4 cup"}

class Chat(BaseModel):
    message: str; recipe_id: str = "dal"; step: int = 0; pantry: list[str] = []

@app.get("/api/recipes")
def recipes(): return RECIPES

@app.post("/api/cook/chat")
def chat(c: Chat):
    m = c.message.lower(); rec = next((x for x in RECIPES if x["id"] == c.recipe_id), RECIPES[0])
    if "missing" in m or "what can i" in m:
        miss = [i for i in rec["ingredients"] if not any(p.lower() in i for p in c.pantry)]
        return {"reply": ("You are missing: " + ", ".join(miss) + ".") if miss else "You have everything for this recipe.", "tag": "Pantry"}
    for k, v in SUBS.items():
        if k in m: return {"reply": f"No {k}? Try {v}.", "tag": "Substitution"}
    tips = {"burn": "Lower the heat, move food to a clean pan and don't scrape the burnt layer.", "stuck": "Let it release naturally; add a splash of oil or water and wait 30s.",
            "salty": "Add acid or a starch (potato, rice, lemon) and dilute with unsalted liquid.", "bland": "Add salt first, then acid (lemon/vinegar), then a tempered spice.", "spicy": "Stir in yogurt, cream, sugar or coconut milk."}
    for k, v in tips.items():
        if k in m: return {"reply": v, "tag": "Rescue"}
    if "how long" in m or "time" in m: return {"reply": f"The whole recipe takes about {rec['time']}.", "tag": "Timing"}
    return {"reply": f"You're on step {c.step + 1}: {rec['steps'][c.step]} Ask for a substitute (e.g. 'no butter') or how to fix a mistake.", "tag": "Guide"}
