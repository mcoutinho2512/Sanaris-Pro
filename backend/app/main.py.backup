from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.api.endpoints import (
    patients, appointments, medical_records, prescriptions, 
    utils, documents, medical_record_extensions, 
    cfm_integration, digital_signature, 
    accounts_receivable, accounts_payable, cash_flow, professional_fees,
    tiss, auth, organizations, medications, notifications, google_calendar, cfm_test, statistics, signatures
)

app = FastAPI(
    title="Sanaris Pro API",
    description="Sistema de Gestão de Clínicas e Consultórios",
    version="1.0.0 - GOOGLE CALENDAR"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware, 
    secret_key="sua_chave_secreta_para_sessoes_mude_em_producao_123456"
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(organizations.router, prefix="/api/v1/organizations", tags=["Organizations"])
app.include_router(medications.router, prefix="/api/v1/medications", tags=["Medications"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["Notifications"])
app.include_router(google_calendar.router, prefix="/api/v1/calendar", tags=["Google Calendar"])
app.include_router(patients.router, prefix="/api/v1/patients", tags=["Patients"])
app.include_router(appointments.router)
app.include_router(appointments.waitlist_router)
app.include_router(appointments.schedule_router)
app.include_router(appointments.availability_router)
app.include_router(medical_records.router)
app.include_router(prescriptions.router)
app.include_router(utils.router)
app.include_router(documents.router)
app.include_router(medical_record_extensions.router)
app.include_router(cfm_integration.router)
app.include_router(digital_signature.router)
app.include_router(accounts_receivable.router)
app.include_router(accounts_payable.router)
app.include_router(cash_flow.router)
app.include_router(professional_fees.router)
app.include_router(tiss.router)
app.include_router(cfm_test.router, prefix="/api/v1/cfm", tags=["CFM Test"])
app.include_router(statistics.router, prefix="/api/v1/statistics", tags=["Statistics"])
app.include_router(signatures.router, prefix="/api/v1/signatures", tags=["Signatures"])

@app.get("/")
def read_root():
    return {
        "message": "🏥 Sanaris Pro API - GOOGLE CALENDAR! 📅✨",
        "version": "1.0.0 - GOOGLE CALENDAR INTEGRATION",
        "status": "online",
        "modules": {
            "authentication": "✅ (7 endpoints) 🔐",
            "organizations": "✅ (6 endpoints) 🏥",
            "medications": "✅ (6 endpoints) 💊",
            "notifications": "✅ (4 endpoints) 📧💬📱",
            "google_calendar": "✅ (3 endpoints) 📅",
            "patients": "✅ (3 endpoints)",
            "appointments": "✅ (29 endpoints)"
        },
        "total_endpoints": 247,
        "features": ["google_oauth", "logo_upload", "medication_search", "notifications", "calendar_sync"]
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "total_endpoints": 247,
        "total_tables": 42,
        "features": ["google_oauth", "logo_upload", "medication_autocomplete", "notifications", "calendar_integration"]
    }
