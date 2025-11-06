from fastapi import APIRouter
from app.api.endpoints import (
    patients,
    appointments,
    medical_records,
    prescriptions,
    auth
)

api_router = APIRouter()

# Rotas de autenticação
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

# Rotas de pacientes
api_router.include_router(
    patients.router,
    prefix="/patients",
    tags=["Patients"]
)

# Rotas de agendamentos
api_router.include_router(
    appointments.router,
    prefix="/appointments",
    tags=["Appointments"]
)

# Rotas de prontuários
api_router.include_router(
    medical_records.router,
    prefix="/medical-records",
    tags=["Medical Records"]
)

# Rotas de prescrições
api_router.include_router(
    prescriptions.router,
    prefix="/prescriptions",
    tags=["Prescriptions"]
)
