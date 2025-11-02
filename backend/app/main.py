from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import patients, appointments

app = FastAPI(
    title="Sanaris Pro API",
    description="Sistema de Gestão de Clínicas e Consultórios",
    version="1.0.0 - Fase 2"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(patients.router)
app.include_router(appointments.router)

@app.get("/")
def read_root():
    return {
        "message": "🏥 Sanaris Pro API - Fase 2",
        "version": "1.0.0",
        "status": "online",
        "modules": {
            "patients": "✅ Active",
            "appointments": "✅ Active",
            "medical_records": "⏳ Coming soon",
            "prescriptions": "⏳ Coming soon"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "phase": "2"}
