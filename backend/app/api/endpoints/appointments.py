from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.appointment import Appointment
from app.schemas.appointment import AppointmentCreate, AppointmentResponse

router = APIRouter(prefix="/api/v1/appointments", tags=["appointments"])

@router.post("/", response_model=AppointmentResponse)
def create_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db)):
    db_appointment = Appointment(**appointment.dict())
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

@router.get("/", response_model=List[AppointmentResponse])
def list_appointments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    appointments = db.query(Appointment).offset(skip).limit(limit).all()
    return appointments

@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(appointment_id: str, db: Session = Depends(get_db)):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment
