from fastapi import FastAPI
from app.database import engine, Base

# Crée automatiquement les tables SQL au démarrage du serveur
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="My Social Networks API",
    version="1.0.0",
    description="Refonte des API d'un réseau social"
)

@app.get("/api/health", tags=["Système"])
def health_check():
    return {"status": "ok", "message": "L'API fonctionne parfaitement"}