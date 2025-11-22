import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base

from app.services.reminder_scheduler import reminder_scheduler

from app.api.endpoints import (
    schedule,
    notifications,
    dashboard,
    financial,
    job_titles,
    doctor_profile,
    medications,
    users_simple,
    auth,
    file_upload,
    file_download, 
    organizations, 
    users_management, 
    chat, 
    patients, 
    permissions, 
    admin_stats,
    dashboard_stats,
    appointments,
    medical_records,
    prescriptions
)

# Importar routers TISS
from app.api import (
    tiss_operadoras,
    tiss_lotes,
    tiss_guias,
    tiss_procedimentos,
    tiss_tabelas,
    tiss_xml,
    prestadores
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Sanaris Pro API",
    description="Sistema de Gestão de Clínicas",
    version="1.0.0"
)

# Servir arquivos estáticos de uploads
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Eventos de inicialização e desligamento
@app.on_event("startup")
async def startup_event():
    """Iniciar scheduler de lembretes ao subir o backend"""
    reminder_scheduler.start()
    logger.info("🚀 Scheduler de lembretes iniciado!")

@app.on_event("shutdown")
async def shutdown_event():
    """Parar scheduler ao desligar o backend"""
    reminder_scheduler.stop()
    logger.info("⏹️ Scheduler de lembretes parado!")


# Routers de Autenticação e Organizações
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(organizations.router, prefix="/api/v1/organizations", tags=["Organizations"])

# Routers de Usuários
app.include_router(users_management.router, prefix="/api/v1/users-management", tags=["Users Management"])
app.include_router(users_simple.router, prefix="/api/v1/users", tags=["Users"])

# Routers de Pacientes e Atendimento
app.include_router(patients.router, prefix="/api/v1/patients", tags=["Patients"])
app.include_router(appointments.router, prefix="/api/v1/appointments", tags=["Appointments"])
app.include_router(medical_records.router, prefix="/api/v1/medical-records", tags=["Medical Records"])
app.include_router(prescriptions.router, prefix="/api/v1/prescriptions", tags=["Prescriptions"])

# Routers de Comunicação
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["Notifications"])

# Routers de Dashboard e Estatísticas
app.include_router(dashboard_stats.router, prefix="/api/v1/statistics", tags=["Dashboard Statistics"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(admin_stats.router, prefix="/api/v1/admin", tags=["Admin Statistics"])

# Routers Financeiros
app.include_router(financial.router, prefix="/api/v1/financial", tags=["Financial"])

# Routers de Configurações
app.include_router(job_titles.router, prefix="/api/v1/job-titles", tags=["Job Titles"])
app.include_router(permissions.router, prefix="/api/v1/permissions", tags=["Permissions"])
app.include_router(medications.router, prefix="/api/v1/medications", tags=["Medications"])
app.include_router(doctor_profile.router, prefix="/api/v1/doctor-profile", tags=["Doctor Profile"])
app.include_router(schedule.router, prefix="/api/v1/schedule", tags=["Schedule"])

# Routers de Arquivos
app.include_router(file_upload.router, prefix="/api/files", tags=["Files"])
app.include_router(file_download.router, prefix="/api/files", tags=["Files"])

# ========== ROUTERS TISS ==========
app.include_router(tiss_operadoras.router, prefix="/api/v1", tags=["TISS"])
app.include_router(tiss_lotes.router, prefix="/api/v1", tags=["TISS"])
app.include_router(tiss_guias.router, prefix="/api/v1", tags=["TISS"])
app.include_router(tiss_procedimentos.router, prefix="/api/v1", tags=["TISS"])
app.include_router(prestadores.router, prefix="/api/v1/prestadores", tags=["Prestadores"])
app.include_router(tiss_tabelas.router, prefix="/api/v1", tags=["TISS"])
app.include_router(tiss_xml.router, prefix="/api/v1", tags=["TISS"])


# Health checks
@app.get("/")
def read_root():
    return {"message": "Sanaris Pro API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}