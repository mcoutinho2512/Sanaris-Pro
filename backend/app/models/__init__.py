from app.models.patient import Patient
from app.models.appointment import Appointment, AppointmentWaitlist, ProfessionalSchedule
from app.models.medical_record import MedicalRecord, VitalSigns, MedicalRecordAttachment
from app.models.prescription import Prescription, PrescriptionItem, PrescriptionTemplate
from app.models.document import DocumentTemplate, PatientDocument, QuickPatientRegistration

__all__ = [
    "Patient",
    "Appointment",
    "AppointmentWaitlist",
    "ProfessionalSchedule",
    "MedicalRecord",
    "VitalSigns",
    "MedicalRecordAttachment",
    "Prescription",
    "PrescriptionItem",
    "PrescriptionTemplate",
    "DocumentTemplate",
    "PatientDocument",
    "QuickPatientRegistration"
]
