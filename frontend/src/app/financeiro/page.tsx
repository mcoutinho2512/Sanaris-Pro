'use client';

import { useState, useEffect } from 'react';
import {
  DollarSign,
  TrendingUp,
  TrendingDown,
  Clock,
  CheckCircle,
  XCircle,
  Plus,
  Search,
  Filter,
  Eye,
  Edit,
  Trash2,
  Calendar
} from 'lucide-react';

interface FinancialSummary {
  total_receivable: string;
  total_received: string;
  total_pending: string;
  total_overdue: string;
  pending_count: number;
  overdue_count: number;
  paid_count: number;
}

interface AccountReceivable {
  id: string;
  invoice_number: string;
  description: string;
  patient_name: string;
  original_amount: string;
  total_amount: string;
  paid_amount: string;
  remaining_amount: string;
  due_date: string;
  payment_date: string | null;
  status: string;
}

export default function FinanceiroPage() {
  const [summary, setSummary] = useState<FinancialSummary | null>(null);
  const [receivables, setReceivables] = useState<AccountReceivable[]>([]);
  const [loading, setLoading] = useState(true);
  const [showNewModal, setShowNewModal] = useState(false);
  const [statusFilter, setStatusFilter] = useState<string>('');

  useEffect(() => {
    loadData();
  }, [statusFilter]);

  const loadData = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = { 'Authorization': `Bearer ${token}` };

      // Carregar resumo
      const summaryRes = await fetch('http://localhost:8888/api/v1/financial/summary', { headers });
      if (summaryRes.ok) {
        setSummary(await summaryRes.json());
      }

      // Carregar contas
      const url = statusFilter 
        ? `http://localhost:8888/api/v1/financial/receivables?status=${statusFilter}`
        : 'http://localhost:8888/api/v1/financial/receivables';
      
      const receivablesRes = await fetch(url, { headers });
      if (receivablesRes.ok) {
        setReceivables(await receivablesRes.json());
      }

    } catch (error) {
      console.error('Erro ao carregar dados:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: string | number) => {
    const num = typeof value === 'string' ? parseFloat(value) : value;
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(num);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR');
  };

  const getStatusBadge = (status: string) => {
    const statusMap: Record<string, { label: string; color: string }> = {
      'pending': { label: 'Pendente', color: 'bg-yellow-100 text-yellow-800' },
      'paid': { label: 'Pago', color: 'bg-green-100 text-green-800' },
      'overdue': { label: 'Vencido', color: 'bg-red-100 text-red-800' },
      'partially_paid': { label: 'Parcial', color: 'bg-blue-100 text-blue-800' },
      'cancelled': { label: 'Cancelado', color: 'bg-gray-100 text-gray-800' }
    };

    const statusInfo = statusMap[status] || { label: status, color: 'bg-gray-100 text-gray-800' };

    return (
      <span className={`px-2 py-1 rounded-full text-xs font-semibold ${statusInfo.color}`}>
        {statusInfo.label}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p>Carregando dados financeiros...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">💰 Gestão Financeira</h1>
        <button
          onClick={() => setShowNewModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <Plus className="w-5 h-5" />
          Nova Conta a Receber
        </button>
      </div>

      {/* Cards de Resumo */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-600 text-sm">Total a Receber</span>
            <DollarSign className="w-5 h-5 text-blue-600" />
          </div>
          <p className="text-2xl font-bold text-blue-600">
            {formatCurrency(summary?.total_receivable || 0)}
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-600 text-sm">Total Recebido</span>
            <CheckCircle className="w-5 h-5 text-green-600" />
          </div>
          <p className="text-2xl font-bold text-green-600">
            {formatCurrency(summary?.total_received || 0)}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            {summary?.paid_count || 0} contas pagas
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-600 text-sm">Pendente</span>
            <Clock className="w-5 h-5 text-yellow-600" />
          </div>
          <p className="text-2xl font-bold text-yellow-600">
            {formatCurrency(summary?.total_pending || 0)}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            {summary?.pending_count || 0} contas
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-600 text-sm">Vencido</span>
            <XCircle className="w-5 h-5 text-red-600" />
          </div>
          <p className="text-2xl font-bold text-red-600">
            {formatCurrency(summary?.total_overdue || 0)}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            {summary?.overdue_count || 0} contas
          </p>
        </div>
      </div>

      {/* Filtros */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="flex items-center gap-4">
          <Filter className="w-5 h-5 text-gray-600" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border rounded-lg"
          >
            <option value="">Todos os Status</option>
            <option value="pending">Pendente</option>
            <option value="paid">Pago</option>
            <option value="overdue">Vencido</option>
            <option value="partially_paid">Parcialmente Pago</option>
          </select>
        </div>
      </div>

      {/* Tabela de Contas */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Fatura</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Paciente</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Descrição</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Valor Total</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Pago</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Restante</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Vencimento</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Ações</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {receivables.length === 0 ? (
                <tr>
                  <td colSpan={9} className="px-6 py-8 text-center text-gray-500">
                    Nenhuma conta a receber encontrada
                  </td>
                </tr>
              ) : (
                receivables.map((account) => (
                  <tr key={account.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      {account.invoice_number}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {account.patient_name}
                    </td>
                    <td className="px-6 py-4 text-sm">
                      {account.description}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold">
                      {formatCurrency(account.total_amount)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600">
                      {formatCurrency(account.paid_amount)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-yellow-600">
                      {formatCurrency(account.remaining_amount)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {formatDate(account.due_date)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getStatusBadge(account.status)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <div className="flex items-center gap-2">
                        <button className="text-blue-600 hover:text-blue-800">
                          <Eye className="w-4 h-4" />
                        </button>
                        <button className="text-green-600 hover:text-green-800">
                          <DollarSign className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal Nova Conta */}
      {showNewModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">Nova Conta a Receber</h2>
            <p className="text-gray-600 mb-4">
              Funcionalidade de cadastro será implementada em breve.
            </p>
            <button
              onClick={() => setShowNewModal(false)}
              className="w-full px-4 py-2 bg-gray-200 rounded-lg hover:bg-gray-300"
            >
              Fechar
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
