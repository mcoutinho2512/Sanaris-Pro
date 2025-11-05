'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { financialService } from '@/services/financial.service';
import type { FinancialSummary } from '@/types/financial';

export function DashboardPage() {
  const [data, setData] = useState<FinancialSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const dashboard = await financialService.getDashboard();
      setData(dashboard);
    } catch (error) {
      console.error('Erro ao carregar dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: any): string => {
    const num = typeof value === 'string' ? parseFloat(value) : value;
    return (num || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <p className="ml-4 text-gray-600">Carregando dashboard...</p>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Dashboard Financeiro</h1>

      {/* Cards Resumo */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        {/* Saldo Atual */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-gray-500 text-sm font-medium">Saldo Atual</h3>
          <p className="text-3xl font-bold text-blue-600 mt-2">
            R$ {formatCurrency(data?.current_balance)}
          </p>
        </div>

        {/* Receitas */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-gray-500 text-sm font-medium">Receitas</h3>
          <p className="text-3xl font-bold text-green-600 mt-2">
            R$ {formatCurrency(data?.total_revenue)}
          </p>
        </div>

        {/* Despesas */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-gray-500 text-sm font-medium">Despesas</h3>
          <p className="text-3xl font-bold text-red-600 mt-2">
            R$ {formatCurrency(data?.total_expenses)}
          </p>
        </div>
      </div>

      {/* Contas Pendentes */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Contas a Receber</h3>
          <p className="text-2xl font-bold text-green-600">
            R$ {formatCurrency(data?.pending_receivables)}
          </p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Contas a Pagar</h3>
          <p className="text-2xl font-bold text-red-600">
            R$ {formatCurrency(data?.pending_payables)}
          </p>
        </div>
      </div>

      {/* Ações Rápidas */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Ações Rápidas</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button 
            onClick={() => router.push('/financeiro')}
            className="p-4 border-2 border-blue-200 rounded-lg hover:bg-blue-50 transition"
          >
            <p className="font-semibold">Nova Receita</p>
          </button>
          <button 
            onClick={() => router.push('/financeiro')}
            className="p-4 border-2 border-red-200 rounded-lg hover:bg-red-50 transition"
          >
            <p className="font-semibold">Nova Despesa</p>
          </button>
          <button 
            onClick={() => router.push('/pacientes')}
            className="p-4 border-2 border-green-200 rounded-lg hover:bg-green-50 transition"
          >
            <p className="font-semibold">Novo Paciente</p>
          </button>
          <button 
            onClick={() => router.push('/agenda')}
            className="p-4 border-2 border-purple-200 rounded-lg hover:bg-purple-50 transition"
          >
            <p className="font-semibold">Agendar</p>
          </button>
        </div>
      </div>
    </div>
  );
}
