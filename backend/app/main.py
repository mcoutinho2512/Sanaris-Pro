from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Sanaris Pro API",
    description="Sistema de Gestão de Clínicas e Consultórios",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8888"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "message": "🏥 Sanaris Pro API",
        "version": "1.0.0",
        "status": "online",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "sanaris-pro-api",
        "port": 8888,
        "database": "configured",
        "redis": "configured"
    }

@app.get("/api/v1/status")
def api_status():
    return {
        "api": "Sanaris Pro",
        "version": "1.0.0",
        "phase": "Phase 1 - Core Infrastructure",
        "modules": {
            "auth": "✅ Ready to implement",
            "scheduling": "⏳ Phase 2",
            "medical_records": "⏳ Phase 2",
            "prescriptions": "⏳ Phase 2"
        }
    }
