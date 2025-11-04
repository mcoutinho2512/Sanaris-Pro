import { api } from '@/lib/api';
import { FinancialSummary } from '@/types';

export const financialService = {
  getDashboard: async (): Promise<FinancialSummary> => {
    const response = await api.get('/api/v1/financial/cash-flow/dashboard');
    return response.data;
  },

  getDailyCashFlow: async (days: number = 7) => {
    const response = await api.get(`/api/v1/financial/cash-flow/daily?days=${days}`);
    return response.data;
  },

  getMonthlyCashFlow: async (months: number = 6) => {
    const response = await api.get(`/api/v1/financial/cash-flow/monthly?months=${months}`);
    return response.data;
  },
};
