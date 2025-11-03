from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import patients, appointments, medical_records, prescriptions, utils, documents

app = FastAPI(
    title="Sanaris Pro API",
    description="Sistema de Gestão de Clínicas e Consultórios",
    version="1.0.0 - Fase 2.5"
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
app.include_router(appointments.waitlist_router)
app.include_router(appointments.schedule_router)
app.include_router(appointments.availability_router)
app.include_router(medical_records.router)
app.include_router(prescriptions.router)
app.include_router(utils.router)
app.include_router(documents.router)

@app.get("/")
def read_root():
    return {
        "message": "🏥 Sanaris Pro API - Fase 2.5 ✅",
        "version": "1.0.0",
        "status": "online",
        "modules": {
            "patients": "✅ Active",
            "appointments": "✅ Active (29 endpoints)",
            "waitlist": "✅ Active",
            "schedules": "✅ Active", 
            "availability": "✅ Active",
            "medical_records": "✅ Active (17 endpoints)",
            "prescriptions": "✅ Active (20 endpoints)",
            "utils": "✅ Active (6 endpoints)",
            "documents": "✅ Active (16 endpoints)"
        },
        "improvements": {
            "validators": "✅ CPF, CNPJ, Telefone, CEP, CRM",
            "soft_delete": "✅ Exclusão lógica",
            "pagination": "✅ Sistema de paginação",
            "filters": "✅ Filtros avançados",
            "documents": "✅ Templates e Termos",
            "quick_registration": "✅ Pré-cadastro rápido"
        }
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "phase": "2.5",
        "features": [
            "appointments_crud",
            "confirmations",
            "waitlist",
            "schedules",
            "availability",
            "medical_records",
            "vital_signs",
            "attachments",
            "patient_timeline",
            "prescriptions",
            "prescription_templates",
            "digital_signature",
            "brazilian_validators",
            "soft_delete",
            "pagination",
            "advanced_filters",
            "document_templates",
            "patient_documents",
            "quick_registration"
        ]
    }
