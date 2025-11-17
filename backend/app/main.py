from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base

from app.api.endpoints import (
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
    appointments,
    medical_records,
    prescriptions
)

app = FastAPI(
    title="Sanaris Pro API",
    description="Sistema de Gestão de Clínicas",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(organizations.router, prefix="/api/v1/organizations", tags=["Organizations"])
app.include_router(users_management.router, prefix="/api/v1/users-management", tags=["Users Management"])
app.include_router(users_simple.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(patients.router, prefix="/api/v1/patients", tags=["Patients"])
app.include_router(appointments.router, prefix="/api/v1/appointments", tags=["Appointments"])
app.include_router(medical_records.router, prefix="/api/v1/medical-records", tags=["Medical Records"])
app.include_router(prescriptions.router, prefix="/api/v1/prescriptions", tags=["Prescriptions"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(file_upload.router, prefix="/api/files", tags=["Files"])
app.include_router(file_download.router, prefix="/api/files", tags=["Files"])
app.include_router(permissions.router, prefix="/api/v1/permissions", tags=["Permissions"])
app.include_router(admin_stats.router, prefix="/api/v1/admin", tags=["Admin Statistics"])

@app.get("/")
def read_root():
    return {"message": "Sanaris Pro API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
