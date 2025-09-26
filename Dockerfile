FROM python:3.11-slim

# Empêcher Python d'écrire des fichiers .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Dossier de travail
WORKDIR /app

# Installer dépendances système minimales
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates && rm -rf /var/lib/apt/lists/*

# Copier requirements et installer
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copier le backend
COPY backend_fastapi_example.py ./

# Variables d’environnement par défaut
ENV RECENSEUR_API_KEY=CHANGE_ME

# Exposer le port
EXPOSE 8000

# Lancer l’application
CMD ["uvicorn", "backend_fastapi_example:app", "--host", "0.0.0.0", "--port", "8000"]
