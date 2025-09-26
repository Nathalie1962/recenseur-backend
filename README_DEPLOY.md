# Déployer le backend "Le Recenseur" avec FastAPI

## 🚀 Render (le plus simple)
1. Mets tous ces fichiers dans un dépôt GitHub (c’est déjà fait ✅).
2. Sur [Render.com](https://render.com) → clique sur **New** → **Blueprint** → connecte ton repo GitHub.
3. Dans **Environment Variables**, ajoute :
   - `RECENSEUR_API_KEY` = une clé secrète longue (ex. 40 caractères).
   - `NAVITIA_KEY` = optionnel (clé Navitia pour calculer les temps de train réels).
4. Clique **Deploy**.  
5. Tu auras une URL publique comme :  
