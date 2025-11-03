"""
Rotas de Extensões do Prontuário
Templates, Exames e Evolução Fotográfica
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from typing import Optional, List
from datetime import datetime
import json

from app.core.database import get_db
from app.models.medical_record_template import MedicalRecordTemplate, ExamResult, PhotoEvolution
from app.models.patient import Patient
from app.schemas.medical_record_extension import (
    MedicalRecordTemplateCreate, MedicalRecordTemplateUpdate, MedicalRecordTemplateResponse,
    ExamResultCreate, ExamResultUpdate, ExamResultResponse, ExamResultListResponse,
    PhotoEvolutionCreate, PhotoEvolutionUpdate, PhotoEvolutionResponse, PhotoEvolutionListResponse,
    ExamChartData, ExamChartRequest, PhotoComparisonRequest
)

router = APIRouter(prefix="/api/v1/medical-records", tags=["Prontuário - Extensões"])


# ============================================
# TEMPLATES DE PRONTUÁRIO
# ============================================

@router.post("/templates", response_model=MedicalRecordTemplateResponse, status_code=status.HTTP_201_CREATED)
def create_template(template_data: MedicalRecordTemplateCreate, db: Session = Depends(get_db)):
    """Cria template de prontuário por especialidade"""
    template = MedicalRecordTemplate(**template_data.dict())
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@router.get("/templates", response_model=List[MedicalRecordTemplateResponse])
def list_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    specialty: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Lista templates de prontuário"""
    query = db.query(MedicalRecordTemplate)
    if specialty:
        query = query.filter(MedicalRecordTemplate.specialty == specialty)
    if is_active is not None:
        query = query.filter(MedicalRecordTemplate.is_active == is_active)
    templates = query.order_by(MedicalRecordTemplate.specialty, MedicalRecordTemplate.name).offset(skip).limit(limit).all()
    return templates


@router.get("/templates/{template_id}", response_model=MedicalRecordTemplateResponse)
def get_template(template_id: str, db: Session = Depends(get_db)):
    """Busca template por ID"""
    template = db.query(MedicalRecordTemplate).filter(MedicalRecordTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template não encontrado")
    return template


@router.put("/templates/{template_id}", response_model=MedicalRecordTemplateResponse)
def update_template(template_id: str, template_data: MedicalRecordTemplateUpdate, db: Session = Depends(get_db)):
    """Atualiza template"""
    template = db.query(MedicalRecordTemplate).filter(MedicalRecordTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template não encontrado")
    update_data = template_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)
    db.commit()
    db.refresh(template)
    return template


@router.delete("/templates/{template_id}")
def delete_template(template_id: str, db: Session = Depends(get_db)):
    """Deleta template"""
    template = db.query(MedicalRecordTemplate).filter(MedicalRecordTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template não encontrado")
    db.delete(template)
    db.commit()
    return {"message": "Template deletado com sucesso", "success": True}


@router.get("/specialties")
def list_specialties(db: Session = Depends(get_db)):
    """Lista especialidades disponíveis"""
    specialties = db.query(MedicalRecordTemplate.specialty).distinct().all()
    return {"specialties": [s[0] for s in specialties]}


# ============================================
# RESULTADOS DE EXAMES
# ============================================

@router.post("/exam-results", response_model=ExamResultResponse, status_code=status.HTTP_201_CREATED)
def create_exam_result(exam_data: ExamResultCreate, db: Session = Depends(get_db)):
    """Registra resultado de exame"""
    patient = db.query(Patient).filter(Patient.id == exam_data.patient_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente não encontrado")
    
    exam = ExamResult(**exam_data.dict())
    db.add(exam)
    db.commit()
    db.refresh(exam)
    return exam


@router.get("/exam-results", response_model=List[ExamResultListResponse])
def list_exam_results(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    patient_id: Optional[str] = None,
    exam_type: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    has_alert: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Lista resultados de exames"""
    query = db.query(ExamResult)
    if patient_id:
        query = query.filter(ExamResult.patient_id == patient_id)
    if exam_type:
        query = query.filter(ExamResult.exam_type == exam_type)
    if date_from:
        query = query.filter(ExamResult.exam_date >= date_from)
    if date_to:
        query = query.filter(ExamResult.exam_date <= date_to)
    if has_alert is not None:
        query = query.filter(ExamResult.has_alert == has_alert)
    
    exams = query.order_by(desc(ExamResult.exam_date)).offset(skip).limit(limit).all()
    return exams


@router.get("/exam-results/{exam_id}", response_model=ExamResultResponse)
def get_exam_result(exam_id: str, db: Session = Depends(get_db)):
    """Busca resultado de exame por ID"""
    exam = db.query(ExamResult).filter(ExamResult.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resultado não encontrado")
    return exam


@router.put("/exam-results/{exam_id}", response_model=ExamResultResponse)
def update_exam_result(exam_id: str, exam_data: ExamResultUpdate, db: Session = Depends(get_db)):
    """Atualiza resultado de exame"""
    exam = db.query(ExamResult).filter(ExamResult.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resultado não encontrado")
    update_data = exam_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(exam, field, value)
    db.commit()
    db.refresh(exam)
    return exam


@router.delete("/exam-results/{exam_id}")
def delete_exam_result(exam_id: str, db: Session = Depends(get_db)):
    """Deleta resultado de exame"""
    exam = db.query(ExamResult).filter(ExamResult.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resultado não encontrado")
    db.delete(exam)
    db.commit()
    return {"message": "Resultado deletado com sucesso", "success": True}


@router.post("/exam-results/chart")
def get_exam_chart(chart_request: ExamChartRequest, db: Session = Depends(get_db)):
    """Gera dados para gráfico de evolução de exames"""
    query = db.query(ExamResult).filter(
        ExamResult.patient_id == chart_request.patient_id,
        ExamResult.exam_type == chart_request.exam_type
    )
    
    if chart_request.date_from:
        query = query.filter(ExamResult.exam_date >= chart_request.date_from)
    if chart_request.date_to:
        query = query.filter(ExamResult.exam_date <= chart_request.date_to)
    
    exams = query.order_by(ExamResult.exam_date).all()
    
    if not exams:
        return {"dates": [], "values": [], "exam_type": chart_request.exam_type}
    
    dates = []
    values = []
    
    for exam in exams:
        try:
            results_data = json.loads(exam.results)
            if isinstance(results_data, dict) and 'value' in results_data:
                dates.append(exam.exam_date.strftime('%d/%m/%Y'))
                values.append(float(results_data['value']))
        except:
            continue
    
    return {
        "exam_type": chart_request.exam_type,
        "dates": dates,
        "values": values,
        "total_exams": len(exams)
    }


# ============================================
# EVOLUÇÃO FOTOGRÁFICA
# ============================================

@router.post("/photo-evolution", response_model=PhotoEvolutionResponse, status_code=status.HTTP_201_CREATED)
def create_photo(photo_data: PhotoEvolutionCreate, db: Session = Depends(get_db)):
    """Adiciona foto de evolução"""
    patient = db.query(Patient).filter(Patient.id == photo_data.patient_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente não encontrado")
    
    photo = PhotoEvolution(**photo_data.dict())
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo


@router.get("/photo-evolution", response_model=List[PhotoEvolutionListResponse])
def list_photos(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    patient_id: Optional[str] = None,
    body_part: Optional[str] = None,
    category: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Lista fotos de evolução"""
    query = db.query(PhotoEvolution)
    if patient_id:
        query = query.filter(PhotoEvolution.patient_id == patient_id)
    if body_part:
        query = query.filter(PhotoEvolution.body_part == body_part)
    if category:
        query = query.filter(PhotoEvolution.category == category)
    if date_from:
        query = query.filter(PhotoEvolution.photo_date >= date_from)
    if date_to:
        query = query.filter(PhotoEvolution.photo_date <= date_to)
    
    photos = query.order_by(desc(PhotoEvolution.photo_date)).offset(skip).limit(limit).all()
    return photos


@router.get("/photo-evolution/{photo_id}", response_model=PhotoEvolutionResponse)
def get_photo(photo_id: str, db: Session = Depends(get_db)):
    """Busca foto por ID"""
    photo = db.query(PhotoEvolution).filter(PhotoEvolution.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Foto não encontrada")
    return photo


@router.put("/photo-evolution/{photo_id}", response_model=PhotoEvolutionResponse)
def update_photo(photo_id: str, photo_data: PhotoEvolutionUpdate, db: Session = Depends(get_db)):
    """Atualiza informações da foto"""
    photo = db.query(PhotoEvolution).filter(PhotoEvolution.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Foto não encontrada")
    update_data = photo_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(photo, field, value)
    db.commit()
    db.refresh(photo)
    return photo


@router.delete("/photo-evolution/{photo_id}")
def delete_photo(photo_id: str, db: Session = Depends(get_db)):
    """Deleta foto"""
    photo = db.query(PhotoEvolution).filter(PhotoEvolution.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Foto não encontrada")
    db.delete(photo)
    db.commit()
    return {"message": "Foto deletada com sucesso", "success": True}


@router.post("/photo-evolution/comparison")
def compare_photos(comparison_request: PhotoComparisonRequest, db: Session = Depends(get_db)):
    """Retorna fotos para comparação lado a lado"""
    query = db.query(PhotoEvolution).filter(PhotoEvolution.patient_id == comparison_request.patient_id)
    
    if comparison_request.body_part:
        query = query.filter(PhotoEvolution.body_part == comparison_request.body_part)
    if comparison_request.category:
        query = query.filter(PhotoEvolution.category == comparison_request.category)
    if comparison_request.date_from:
        query = query.filter(PhotoEvolution.photo_date >= comparison_request.date_from)
    if comparison_request.date_to:
        query = query.filter(PhotoEvolution.photo_date <= comparison_request.date_to)
    
    photos = query.order_by(PhotoEvolution.photo_date).all()
    
    return {
        "patient_id": comparison_request.patient_id,
        "total_photos": len(photos),
        "photos": [
            {
                "id": photo.id,
                "title": photo.title,
                "photo_date": photo.photo_date,
                "body_part": photo.body_part,
                "angle": photo.angle,
                "category": photo.category,
                "file_url": photo.file_url,
                "thumbnail_url": photo.thumbnail_url
            }
            for photo in photos
        ]
    }


@router.get("/photo-evolution/body-parts")
def list_body_parts(patient_id: Optional[str] = None, db: Session = Depends(get_db)):
    """Lista partes do corpo fotografadas"""
    query = db.query(PhotoEvolution.body_part).distinct()
    if patient_id:
        query = query.filter(PhotoEvolution.patient_id == patient_id)
    body_parts = query.all()
    return {"body_parts": [bp[0] for bp in body_parts if bp[0]]}
