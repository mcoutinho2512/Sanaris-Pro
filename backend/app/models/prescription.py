"""
Modelos de Prescrição Digital - COMPLETO
Inclui: Prescription, PrescriptionItem, PrescriptionTemplate
"""
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text, Integer, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import uuid


class Prescription(Base):
    """Prescrição Digital - Documento principal"""
    __tablename__ = "prescriptions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False, index=True)
    medical_record_id = Column(String(36), ForeignKey("medical_records.id"), index=True)
    healthcare_professional_id = Column(String(36), nullable=False, index=True)
    
    # Data da prescrição
    prescription_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Tipo de prescrição
    prescription_type = Column(String(50), default="regular")  # regular, controlled, special
    
    # Validade
    valid_until = Column(DateTime)  # Data de validade da receita
    
    # Instruções gerais
    general_instructions = Column(Text)  # Orientações gerais ao paciente
    
    # Controle
    is_printed = Column(Boolean, default=False)
    printed_at = Column(DateTime)
    
    is_signed = Column(Boolean, default=False)
    signed_at = Column(DateTime)
    
    # Assinatura digital
    professional_signature = Column(Text)  # Hash da assinatura
    crm_number = Column(String(20))
    crm_state = Column(String(2))
    
    # Controle de dispensação (farmácia)
    is_dispensed = Column(Boolean, default=False)
    dispensed_at = Column(DateTime)
    pharmacy_name = Column(String(255))
    pharmacist_name = Column(String(255))
    
    # Observações
    notes = Column(Text)  # Observações internas
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    patient = relationship("Patient", back_populates="prescriptions")
    items = relationship("PrescriptionItem", back_populates="prescription", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Prescription {self.id} - Patient {self.patient_id}>"


class PrescriptionItem(Base):
    """Item da Prescrição - Medicamento individual"""
    __tablename__ = "prescription_items"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    prescription_id = Column(String(36), ForeignKey("prescriptions.id"), nullable=False, index=True)
    
    # Medicamento
    medication_name = Column(String(255), nullable=False)  # Nome comercial ou genérico
    active_ingredient = Column(String(255))  # Princípio ativo
    concentration = Column(String(100))  # Ex: 500mg, 10mg/ml
    pharmaceutical_form = Column(String(100))  # Comprimido, cápsula, xarope, etc
    
    # Posologia
    dosage = Column(String(255), nullable=False)  # Ex: "1 comprimido"
    frequency = Column(String(255), nullable=False)  # Ex: "de 8 em 8 horas", "3x ao dia"
    duration = Column(String(100))  # Ex: "por 7 dias", "uso contínuo"
    route_of_administration = Column(String(100))  # Via oral, tópica, etc
    
    # Quantidade
    quantity = Column(Integer)  # Quantidade a ser dispensada
    quantity_unit = Column(String(50))  # Unidade: comprimidos, frascos, caixas
    
    # Instruções específicas
    instructions = Column(Text)  # Ex: "tomar em jejum", "evitar exposição ao sol"
    
    # Controle
    is_generic = Column(Boolean, default=False)  # Se aceita genérico
    is_controlled = Column(Boolean, default=False)  # Medicamento controlado
    
    # Ordem de exibição
    display_order = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    prescription = relationship("Prescription", back_populates="items")
    
    def __repr__(self):
        return f"<PrescriptionItem {self.medication_name} - {self.dosage}>"


class PrescriptionTemplate(Base):
    """Modelo de Prescrição - Templates prontos e customizáveis"""
    __tablename__ = "prescription_templates"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    healthcare_professional_id = Column(String(36), nullable=False, index=True)
    
    # Informações do template
    template_name = Column(String(255), nullable=False)  # Ex: "Tratamento Hipertensão", "Resfriado Comum"
    description = Column(Text)
    
    # Categoria
    category = Column(String(100))  # Ex: "Cardiologia", "Pediatria", "Uso Geral"
    
    # Uso
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)  # Se pode ser usado por outros profissionais
    usage_count = Column(Integer, default=0)  # Contador de usos
    
    # Template em JSON
    template_data = Column(Text)  # JSON com os medicamentos do template
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_used_at = Column(DateTime)
    
    def __repr__(self):
        return f"<PrescriptionTemplate {self.template_name}>"
