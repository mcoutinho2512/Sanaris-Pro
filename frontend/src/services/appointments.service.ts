import { api } from '@/lib/api';

export enum AppointmentStatus {
  SCHEDULED = 'scheduled',
  CONFIRMED = 'confirmed',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled',
  NO_SHOW = 'no_show',
}

export enum AppointmentType {
  FIRST_TIME = 'first_time',
  RETURN = 'return',
  EMERGENCY = 'emergency',
  TELEMEDICINE = 'telemedicine',
}

export enum ConfirmationMethod {
  WHATSAPP = 'whatsapp',
  EMAIL = 'email',
  SMS = 'sms',
  PHONE = 'phone',
  NONE = 'none',
}

export interface Appointment {
  id: string;
  patient_id: string;
  healthcare_professional_id: string;
  scheduled_date: string;
  duration_minutes: number;
  appointment_type: AppointmentType;
  status: AppointmentStatus;
  reason?: string;
  notes?: string;
  price?: number;
  paid?: boolean;
  payment_method?: string;
  confirmation_sent: boolean;
  confirmation_sent_at?: string;
  confirmation_method: ConfirmationMethod;
  confirmed_at?: string;
  confirmed_by?: string;
  checked_in_at?: string;
  started_at?: string;
  completed_at?: string;
  cancellation_reason?: string;
}

export interface AppointmentCreate {
  patient_id: string;
  healthcare_professional_id: string;
  scheduled_date: string;
  duration_minutes?: number;
  appointment_type?: AppointmentType;
  reason?: string;
  notes?: string;
  price?: number;
}

export interface AppointmentUpdate {
  patient_id?: string;
  healthcare_professional_id?: string;
  scheduled_date?: string;
  duration_minutes?: number;
  appointment_type?: AppointmentType;
  status?: AppointmentStatus;
  reason?: string;
  notes?: string;
  price?: number;
  paid?: boolean;
  payment_method?: string;
}

export const appointmentsService = {
  async list(params?: {
    skip?: number;
    limit?: number;
    status_filter?: AppointmentStatus;
    professional_id?: string;
    patient_id?: string;
    date_from?: string;
    date_to?: string;
  }): Promise<Appointment[]> {
    const queryParams = new URLSearchParams();
    if (params?.skip) queryParams.append('skip', params.skip.toString());
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.status_filter) queryParams.append('status_filter', params.status_filter);
    if (params?.professional_id) queryParams.append('professional_id', params.professional_id);
    if (params?.patient_id) queryParams.append('patient_id', params.patient_id);
    if (params?.date_from) queryParams.append('date_from', params.date_from);
    if (params?.date_to) queryParams.append('date_to', params.date_to);

    const response = await api.get(`/api/v1/appointments/?${queryParams.toString()}`);
    return response.data;
  },

  async get(id: string): Promise<Appointment> {
    const response = await api.get(`/api/v1/appointments/${id}`);
    return response.data;
  },

  async create(data: AppointmentCreate): Promise<Appointment> {
    const response = await api.post('/api/v1/appointments/', data);
    return response.data;
  },

  async update(id: string, data: AppointmentUpdate): Promise<Appointment> {
    const response = await api.put(`/api/v1/appointments/${id}`, data);
    return response.data;
  },

  async delete(id: string): Promise<void> {
    await api.delete(`/api/v1/appointments/${id}`);
  },

  async sendConfirmation(id: string, method: ConfirmationMethod): Promise<void> {
    await api.post(`/api/v1/appointments/${id}/send-confirmation?method=${method}`);
  },

  async confirm(id: string, method: ConfirmationMethod, confirmedBy: string = 'patient'): Promise<Appointment> {
    const response = await api.post(`/api/v1/appointments/${id}/confirm`, {
      confirmation_method: method,
      confirmed_by: confirmedBy,
    });
    return response.data;
  },

  async checkIn(id: string): Promise<Appointment> {
    const response = await api.post(`/api/v1/appointments/${id}/check-in`);
    return response.data;
  },

  async start(id: string): Promise<Appointment> {
    const response = await api.post(`/api/v1/appointments/${id}/start`);
    return response.data;
  },

  async complete(id: string): Promise<Appointment> {
    const response = await api.post(`/api/v1/appointments/${id}/complete`);
    return response.data;
  },

  async cancel(id: string, reason: string): Promise<Appointment> {
    const response = await api.post(`/api/v1/appointments/${id}/cancel`, {
      cancellation_reason: reason,
    });
    return response.data;
  },

  async markNoShow(id: string): Promise<Appointment> {
    const response = await api.post(`/api/v1/appointments/${id}/no-show`);
    return response.data;
  },
};
