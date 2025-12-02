'use client';

import { useState, useEffect } from 'react';
import { Users, Calendar, FileText, Activity } from 'lucide-react';

export default function DashboardPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        setError('Token não encontrado. Faça login novamente.');
        setLoading(false);
        return;
      }

      const response = await fetch('/api/v1/statistics/dashboard-admin', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const dashboardData = await response.json();
        setData(dashboardData);
        setError('');
      } else {
        setError(`Erro ${response.status}: ${await response.text()}`);
      }
    } catch (err: any) {
      setError(`Erro: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Tradução de status
  const translateStatus = (status: string): string => {
    const translations: Record<string, string> = {
      'scheduled': 'Agendada',
      'confirmed': 'Confirmada',
      'completed': 'Concluída',
      'cancelled': 'Cancelada',
      'no_show': 'Não Compareceu',
      'in_progress': 'Em Andamento',
      'waitlist': 'Lista de Espera'
    };
    return translations[status] || status;
  };

  if (loading) {
    return (
      <div className="p-6">
        <p>Carregando dashboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <p className="text-red-600">{error}</p>
        <button 
          onClick={loadDashboard}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded"
        >
          Tentar novamente
        </button>
      </div>
    );
  }

  if (!data) {
    return <div className="p-6">Sem dados</div>;
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <h1 className="text-3xl font-bold mb-8">Dashboard Analítico</h1>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-blue-600 text-white rounded-lg p-6">
          <Users className="w-8 h-8 mb-4" />
          <h3 className="text-sm mb-2">Pacientes</h3>
          <p className="text-4xl font-bold">{data.patients.total}</p>
        </div>

        <div className="bg-green-600 text-white rounded-lg p-6">
          <Calendar className="w-8 h-8 mb-4" />
          <h3 className="text-sm mb-2">Consultas</h3>
          <p className="text-4xl font-bold">{data.appointments.total}</p>
          <p className="text-sm mt-2">{data.appointments.today} hoje</p>
        </div>

        <div className="bg-purple-600 text-white rounded-lg p-6">
          <FileText className="w-8 h-8 mb-4" />
          <h3 className="text-sm mb-2">Prontuários</h3>
          <p className="text-4xl font-bold">{data.medical_records.total}</p>
        </div>

        <div className="bg-orange-600 text-white rounded-lg p-6">
          <Activity className="w-8 h-8 mb-4" />
          <h3 className="text-sm mb-2">Taxa Comparecimento</h3>
          <p className="text-4xl font-bold">{data.appointments.attendance_rate}%</p>
        </div>
      </div>

      <div className="mt-8 bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-bold mb-4">Consultas por Status</h2>
        <div className="space-y-2">
          {Object.entries(data.appointments.by_status).map(([status, count]: [string, any]) => (
            <div key={status} className="flex justify-between p-3 bg-gray-50 rounded">
              <span className="font-medium">{translateStatus(status)}</span>
              <span className="font-bold">{count}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
