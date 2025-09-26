
# Déployer le backend "Le Recenseur" avec FastAPI

## 🚀 Render (le plus simple)
1. Mets tous ces fichiers dans un dépôt GitHub (c’est déjà fait ✅).
2. Sur [Render.com](https://render.com) → clique sur **New** → **Blueprint** → connecte ton repo GitHub.
3. Dans **Environment Variables**, ajoute :
   - `RECENSEUR_API_KEY` = une clé secrète longue (ex. 40 caractères).
   - `NAVITIA_KEY` = optionnel (clé Navitia pour calculer les temps de train réels).
4. Clique **Deploy**.  
5. Tu auras une URL publique comme :  
https://recenseur-backend.onrender.com
## 🖥️ Test rapide
Depuis ton terminal (ou depuis l’onglet “Shell” sur Render) :
```bash
curl -X POST https://recenseur-backend.onrender.com/score_match \
-H "Authorization: Bearer VOTRE_CLE" -H "Content-Type: application/json" \
-d '{"texte":"Maison à rénover, gros travaux à prévoir"}'
docker build -t recenseur-backend .
docker run -e RECENSEUR_API_KEY=CHANGE_ME -p 8000:8000 recenseur-backend
Puis ouvre http://localhost:8000/docsgcloud builds submit --tag gcr.io/PROJECT/recenseur-backend
gcloud run deploy recenseur-backend --image gcr.io/PROJECT/recenseur-backend --platform managed \
  --allow-unauthenticated --region europe-west1 \
  --set-env-vars RECENSEUR_API_KEY=YOUR_KEY,NAVITIA_KEY=...
