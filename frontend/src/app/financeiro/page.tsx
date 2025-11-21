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
  Calendar,
  X
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

interface Patient {
  id: string;
  full_name: string;
}

export default function FinanceiroPage() {
  const [summary, setSummary] = useState<FinancialSummary | null>(null);
  const [receivables, setReceivables] = useState<AccountReceivable[]>([]);
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(true);
  const [showNewModal, setShowNewModal] = useState(false);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [saving, setSaving] = useState(false);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [selectedAccount, setSelectedAccount] = useState<AccountReceivable | null>(null);
  const [paymentAmount, setPaymentAmount] = useState('');

  // Form state
  const [formData, setFormData] = useState({
    patient_id: '',
    description: '',
    original_amount: '',
    discount_amount: '0',
    due_date: '',
    total_installments: '1',
    payment_method: '',
    notes: ''
  });

  useEffect(() => {
    loadData();
    loadPatients();
  }, [statusFilter]);

  const loadData = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = { 'Authorization': `Bearer ${token}` };

      const summaryRes = await fetch('http://localhost:8888/api/v1/financial/summary', { headers });
      if (summaryRes.ok) {
        setSummary(await summaryRes.json());
      }

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

  const loadPatients = async () => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch('http://localhost:8888/api/v1/patients/?limit=100', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setPatients(data);
      }
    } catch (error) {
      console.error('Erro ao carregar pacientes:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);

    try {
      const token = localStorage.getItem('token');
      
      // Validar patient_id
      if (!formData.patient_id) {
        alert('❌ Selecione um paciente!');
        setSaving(false);
        return;
      }

      const payload = {
        ...formData,
        original_amount: parseFloat(formData.original_amount),
        discount_amount: parseFloat(formData.discount_amount || '0'),
        total_installments: parseInt(formData.total_installments),
        due_date: new Date(formData.due_date).toISOString()
      };

      const res = await fetch('http://localhost:8888/api/v1/financial/receivables', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        alert('✅ Conta a receber criada com sucesso!');
        setShowNewModal(false);
        resetForm();
        loadData();
      } else {
        const error = await res.json();
        alert('❌ Erro: ' + (error.detail || 'Erro ao criar conta'));
      }
    } catch (error) {
      console.error('Erro:', error);
      alert('❌ Erro ao criar conta a receber');
    } finally {
      setSaving(false);
    }
  };

  const handleViewDetails = (account: AccountReceivable) => {
    setSelectedAccount(account);
    setShowDetailsModal(true);
  };

  const handleRegisterPayment = (account: AccountReceivable) => {
    setSelectedAccount(account);
    setPaymentAmount('');
    setShowPaymentModal(true);
  };

  const submitPayment = async () => {
    if (!selectedAccount || !paymentAmount) {
      alert('❌ Informe o valor do pagamento');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`http://localhost:8888/api/v1/financial/receivables/${selectedAccount.id}/pay`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          account_id: selectedAccount.id,
          amount: parseFloat(paymentAmount),
          payment_method: 'cash',
          payment_date: new Date().toISOString()
        })
      });

      if (res.ok) {
        alert('✅ Pagamento registrado com sucesso!');
        setShowPaymentModal(false);
        setSelectedAccount(null);
        loadData();
      } else {
        alert('❌ Erro ao registrar pagamento');
      }
    } catch (error) {
      console.error('Erro:', error);
      alert('❌ Erro ao registrar pagamento');
    }
  };

  const resetForm = () => {
    setFormData({
      patient_id: '',
      description: '',
      original_amount: '',
      discount_amount: '0',
      due_date: '',
      total_installments: '1',
      payment_method: '',
      notes: ''
    });
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
        <h1 className="text-2xl font-bold">�� Gestão Financeira</h1>
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
                        <button 
                          onClick={() => handleViewDetails(account)}
                          className="text-blue-600 hover:text-blue-800"
                          title="Ver detalhes"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        {account.status !== 'paid' && (
                          <button 
                            onClick={() => handleRegisterPayment(account)}
                            className="text-green-600 hover:text-green-800"
                            title="Registrar pagamento"
                          >
                            <DollarSign className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal Detalhes */}
      {showDetailsModal && selectedAccount && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-6 w-full max-w-lg">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">Detalhes da Conta</h2>
              <button onClick={() => setShowDetailsModal(false)} className="text-gray-500 hover:text-gray-700">
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Número da Fatura</p>
                  <p className="font-semibold">{selectedAccount.invoice_number}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Status</p>
                  {getStatusBadge(selectedAccount.status)}
                </div>
              </div>

              <div>
                <p className="text-sm text-gray-600">Paciente</p>
                <p className="font-semibold">{selectedAccount.patient_name}</p>
              </div>

              <div>
                <p className="text-sm text-gray-600">Descrição</p>
                <p>{selectedAccount.description}</p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Valor Total</p>
                  <p className="font-bold text-lg">{formatCurrency(selectedAccount.total_amount)}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Valor Pago</p>
                  <p className="font-bold text-lg text-green-600">{formatCurrency(selectedAccount.paid_amount)}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Valor Restante</p>
                  <p className="font-bold text-lg text-yellow-600">{formatCurrency(selectedAccount.remaining_amount)}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Vencimento</p>
                  <p className="font-semibold">{formatDate(selectedAccount.due_date)}</p>
                </div>
              </div>
            </div>

            <button
              onClick={() => setShowDetailsModal(false)}
              className="w-full mt-6 px-4 py-2 bg-gray-200 rounded-lg hover:bg-gray-300"
            >
              Fechar
            </button>
          </div>
        </div>
      )}

      {/* Modal Pagamento */}
      {showPaymentModal && selectedAccount && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">Registrar Pagamento</h2>
              <button onClick={() => setShowPaymentModal(false)} className="text-gray-500 hover:text-gray-700">
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-600">Fatura</p>
                <p className="font-semibold">{selectedAccount.invoice_number}</p>
              </div>

              <div>
                <p className="text-sm text-gray-600">Paciente</p>
                <p className="font-semibold">{selectedAccount.patient_name}</p>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="flex justify-between mb-2">
                  <span className="text-sm">Valor Total:</span>
                  <span className="font-bold">{formatCurrency(selectedAccount.total_amount)}</span>
                </div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm">Já Pago:</span>
                  <span className="font-bold text-green-600">{formatCurrency(selectedAccount.paid_amount)}</span>
                </div>
                <div className="flex justify-between border-t pt-2">
                  <span className="font-semibold">Restante:</span>
                  <span className="font-bold text-yellow-600">{formatCurrency(selectedAccount.remaining_amount)}</span>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Valor do Pagamento *</label>
                <input
                  type="number"
                  step="0.01"
                  value={paymentAmount}
                  onChange={(e) => setPaymentAmount(e.target.value)}
                  className="w-full px-4 py-2 border rounded-lg"
                  placeholder="0.00"
                  max={parseFloat(selectedAccount.remaining_amount)}
                />
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => setShowPaymentModal(false)}
                  className="flex-1 px-4 py-2 border rounded-lg hover:bg-gray-50"
                >
                  Cancelar
                </button>
                <button
                  onClick={submitPayment}
                  className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                >
                  Registrar Pagamento
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal Nova Conta */}
      {showNewModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-bold">Nova Conta a Receber</h2>
                <button
                  onClick={() => {
                    setShowNewModal(false);
                    resetForm();
                  }}
                  className="text-gray-500 hover:text-gray-700"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Paciente *</label>
                  <select
                    required
                    value={formData.patient_id}
                    onChange={(e) => setFormData({...formData, patient_id: e.target.value})}
                    className="w-full px-4 py-2 border rounded-lg"
                  >
                    <option value="">Selecione um paciente</option>
                    {patients.map(p => (
                      <option key={p.id} value={p.id}>{p.full_name}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Descrição *</label>
                  <input
                    type="text"
                    required
                    value={formData.description}
                    onChange={(e) => setFormData({...formData, description: e.target.value})}
                    className="w-full px-4 py-2 border rounded-lg"
                    placeholder="Ex: Consulta médica"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">Valor Original *</label>
                    <input
                      type="number"
                      step="0.01"
                      required
                      value={formData.original_amount}
                      onChange={(e) => setFormData({...formData, original_amount: e.target.value})}
                      className="w-full px-4 py-2 border rounded-lg"
                      placeholder="0.00"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">Desconto</label>
                    <input
                      type="number"
                      step="0.01"
                      value={formData.discount_amount}
                      onChange={(e) => setFormData({...formData, discount_amount: e.target.value})}
                      className="w-full px-4 py-2 border rounded-lg"
                      placeholder="0.00"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">Vencimento *</label>
                    <input
                      type="date"
                      required
                      value={formData.due_date}
                      onChange={(e) => setFormData({...formData, due_date: e.target.value})}
                      className="w-full px-4 py-2 border rounded-lg"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">Parcelas</label>
                    <input
                      type="number"
                      min="1"
                      max="12"
                      value={formData.total_installments}
                      onChange={(e) => setFormData({...formData, total_installments: e.target.value})}
                      className="w-full px-4 py-2 border rounded-lg"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Método de Pagamento</label>
                  <select
                    value={formData.payment_method}
                    onChange={(e) => setFormData({...formData, payment_method: e.target.value})}
                    className="w-full px-4 py-2 border rounded-lg"
                  >
                    <option value="">Selecione...</option>
                    <option value="cash">Dinheiro</option>
                    <option value="credit_card">Cartão de Crédito</option>
                    <option value="debit_card">Cartão de Débito</option>
                    <option value="pix">PIX</option>
                    <option value="bank_slip">Boleto</option>
                    <option value="transfer">Transferência</option>
                    <option value="insurance">Convênio</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Observações</label>
                  <textarea
                    value={formData.notes}
                    onChange={(e) => setFormData({...formData, notes: e.target.value})}
                    className="w-full px-4 py-2 border rounded-lg"
                    rows={3}
                    placeholder="Observações adicionais..."
                  />
                </div>

                <div className="flex gap-3">
                  <button
                    type="button"
                    onClick={() => {
                      setShowNewModal(false);
                      resetForm();
                    }}
                    className="flex-1 px-4 py-2 border rounded-lg hover:bg-gray-50"
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    disabled={saving}
                    className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                  >
                    {saving ? 'Salvando...' : 'Criar Conta'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
