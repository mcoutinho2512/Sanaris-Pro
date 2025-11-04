export interface Patient {
  id: string;
  full_name: string;
  cpf: string;
  phone: string;
  email?: string;
  birth_date: string;
  created_at: string;
}

export interface Appointment {
  id: string;
  patient_id: string;
  healthcare_professional_id: string;
  appointment_date: string;
  status: string;
  notes?: string;
}

export interface FinancialSummary {
  current_balance: number;
  today_income: number;
  today_expense: number;
  today_balance: number;
  month_income: number;
  month_expense: number;
  month_balance: number;
  pending_receivables: number;
  pending_payables: number;
  projected_balance: number;
}
