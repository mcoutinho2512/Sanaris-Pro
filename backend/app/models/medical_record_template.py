"""
Templates de Prontuário por Especialidade
"""
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer
from datetime import datetime
from app.core.database import Base
import uuid


class MedicalRecordTemplate(Base):
    """Template de prontuário por especialidade"""
    __tablename__ = "medical_record_templates"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Identificação
    name = Column(String(255), nullable=False)
    specialty = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    
    # Configuração de campos
    anamnesis_fields = Column(Text)  # JSON com campos customizados
    physical_exam_fields = Column(Text)  # JSON com campos customizados
    
    # Campos específicos da especialidade
    specialty_fields = Column(Text)  # JSON com campos extras
    
    # Configurações de exibição
    field_order = Column(Text)  # JSON com ordem dos campos
    required_fields = Column(Text)  # JSON com campos obrigatórios
    hidden_fields = Column(Text)  # JSON com campos ocultos
    
    # Valores padrão
    default_values = Column(Text)  # JSON com valores padrão
    
    # Controle
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    usage_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<MedicalRecordTemplate {self.name} - {self.specialty}>"


class ExamResult(Base):
    """Resultado de exame do paciente"""
    __tablename__ = "exam_results"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String(36), nullable=False, index=True)
    medical_record_id = Column(String(36), index=True)
    
    # Informações do exame
    exam_type = Column(String(100), nullable=False)
    exam_name = Column(String(255), nullable=False)
    exam_date = Column(DateTime, nullable=False, index=True)
    
    # Resultados (JSON para flexibilidade)
    results = Column(Text, nullable=False)
    
    # Valores de referência
    reference_values = Column(Text)
    
    # Status
    is_normal = Column(Boolean)
    has_alert = Column(Boolean, default=False)
    alert_message = Column(Text)
    
    # Arquivo
    file_path = Column(String(500))
    file_url = Column(String(500))
    
    # Observações
    observations = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ExamResult {self.exam_name} - {self.exam_date}>"


class PhotoEvolution(Base):
    """Evolução fotográfica do paciente"""
    __tablename__ = "photo_evolutions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String(36), nullable=False, index=True)
    medical_record_id = Column(String(36), index=True)
    
    # Informações da foto
    title = Column(String(255), nullable=False)
    description = Column(Text)
    photo_date = Column(DateTime, nullable=False, index=True)
    
    # Classificação
    body_part = Column(String(100))
    angle = Column(String(50))
    category = Column(String(100))
    
    # Arquivo
    file_path = Column(String(500), nullable=False)
    file_url = Column(String(500))
    thumbnail_url = Column(String(500))
    
    # Metadados
    treatment_phase = Column(String(100))
    session_number = Column(Integer)
    
    # Observações
    observations = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<PhotoEvolution {self.title} - {self.photo_date}>"
