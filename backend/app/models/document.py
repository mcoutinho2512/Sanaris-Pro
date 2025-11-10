"""
Modelos de Documentos e Termos
"""
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import uuid


class DocumentTemplate(Base):
    """Template de documento/termo"""
    __tablename__ = "document_templates"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Informações do template
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Tipo de documento
    document_type = Column(String(50), nullable=False)  # term, consent, contract, declaration
    
    # Categoria
    category = Column(String(100))  # appointment, treatment, surgery, anesthesia, etc
    
    # Conteúdo do template (HTML ou texto com variáveis)
    content = Column(Text, nullable=False)
    
    # Variáveis disponíveis (JSON)
    available_variables = Column(Text)  # {patient_name}, {date}, {professional_name}, etc
    
    # Configurações
    requires_signature = Column(Boolean, default=True)
    requires_witness = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<DocumentTemplate {self.name}>"


class PatientDocument(Base):
    """Documento gerado para paciente"""
    __tablename__ = "patient_documents"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False, index=True)
    appointment_id = Column(String(36), ForeignKey("appointments.id"), index=True)
    template_id = Column(String(36), ForeignKey("document_templates.id"), index=True)
    
    # Informações do documento
    document_type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    
    # Conteúdo gerado
    content = Column(Text, nullable=False)  # HTML ou texto final
    
    # Arquivo gerado (PDF)
    file_path = Column(String(500))
    file_url = Column(String(500))
    
    # Assinaturas
    patient_signature = Column(Text)  # Base64 ou URL
    patient_signed_at = Column(DateTime)
    
    witness_name = Column(String(255))
    witness_signature = Column(Text)
    witness_signed_at = Column(DateTime)
    
    professional_signature = Column(Text)
    professional_signed_at = Column(DateTime)
    
    # Status
    is_signed = Column(Boolean, default=False)
    is_sent = Column(Boolean, default=False)
    sent_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    patient = relationship("Patient", )
    template = relationship("DocumentTemplate")
    
    def __repr__(self):
        return f"<PatientDocument {self.title}>"


class QuickPatientRegistration(Base):
    """Pré-cadastro rápido de paciente no agendamento"""
    __tablename__ = "quick_patient_registrations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Dados básicos obrigatórios
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False, index=True)
    
    # Dados opcionais
    cpf = Column(String(14), index=True)
    email = Column(String(255))
    birth_date = Column(DateTime)
    
    # Status
    is_converted = Column(Boolean, default=False)  # Se virou paciente completo
    patient_id = Column(String(36), ForeignKey("patients.id"))  # ID do paciente completo
    converted_at = Column(DateTime)
    
    # Origem
    created_by = Column(String(255))  # Quem cadastrou
    appointment_id = Column(String(36), ForeignKey("appointments.id"))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<QuickPatientRegistration {self.full_name}>"
