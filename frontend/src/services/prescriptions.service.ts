import { api } from '@/lib/api';

export enum PrescriptionType {
  REGULAR = 'regular',
  CONTROLLED = 'controlled',
  SPECIAL = 'special',
}

export interface PrescriptionItem {
  id?: string;
  medication_name: string;
  active_ingredient?: string;
  concentration?: string;
  pharmaceutical_form?: string;
  dosage: string;
  frequency: string;
  duration?: string;
  route_of_administration?: string;
  quantity?: number;
  quantity_unit?: string;
  instructions?: string;
  is_generic: boolean;
  is_controlled: boolean;
  display_order: number;
}

export interface Prescription {
  id: string;
  patient_id: string;
  medical_record_id?: string;
  healthcare_professional_id: string;
  prescription_date: string;
  prescription_type: PrescriptionType;
  valid_until?: string;
  general_instructions?: string;
  
  is_printed: boolean;
  printed_at?: string;
  is_signed: boolean;
  signed_at?: string;
  professional_signature?: string;
  
  is_dispensed: boolean;
  dispensed_at?: string;
  pharmacy_name?: string;
  pharmacist_name?: string;
  
  crm_number?: string;
  crm_state?: string;
  notes?: string;
  
  created_at: string;
  updated_at: string;
  
  items: PrescriptionItem[];
}

export interface PrescriptionCreate {
  patient_id: string;
  medical_record_id?: string;
  healthcare_professional_id: string;
  prescription_type?: PrescriptionType;
  prescription_date?: string;
  valid_until?: string;
  general_instructions?: string;
  crm_number?: string;
  crm_state?: string;
  notes?: string;
  items: Omit<PrescriptionItem, 'id'>[];
}

export interface PrescriptionSign {
  crm_number: string;
  crm_state: string;
  signature?: string;
}

export const prescriptionsService = {
  async list(params?: {
    skip?: number;
    limit?: number;
    patient_id?: string;
    professional_id?: string;
    prescription_type?: PrescriptionType;
    is_signed?: boolean;
    is_dispensed?: boolean;
    date_from?: string;
    date_to?: string;
  }): Promise<Prescription[]> {
    const queryParams = new URLSearchParams();
    if (params?.skip) queryParams.append('skip', params.skip.toString());
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.patient_id) queryParams.append('patient_id', params.patient_id);
    if (params?.professional_id) queryParams.append('professional_id', params.professional_id);
    if (params?.prescription_type) queryParams.append('prescription_type', params.prescription_type);
    if (params?.is_signed !== undefined) queryParams.append('is_signed', params.is_signed.toString());
    if (params?.is_dispensed !== undefined) queryParams.append('is_dispensed', params.is_dispensed.toString());
    if (params?.date_from) queryParams.append('date_from', params.date_from);
    if (params?.date_to) queryParams.append('date_to', params.date_to);

    const response = await api.get(`/api/v1/prescriptions/?${queryParams.toString()}`);
    return response.data;
  },

  async get(id: string): Promise<Prescription> {
    const response = await api.get(`/api/v1/prescriptions/${id}`);
    return response.data;
  },

  async create(data: PrescriptionCreate): Promise<Prescription> {
    const response = await api.post('/api/v1/prescriptions/', data);
    return response.data;
  },

  async update(id: string, data: Partial<PrescriptionCreate>): Promise<Prescription> {
    const response = await api.put(`/api/v1/prescriptions/${id}`, data);
    return response.data;
  },

  async delete(id: string): Promise<void> {
    await api.delete(`/api/v1/prescriptions/${id}`);
  },

  async sign(id: string, data: PrescriptionSign): Promise<Prescription> {
    const response = await api.post(`/api/v1/prescriptions/${id}/sign`, data);
    return response.data;
  },

  async print(id: string): Promise<Prescription> {
    const response = await api.post(`/api/v1/prescriptions/${id}/print`);
    return response.data;
  },
};
