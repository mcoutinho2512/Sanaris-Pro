from app.core.database import Base

# Importar modelos diretamente sem passar pelo __init__.py
from app.models.user import User

# Importar outros modelos individualmente
try:
    from app.models.patient import Patient
except:
    pass

try:
    from app.models.appointment import Appointment
except:
    pass

try:
    from app.models.medical_record import MedicalRecord
except:
    pass

try:
    from app.models.prescription import Prescription, PrescriptionItem
except:
    pass

__all__ = ["Base"]
