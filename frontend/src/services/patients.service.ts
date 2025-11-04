import { api } from '@/lib/api';

export interface Patient {
  id: string;
  tenant_id: string;
  full_name: string;
  cpf: string | null;
  birth_date: string | null;
  phone: string | null;
  email: string | null;
  is_active: boolean;
  created_at: string;
}

export interface PatientCreate {
  tenant_id: string;
  full_name: string;
  cpf?: string;
  birth_date?: string;
  phone?: string;
  email?: string;
}

export interface PatientUpdate {
  full_name?: string;
  cpf?: string;
  birth_date?: string;
  phone?: string;
  email?: string;
  is_active?: boolean;
}

export const patientsService = {
  async list(search?: string): Promise<Patient[]> {
    const params = search ? `?search=${encodeURIComponent(search)}` : '';
    const response = await api.get(`/api/v1/patients/${params}`);
    return response.data;
  },

  async get(id: string): Promise<Patient> {
    const response = await api.get(`/api/v1/patients/${id}`);
    return response.data;
  },

  async create(data: PatientCreate): Promise<Patient> {
    const response = await api.post('/api/v1/patients/', data);
    return response.data;
  },

  async update(id: string, data: PatientUpdate): Promise<Patient> {
    const response = await api.put(`/api/v1/patients/${id}`, data);
    return response.data;
  },

  async delete(id: string): Promise<void> {
    await api.delete(`/api/v1/patients/${id}`);
  }
};
