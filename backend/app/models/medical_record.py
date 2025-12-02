"""
Modelos de Prontuário Eletrônico - COMPLETO
Inclui: MedicalRecord, VitalSigns, MedicalRecordAttachment
"""
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text, Integer, Numeric, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import uuid


class MedicalRecord(Base):
    """Prontuário Eletrônico - Registro principal"""
    __tablename__ = "medical_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False, index=True)
    appointment_id = Column(UUID(as_uuid=True), ForeignKey("appointments.id"), index=True)
    healthcare_professional_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Data do atendimento
    record_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Tipo de atendimento
    record_type = Column(String(50), default="consultation")  # consultation, emergency, followup, telemedicine
    
    # TRIAGEM / PRÉ-CONSULTA
    chief_complaint = Column(Text)  # Queixa principal
    history_of_present_illness = Column(Text)  # História da doença atual (HDA)
    
    # ANAMNESE COMPLETA
    past_medical_history = Column(Text)  # História patológica pregressa
    medications = Column(Text)  # Medicamentos em uso
    allergies = Column(Text)  # Alergias
    family_history = Column(Text)  # História familiar
    social_history = Column(Text)  # História social
    review_of_systems = Column(Text)  # Revisão de sistemas
    
    # EXAME FÍSICO
    general_appearance = Column(Text)  # Aspecto geral
    head_neck = Column(Text)  # Cabeça e pescoço
    cardiovascular = Column(Text)  # Cardiovascular
    respiratory = Column(Text)  # Respiratório
    abdomen = Column(Text)  # Abdômen
    extremities = Column(Text)  # Extremidades
    neurological = Column(Text)  # Neurológico
    skin = Column(Text)  # Pele
    additional_findings = Column(Text)  # Achados adicionais
    
    # DIAGNÓSTICO E CONDUTA
    diagnosis = Column(Text)  # Diagnóstico / Hipótese diagnóstica
    icd10_codes = Column(Text)  # Códigos CID-10 (separados por vírgula)
    treatment_plan = Column(Text)  # Plano de tratamento
    prescriptions = Column(Text)  # Prescrições
    exams_requested = Column(Text)  # Exames solicitados
    referrals = Column(Text)  # Encaminhamentos
    observations = Column(Text)  # Observações gerais
    
    # RETORNO
    followup_date = Column(Date)  # Data de retorno
    followup_notes = Column(Text)  # Orientações para retorno
    
    # CONTROLE
    is_completed = Column(Boolean, default=False)  # Prontuário finalizado
    completed_at = Column(DateTime)
    is_locked = Column(Boolean, default=False)  # Bloqueado para edição
    
    # Assinatura digital (CREMERJ)
    professional_signature = Column(Text)  # Assinatura profissional
    crm_number = Column(String(20))  # CRM
    crm_state = Column(String(2))  # UF do CRM
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    patient = relationship("Patient", )
    vital_signs = relationship("VitalSigns", back_populates="medical_record", cascade="all, delete-orphan")
    attachments = relationship("MedicalRecordAttachment", back_populates="medical_record", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<MedicalRecord {self.id} - Patient {self.patient_id}>"


class VitalSigns(Base):
    """Sinais Vitais"""
    __tablename__ = "vital_signs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    medical_record_id = Column(UUID(as_uuid=True), ForeignKey("medical_records.id"), nullable=False, index=True)
    
    # Data/hora da medição
    measured_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Sinais Vitais
    systolic_pressure = Column(Integer)  # Pressão arterial sistólica (mmHg)
    diastolic_pressure = Column(Integer)  # Pressão arterial diastólica (mmHg)
    heart_rate = Column(Integer)  # Frequência cardíaca (bpm)
    respiratory_rate = Column(Integer)  # Frequência respiratória (irpm)
    temperature = Column(Numeric(4, 1))  # Temperatura (°C)
    oxygen_saturation = Column(Integer)  # Saturação O2 (%)
    
    # Medidas Antropométricas
    weight = Column(Numeric(5, 2))  # Peso (kg)
    height = Column(Numeric(5, 2))  # Altura (cm)
    bmi = Column(Numeric(5, 2))  # IMC (calculado)
    
    # Glicemia
    glucose = Column(Integer)  # Glicemia (mg/dL)
    
    # Observações
    notes = Column(Text)
    
    # Quem mediu
    measured_by = Column(String(255))  # Nome de quem realizou a medição
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    medical_record = relationship("MedicalRecord", back_populates="vital_signs")
    
    def __repr__(self):
        return f"<VitalSigns {self.id} - PA: {self.systolic_pressure}/{self.diastolic_pressure}>"


class MedicalRecordAttachment(Base):
    """Anexos do Prontuário (exames, imagens, documentos)"""
    __tablename__ = "medical_record_attachments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    medical_record_id = Column(UUID(as_uuid=True), ForeignKey("medical_records.id"), nullable=False, index=True)
    
    # Informações do arquivo
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(50))  # pdf, jpg, png, dicom, etc
    file_size = Column(Integer)  # Tamanho em bytes
    file_path = Column(String(500))  # Caminho no storage
    file_url = Column(String(500))  # URL para acesso
    
    # Tipo de anexo
    attachment_type = Column(String(50))  # exam, image, document, prescription, other
    
    # Descrição
    description = Column(Text)
    
    # Metadados
    uploaded_by = Column(UUID(as_uuid=True))  # ID do usuário que fez upload
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    medical_record = relationship("MedicalRecord", back_populates="attachments")
    
    def __repr__(self):
        return f"<MedicalRecordAttachment {self.id} - {self.file_name}>"
