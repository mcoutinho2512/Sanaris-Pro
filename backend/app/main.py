from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import (
    patients, appointments, medical_records, prescriptions, 
    utils, documents, medical_record_extensions, 
    cfm_integration, digital_signature, 
    accounts_receivable, accounts_payable
)

app = FastAPI(
    title="Sanaris Pro API",
    description="Sistema de Gestão de Clínicas e Consultórios",
    version="1.0.0 - Fase 3.2"
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
app.include_router(accounts_receivable.router)
app.include_router(accounts_payable.router)

@app.get("/")
def read_root():
    return {
        "message": "🏥 Sanaris Pro API - Fase 3.2 ✅",
        "version": "1.0.0",
        "status": "online",
        "phase": "FASE 3 - GESTÃO FINANCEIRA",
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
            "digital_signature": "✅ Active (12 endpoints)",
            "accounts_receivable": "✅ Active (12 endpoints)",
            "accounts_payable": "✅ Active (18 endpoints)"
        },
        "financial": {
            "accounts_receivable": "✅ Contas a Receber Completo",
            "accounts_payable": "✅ Contas a Pagar Completo",
            "suppliers": "✅ Gestão de Fornecedores",
            "expense_categories": "✅ Categorias de Despesas",
            "cost_centers": "✅ Centros de Custo",
            "payment_approval": "✅ Aprovação de Pagamentos",
            "cash_flow": "⏳ Próximo",
            "professional_fees": "⏳ Próximo"
        }
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "phase": "3.2",
        "total_endpoints": 161
    }
