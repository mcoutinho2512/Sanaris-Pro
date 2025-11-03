"""
Rotas de Prontuário Eletrônico - COMPLETO
CRUD completo + Sinais Vitais + Anexos + Linha do Tempo
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional, List
from datetime import datetime, date

from app.core.database import get_db
from app.models.medical_record import MedicalRecord, VitalSigns, MedicalRecordAttachment
from app.models.patient import Patient
from app.schemas.medical_record import (
    MedicalRecordCreate, MedicalRecordUpdate, MedicalRecordResponse,
    MedicalRecordListResponse, VitalSignsCreate, VitalSignsUpdate,
    VitalSignsResponse, AttachmentCreate, AttachmentResponse,
    RecordType
)

router = APIRouter(prefix="/api/v1/medical-records", tags=["Prontuários"])


# ============================================
# CRUD DE PRONTUÁRIOS
# ============================================

@router.post("/", response_model=MedicalRecordResponse, status_code=status.HTTP_201_CREATED)
def create_medical_record(
    record_data: MedicalRecordCreate,
    db: Session = Depends(get_db)
):
    """Cria um novo prontuário eletrônico"""
    
    # Verifica se paciente existe
    patient = db.query(Patient).filter(Patient.id == record_data.patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente não encontrado"
        )
    
    # Define data do registro se não informada
    if not record_data.record_date:
        record_data.record_date = datetime.utcnow()
    
    # Cria prontuário
    record = MedicalRecord(**record_data.dict())
    db.add(record)
    db.commit()
    db.refresh(record)
    
    return record


@router.get("/", response_model=List[MedicalRecordListResponse])
def list_medical_records(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    patient_id: Optional[str] = None,
    professional_id: Optional[str] = None,
    record_type: Optional[RecordType] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    is_completed: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    Lista prontuários com filtros avançados
    
    Filtros disponíveis:
    - patient_id: filtra por paciente
    - professional_id: filtra por profissional
    - record_type: filtra por tipo de atendimento
    - date_from/date_to: filtra por período
    - is_completed: filtra por status de conclusão
    """
    
    query = db.query(MedicalRecord)
    
    # Aplicar filtros
    if patient_id:
        query = query.filter(MedicalRecord.patient_id == patient_id)
    
    if professional_id:
        query = query.filter(MedicalRecord.healthcare_professional_id == professional_id)
    
    if record_type:
        query = query.filter(MedicalRecord.record_type == record_type)
    
    if date_from:
        query = query.filter(func.date(MedicalRecord.record_date) >= date_from)
    
    if date_to:
        query = query.filter(func.date(MedicalRecord.record_date) <= date_to)
    
    if is_completed is not None:
        query = query.filter(MedicalRecord.is_completed == is_completed)
    
    # Ordenar por data (mais recente primeiro)
    query = query.order_by(desc(MedicalRecord.record_date))
    
    records = query.offset(skip).limit(limit).all()
    return records


@router.get("/{record_id}", response_model=MedicalRecordResponse)
def get_medical_record(record_id: str, db: Session = Depends(get_db)):
    """Busca um prontuário completo por ID"""
    
    record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prontuário não encontrado"
        )
    
    return record


@router.put("/{record_id}", response_model=MedicalRecordResponse)
def update_medical_record(
    record_id: str,
    record_data: MedicalRecordUpdate,
    db: Session = Depends(get_db)
):
    """Atualiza um prontuário"""
    
    record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prontuário não encontrado"
        )
    
    # Verifica se está bloqueado
    if record.is_locked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Prontuário bloqueado para edição"
        )
    
    # Atualiza campos
    update_data = record_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(record, field, value)
    
    # Se marcado como completo, registra timestamp
    if update_data.get('is_completed') and not record.completed_at:
        record.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(record)
    
    return record


@router.delete("/{record_id}")
def delete_medical_record(record_id: str, db: Session = Depends(get_db)):
    """Deleta um prontuário"""
    
    record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prontuário não encontrado"
        )
    
    # Verifica se está bloqueado
    if record.is_locked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Prontuário bloqueado não pode ser deletado"
        )
    
    db.delete(record)
    db.commit()
    
    return {"message": "Prontuário deletado com sucesso", "success": True}



# ============================================
# AÇÕES ESPECIAIS DO PRONTUÁRIO
# ============================================

@router.post("/{record_id}/complete", response_model=MedicalRecordResponse)
def complete_medical_record(record_id: str, db: Session = Depends(get_db)):
    """Marca prontuário como concluído"""
    
    record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prontuário não encontrado"
        )
    
    record.is_completed = True
    record.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(record)
    
    return record


@router.post("/{record_id}/lock", response_model=MedicalRecordResponse)
def lock_medical_record(record_id: str, db: Session = Depends(get_db)):
    """Bloqueia prontuário para edição"""
    
    record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prontuário não encontrado"
        )
    
    if not record.is_completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apenas prontuários concluídos podem ser bloqueados"
        )
    
    record.is_locked = True
    
    db.commit()
    db.refresh(record)
    
    return record


# ============================================
# SINAIS VITAIS
# ============================================

@router.post("/{record_id}/vital-signs", response_model=VitalSignsResponse, status_code=status.HTTP_201_CREATED)
def add_vital_signs(
    record_id: str,
    vital_data: VitalSignsCreate,
    db: Session = Depends(get_db)
):
    """Adiciona sinais vitais ao prontuário"""
    
    record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prontuário não encontrado"
        )
    
    # Define timestamp se não informado
    if not vital_data.measured_at:
        vital_data.measured_at = datetime.utcnow()
    
    # Calcula IMC se tiver peso e altura
    if vital_data.weight and vital_data.height:
        height_m = float(vital_data.height) / 100
        vital_data.bmi = float(vital_data.weight) / (height_m ** 2)
    
    # Cria registro de sinais vitais
    vital_signs = VitalSigns(
        medical_record_id=record_id,
        **vital_data.dict()
    )
    db.add(vital_signs)
    db.commit()
    db.refresh(vital_signs)
    
    return vital_signs


@router.get("/{record_id}/vital-signs", response_model=List[VitalSignsResponse])
def get_vital_signs(record_id: str, db: Session = Depends(get_db)):
    """Lista todos os sinais vitais de um prontuário"""
    
    vital_signs = db.query(VitalSigns).filter(
        VitalSigns.medical_record_id == record_id
    ).order_by(VitalSigns.measured_at).all()
    
    return vital_signs


@router.put("/vital-signs/{vital_id}", response_model=VitalSignsResponse)
def update_vital_signs(
    vital_id: str,
    vital_data: VitalSignsUpdate,
    db: Session = Depends(get_db)
):
    """Atualiza sinais vitais"""
    
    vital_signs = db.query(VitalSigns).filter(VitalSigns.id == vital_id).first()
    
    if not vital_signs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sinais vitais não encontrados"
        )
    
    # Atualiza campos
    update_data = vital_data.dict(exclude_unset=True)
    
    # Recalcula IMC se alterou peso ou altura
    if 'weight' in update_data or 'height' in update_data:
        weight = update_data.get('weight', vital_signs.weight)
        height = update_data.get('height', vital_signs.height)
        if weight and height:
            height_m = float(height) / 100
            update_data['bmi'] = float(weight) / (height_m ** 2)
    
    for field, value in update_data.items():
        setattr(vital_signs, field, value)
    
    db.commit()
    db.refresh(vital_signs)
    
    return vital_signs


@router.delete("/vital-signs/{vital_id}")
def delete_vital_signs(vital_id: str, db: Session = Depends(get_db)):
    """Remove registro de sinais vitais"""
    
    vital_signs = db.query(VitalSigns).filter(VitalSigns.id == vital_id).first()
    
    if not vital_signs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sinais vitais não encontrados"
        )
    
    db.delete(vital_signs)
    db.commit()
    
    return {"message": "Sinais vitais deletados com sucesso", "success": True}



# ============================================
# ANEXOS / REPOSITÓRIO DE MÍDIAS
# ============================================

@router.post("/{record_id}/attachments", response_model=AttachmentResponse, status_code=status.HTTP_201_CREATED)
def add_attachment(
    record_id: str,
    attachment_data: AttachmentCreate,
    db: Session = Depends(get_db)
):
    """Adiciona anexo ao prontuário"""
    
    record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prontuário não encontrado"
        )
    
    # Cria anexo
    attachment = MedicalRecordAttachment(
        medical_record_id=record_id,
        **attachment_data.dict()
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    
    return attachment


@router.get("/{record_id}/attachments", response_model=List[AttachmentResponse])
def get_attachments(record_id: str, db: Session = Depends(get_db)):
    """Lista todos os anexos de um prontuário"""
    
    attachments = db.query(MedicalRecordAttachment).filter(
        MedicalRecordAttachment.medical_record_id == record_id
    ).order_by(MedicalRecordAttachment.uploaded_at).all()
    
    return attachments


@router.delete("/attachments/{attachment_id}")
def delete_attachment(attachment_id: str, db: Session = Depends(get_db)):
    """Remove anexo"""
    
    attachment = db.query(MedicalRecordAttachment).filter(
        MedicalRecordAttachment.id == attachment_id
    ).first()
    
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Anexo não encontrado"
        )
    
    db.delete(attachment)
    db.commit()
    
    return {"message": "Anexo deletado com sucesso", "success": True}


# ============================================
# LINHA DO TEMPO / HISTÓRICO
# ============================================

@router.get("/patient/{patient_id}/timeline", response_model=List[MedicalRecordListResponse])
def get_patient_timeline(
    patient_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Retorna linha do tempo completa do paciente
    Ordenado por data (mais recente primeiro)
    """
    
    # Verifica se paciente existe
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente não encontrado"
        )
    
    records = db.query(MedicalRecord).filter(
        MedicalRecord.patient_id == patient_id
    ).order_by(desc(MedicalRecord.record_date)).offset(skip).limit(limit).all()
    
    return records


@router.get("/patient/{patient_id}/summary")
def get_patient_summary(patient_id: str, db: Session = Depends(get_db)):
    """
    Retorna resumo do histórico médico do paciente
    """
    
    # Verifica se paciente existe
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente não encontrado"
        )
    
    # Total de atendimentos
    total_records = db.query(func.count(MedicalRecord.id)).filter(
        MedicalRecord.patient_id == patient_id
    ).scalar()
    
    # Último atendimento
    last_record = db.query(MedicalRecord).filter(
        MedicalRecord.patient_id == patient_id
    ).order_by(desc(MedicalRecord.record_date)).first()
    
    # Atendimentos por tipo
    records_by_type = db.query(
        MedicalRecord.record_type,
        func.count(MedicalRecord.id)
    ).filter(
        MedicalRecord.patient_id == patient_id
    ).group_by(MedicalRecord.record_type).all()
    
    # Últimos sinais vitais
    last_vital_signs = None
    if last_record:
        last_vital_signs = db.query(VitalSigns).filter(
            VitalSigns.medical_record_id == last_record.id
        ).order_by(desc(VitalSigns.measured_at)).first()
    
    return {
        "patient_id": patient_id,
        "total_records": total_records,
        "last_record_date": last_record.record_date if last_record else None,
        "last_diagnosis": last_record.diagnosis if last_record else None,
        "records_by_type": {rt: count for rt, count in records_by_type},
        "last_vital_signs": {
            "blood_pressure": f"{last_vital_signs.systolic_pressure}/{last_vital_signs.diastolic_pressure}" if last_vital_signs and last_vital_signs.systolic_pressure else None,
            "heart_rate": last_vital_signs.heart_rate if last_vital_signs else None,
            "temperature": float(last_vital_signs.temperature) if last_vital_signs and last_vital_signs.temperature else None,
            "weight": float(last_vital_signs.weight) if last_vital_signs and last_vital_signs.weight else None,
            "bmi": float(last_vital_signs.bmi) if last_vital_signs and last_vital_signs.bmi else None,
        } if last_vital_signs else None
    }


# ============================================
# ESTATÍSTICAS E RELATÓRIOS
# ============================================

@router.get("/statistics")
def get_statistics(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    professional_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Retorna estatísticas gerais de prontuários"""
    
    query = db.query(MedicalRecord)
    
    # Aplicar filtros de data
    if date_from:
        query = query.filter(func.date(MedicalRecord.record_date) >= date_from)
    if date_to:
        query = query.filter(func.date(MedicalRecord.record_date) <= date_to)
    if professional_id:
        query = query.filter(MedicalRecord.healthcare_professional_id == professional_id)
    
    # Total de prontuários
    total = query.count()
    
    # Prontuários concluídos
    completed = query.filter(MedicalRecord.is_completed == True).count()
    
    # Prontuários por tipo
    by_type = db.query(
        MedicalRecord.record_type,
        func.count(MedicalRecord.id)
    ).filter(
        MedicalRecord.id.in_(query.with_entities(MedicalRecord.id))
    ).group_by(MedicalRecord.record_type).all()
    
    return {
        "total_records": total,
        "completed_records": completed,
        "pending_records": total - completed,
        "completion_rate": round((completed / total * 100), 2) if total > 0 else 0,
        "records_by_type": {rt: count for rt, count in by_type}
    }

