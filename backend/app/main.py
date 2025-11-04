from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import (
    patients, appointments, medical_records, prescriptions, 
    utils, documents, medical_record_extensions, 
    cfm_integration, digital_signature, 
    accounts_receivable, accounts_payable, cash_flow, professional_fees
)

app = FastAPI(
    title="Sanaris Pro API",
    description="Sistema de Gestão de Clínicas e Consultórios",
    version="1.0.0 - Fase 3.4 - COMPLETO"
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
app.include_router(cash_flow.router)
app.include_router(professional_fees.router)

@app.get("/")
def read_root():
    return {
        "message": "🏥 Sanaris Pro API - FASE 3 COMPLETA! 🎉",
        "version": "1.0.0",
        "status": "online",
        "phase": "FASE 3 - GESTÃO FINANCEIRA (100% COMPLETA)",
        "modules": {
            "patients": "✅ Active",
            "appointments": "✅ Active (29 endpoints)",
            "medical_records": "✅ Active (17 endpoints)",
            "prescriptions": "✅ Active (23 endpoints)",
            "utils": "✅ Active (6 endpoints)",
            "documents": "✅ Active (16 endpoints)",
            "medical_extensions": "✅ Active (19 endpoints)",
            "cfm_integration": "✅ Active (9 endpoints)",
            "digital_signature": "✅ Active (12 endpoints)",
            "accounts_receivable": "✅ Active (12 endpoints)",
            "accounts_payable": "✅ Active (18 endpoints)",
            "cash_flow": "✅ Active (7 endpoints)",
            "professional_fees": "✅ Active (13 endpoints)"
        },
        "financial_complete": {
            "accounts_receivable": "✅ 100% Completo",
            "accounts_payable": "✅ 100% Completo",
            "suppliers": "✅ 100% Completo",
            "expense_categories": "✅ 100% Completo",
            "cost_centers": "✅ 100% Completo",
            "payment_approval": "✅ 100% Completo",
            "cash_flow_dashboard": "✅ 100% Completo",
            "cash_flow_reports": "✅ 100% Completo",
            "cash_flow_projection": "✅ 100% Completo",
            "professional_fees": "✅ 100% Completo"
        },
        "total_endpoints": 181
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "phase": "3.4 - COMPLETE",
        "total_endpoints": 181,
        "features": [
            "patient_management",
            "appointment_scheduling",
            "intelligent_waitlist",
            "professional_schedules",
            "medical_records",
            "vital_signs",
            "prescriptions",
            "cfm_integration",
            "digital_signature",
            "accounts_receivable",
            "accounts_payable",
            "cash_flow_dashboard",
            "professional_fees",
            "supplier_management",
            "expense_categories",
            "cost_centers",
            "financial_reports",
            "financial_projections"
        ]
    }
