from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importar todos os endpoints
from app.api.endpoints import auth, organizations, users_management, chat, patients, permissions, admin_stats

app = FastAPI(
    title="Sanaris Pro API",
    description="Sistema de Gestão de Clínicas",
    version="2.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Incluir rotas
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(organizations.router, prefix="/api/v1/organizations", tags=["Organizations"])
app.include_router(users_management.router, prefix="/api/v1/users-management", tags=["Users Management"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])
app.include_router(patients.router, prefix="/api/v1/patients", tags=["Patients"])
app.include_router(permissions.router, prefix="/api/v1/permissions", tags=["Permissions"])
app.include_router(admin_stats.router, prefix="/api/v1/admin", tags=["Admin Statistics"])

@app.get("/")
def read_root():
    return {
        "message": "Sanaris Pro API",
        "version": "2.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}
