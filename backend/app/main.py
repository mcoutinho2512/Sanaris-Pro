from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import (
    patients, appointments, medical_records, prescriptions, 
    utils, documents, medical_record_extensions, 
    cfm_integration, digital_signature
)

app = FastAPI(
    title="Sanaris Pro API",
    description="Sistema de Gestão de Clínicas e Consultórios",
    version="1.0.0 - Fase 2.9 FINAL"
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
app.include_router(medical_record_extensions.router)
app.include_router(cfm_integration.router)
app.include_router(digital_signature.router)

@app.get("/")
def read_root():
    return {
        "message": "🏥 Sanaris Pro API - Fase 2.9 FINAL ✅",
        "version": "1.0.0",
        "status": "online",
        "phase": "FASE 2 COMPLETA - PRIORIDADE ALTA",
        "modules": {
            "patients": "✅ Active",
            "appointments": "✅ Active (29 endpoints)",
            "waitlist": "✅ Active",
            "schedules": "✅ Active", 
            "availability": "✅ Active",
            "medical_records": "✅ Active (17 endpoints)",
            "prescriptions": "✅ Active (23 endpoints)",
            "utils": "✅ Active (6 endpoints)",
            "documents": "✅ Active (16 endpoints)",
            "medical_extensions": "✅ Active (19 endpoints)",
            "cfm_integration": "✅ Active (9 endpoints)",
            "digital_signature": "✅ Active (12 endpoints)"
        },
        "improvements": {
            "validators": "✅ CPF, CNPJ, Telefone, CEP, CRM",
            "soft_delete": "✅ Exclusão lógica",
            "pagination": "✅ Sistema de paginação",
            "filters": "✅ Filtros avançados",
            "documents": "✅ Templates e Termos",
            "quick_registration": "✅ Pré-cadastro rápido",
            "specialty_templates": "✅ Templates por especialidade",
            "exam_charts": "✅ Gráficos de exames",
            "photo_evolution": "✅ Evolução fotográfica",
            "prescription_sending": "✅ Envio de prescrições (Email/WhatsApp/SMS)",
            "cfm_integration": "✅ Integração CFM (prescricao.cfm.org.br)",
            "icp_brasil": "✅ Assinatura ICP-Brasil (OPCIONAL)",
            "otp_signature": "✅ Assinatura OTP (OPCIONAL)"
        }
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "phase": "2.9 - FASE 2 COMPLETA",
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
            "quick_registration",
            "specialty_templates",
            "exam_results",
            "exam_charts",
            "photo_evolution",
            "photo_comparison",
            "prescription_sending",
            "cfm_authentication",
            "cfm_prescription_send",
            "cfm_sync",
            "icp_brasil_signature",
            "otp_signature",
            "signature_logs"
        ]
    }
