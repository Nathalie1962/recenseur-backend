# FastAPI backend example for "Le Recenseur"
# Run locally: uvicorn backend_fastapi_example:app --reload
import os, re, hashlib, datetime as dt
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, Header, HTTPException
import httpx

API_KEY = os.getenv("RECENSEUR_API_KEY", "dev-key")
NAVITIA_KEY = os.getenv("NAVITIA_KEY")  # optional for real commute times

app = FastAPI(title="Le Recenseur Backend")

KEYPOS = [
    (r"\bà rénover\b", 0.6),
    (r"\btravaux (?:à prévoir|importants)\b", 0.4),
    (r"\bà réhabiliter\b", 0.4),
    (r"\bà rafraîchir\b", 0.2),
    (r"\bplateau (?:brut|à aménager)\b", 0.4),
]
KEYNEG = [r"\brefait à neuf\b", r"\baucun(?:s)? travaux?\b", r"\brénové(?:e|s)?\b"]

def score_match_text(text: str):
    t = (text or "").lower()
    score = 0.0
    matched = []
    for pat, w in KEYPOS:
        if re.search(pat, t):
            score += w; matched.append(pat)
    for pat in KEYNEG:
        if re.search(pat, t):
            score -= 0.7; matched.append(pat)
    score = max(0.0, min(1.0, score))
    return score, matched

def canonical_key(url: str, titre: str, prix: Any, surface: Any, ville: str) -> str:
    s = f"{(url or '').split('?')[0]}|{(titre or '').strip()}|{prix}|{surface}|{ville}"
    return hashlib.sha1(s.encode("utf-8")).hexdigest()

def require_auth(auth: Optional[str]):
    if auth != f"Bearer {API_KEY}":
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.post("/score_match")
async def score_match(payload: Dict[str, Any], Authorization: Optional[str] = Header(None)):
    require_auth(Authorization)
    score, matched = score_match_text(payload.get("texte", ""))
    return {"score_reno": score, "matched_terms": matched}

@app.post("/extract_features")
async def extract_features(payload: Dict[str, Any], Authorization: Optional[str] = Header(None)):
    require_auth(Authorization)
    rl = payload.get("raw_listing", {})
    listing = {
        "titre": rl.get("titre"),
        "url": rl.get("url"),
        "source": rl.get("source"),
        "prix": rl.get("prix"),
        "surface_m2": rl.get("surface_m2"),
        "type": rl.get("type") or "maison",
        "ville": rl.get("ville"),
        "cp": rl.get("code_postal"),
        "date": rl.get("date_pub"),
        "texte": rl.get("texte"),
        "images": rl.get("images") or [],
    }
    return {"listing": listing}

@app.post("/dedupe")
async def dedupe(payload: Dict[str, Any], Authorization: Optional[str] = Header(None)):
    require_auth(Authorization)
    uniq = {}
    for l in payload.get("listings", []):
        key = canonical_key(l.get("url"), l.get("titre"), l.get("prix"), l.get("surface_m2"), l.get("ville"))
        if key not in uniq:
            l["key"] = key
            uniq[key] = l
    return {"listings_unique": list(uniq.values())}

@app.post("/persist")
async def persist(payload: Dict[str, Any], Authorization: Optional[str] = Header(None)):
    require_auth(Authorization)
    items = payload.get("listings", [])
    path = os.getenv("RECENSEUR_STORE", "recenseur_store.jsonl")
    with open(path, "a", encoding="utf-8") as f:
        for it in items:
            f.write(str(it) + "\n")
    return {"stored_count": len(items)}

async def navitia_commute(from_label: str, to_label: str) -> Optional[int]:
    if not NAVITIA_KEY:
        return None
    base = "https://api.navitia.io/v1/coverage/fr-idf/journeys"
    params = {
        "from": from_label,
        "to": to_label,
        "datetime_represents": "departure",
        "datetime": dt.datetime.now().replace(hour=7, minute=30, second=0, microsecond=0).isoformat(),
        "max_nb_journeys": 3
    }
    async with httpx.AsyncClient(auth=(NAVITIA_KEY, "")) as client:
        r = await client.get(base, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        durs = [j.get("duration") for j in data.get("journeys", []) if j.get("duration")]
        if not durs:
            return None
        return int(min(durs) // 60)

@app.post("/commute_time")
async def commute_time(payload: Dict[str, Any], Authorization: Optional[str] = Header(None)):
    require_auth(Authorization)
    ville_ou_gare = payload.get("ville_ou_gare")
    hint = payload.get("gare_parisienne_hint")
    gare_paris = hint or "Paris Saint-Lazare"
    minutes = await navitia_commute(ville_ou_gare, gare_paris)
    if minutes is None:
        FALLBACK = {
            "Mantes-la-Jolie": 50, "Vernon": 55, "Évreux": 70, "Dreux": 75,
            "Rambouillet": 45, "Chartres": 75, "Étampes": 50, "Dourdan": 60,
            "Fontainebleau-Avon": 50, "Nemours": 65, "Montereau": 75, "Sens": 85,
            "Compiègne": 55, "Beauvais": 80, "Château-Thierry": 55, "Provins": 85,
            "Coulommiers": 70, "La Ferté-sous-Jouarre": 55
        }
        minutes = FALLBACK.get(ville_ou_gare, None)
    return {"minutes_train": minutes, "gare_depart": ville_ou_gare, "gare_parisienne": gare_paris}

@app.post("/search_listings")
async def search_listings(payload: Dict[str, Any], Authorization: Optional[str] = Header(None)):
    require_auth(Authorization)
    return {"raw_listings": []}

