import { api } from '@/lib/api';

export enum RecordType {
  CONSULTATION = 'consultation',
  EMERGENCY = 'emergency',
  FOLLOWUP = 'followup',
  TELEMEDICINE = 'telemedicine',
}

export interface MedicalRecord {
  id: string;
  patient_id: string;
  appointment_id?: string;
  healthcare_professional_id: string;
  record_date: string;
  record_type: RecordType;
  
  // Triagem
  chief_complaint?: string;
  history_of_present_illness?: string;
  
  // Anamnese
  past_medical_history?: string;
  medications?: string;
  allergies?: string;
  family_history?: string;
  social_history?: string;
  review_of_systems?: string;
  
  // Exame Físico
  general_appearance?: string;
  head_neck?: string;
  cardiovascular?: string;
  respiratory?: string;
  abdomen?: string;
  extremities?: string;
  neurological?: string;
  skin?: string;
  additional_findings?: string;
  
  // Diagnóstico e Conduta
  diagnosis?: string;
  icd10_codes?: string;
  treatment_plan?: string;
  prescriptions?: string;
  exams_requested?: string;
  referrals?: string;
  observations?: string;
  
  // Retorno
  followup_date?: string;
  followup_notes?: string;
  
  // Controle
  is_completed: boolean;
  completed_at?: string;
  is_locked: boolean;
  
  // Assinatura
  professional_signature?: string;
  crm_number?: string;
  crm_state?: string;
  
  created_at: string;
  updated_at: string;
}

export interface MedicalRecordCreate {
  patient_id: string;
  appointment_id?: string;
  healthcare_professional_id: string;
  record_type?: RecordType;
  record_date?: string;
  
  chief_complaint?: string;
  history_of_present_illness?: string;
  past_medical_history?: string;
  medications?: string;
  allergies?: string;
  diagnosis?: string;
  treatment_plan?: string;
  prescriptions?: string;
  exams_requested?: string;
  observations?: string;
}

export interface MedicalRecordUpdate {
  chief_complaint?: string;
  history_of_present_illness?: string;
  past_medical_history?: string;
  medications?: string;
  allergies?: string;
  family_history?: string;
  social_history?: string;
  review_of_systems?: string;
  general_appearance?: string;
  head_neck?: string;
  cardiovascular?: string;
  respiratory?: string;
  abdomen?: string;
  extremities?: string;
  neurological?: string;
  skin?: string;
  additional_findings?: string;
  diagnosis?: string;
  icd10_codes?: string;
  treatment_plan?: string;
  prescriptions?: string;
  exams_requested?: string;
  referrals?: string;
  observations?: string;
  followup_date?: string;
  followup_notes?: string;
  professional_signature?: string;
  crm_number?: string;
  crm_state?: string;
}

export const medicalRecordsService = {
  async list(params?: {
    skip?: number;
    limit?: number;
    patient_id?: string;
    professional_id?: string;
    record_type?: RecordType;
    date_from?: string;
    date_to?: string;
    is_completed?: boolean;
  }): Promise<MedicalRecord[]> {
    const queryParams = new URLSearchParams();
    if (params?.skip) queryParams.append('skip', params.skip.toString());
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.patient_id) queryParams.append('patient_id', params.patient_id);
    if (params?.professional_id) queryParams.append('professional_id', params.professional_id);
    if (params?.record_type) queryParams.append('record_type', params.record_type);
    if (params?.date_from) queryParams.append('date_from', params.date_from);
    if (params?.date_to) queryParams.append('date_to', params.date_to);
    if (params?.is_completed !== undefined) queryParams.append('is_completed', params.is_completed.toString());

    const response = await api.get(`/api/v1/medical-records/?${queryParams.toString()}`);
    return response.data;
  },

  async get(id: string): Promise<MedicalRecord> {
    const response = await api.get(`/api/v1/medical-records/${id}`);
    return response.data;
  },

  async create(data: MedicalRecordCreate): Promise<MedicalRecord> {
    const response = await api.post('/api/v1/medical-records/', data);
    return response.data;
  },

  async update(id: string, data: MedicalRecordUpdate): Promise<MedicalRecord> {
    const response = await api.put(`/api/v1/medical-records/${id}`, data);
    return response.data;
  },

  async delete(id: string): Promise<void> {
    await api.delete(`/api/v1/medical-records/${id}`);
  },

  async complete(id: string): Promise<MedicalRecord> {
    const response = await api.post(`/api/v1/medical-records/${id}/complete`);
    return response.data;
  },
};
