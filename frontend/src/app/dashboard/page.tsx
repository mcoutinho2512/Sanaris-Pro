'use client';

import { useState, useEffect } from 'react';
import { 
  BarChart, 
  TrendingUp, 
  Users, 
  Calendar, 
  FileText,
  Activity,
  Clock
} from 'lucide-react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar, Doughnut } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

interface Stats {
  total_patients: number;
  total_appointments: number;
  appointments_today: number;
  pending_appointments: number;
  total_prescriptions: number;
  new_patients_month: number;
}

interface ChartData {
  labels: string[];
  data: number[];
}

export default function DashboardPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [appointmentsByMonth, setAppointmentsByMonth] = useState<ChartData | null>(null);
  const [appointmentsByStatus, setAppointmentsByStatus] = useState<ChartData | null>(null);
  const [patientsByGender, setPatientsByGender] = useState<ChartData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = { 'Authorization': `Bearer ${token}` };

      const [statsRes, monthRes, statusRes, genderRes] = await Promise.all([
        fetch('http://localhost:8888/api/v1/dashboard/stats', { headers }),
        fetch('http://localhost:8888/api/v1/dashboard/appointments/by-month', { headers }),
        fetch('http://localhost:8888/api/v1/dashboard/appointments/by-status', { headers }),
        fetch('http://localhost:8888/api/v1/dashboard/patients/by-gender', { headers })
      ]);

      if (statsRes.ok) setStats(await statsRes.json());
      if (monthRes.ok) setAppointmentsByMonth(await monthRes.json());
      if (statusRes.ok) setAppointmentsByStatus(await statusRes.json());
      if (genderRes.ok) setPatientsByGender(await genderRes.json());

    } catch (error) {
      console.error('Erro ao carregar dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p>Carregando dashboard...</p>
        </div>
      </div>
    );
  }

  const monthChartData = {
    labels: appointmentsByMonth?.labels || [],
    datasets: [{
      label: 'Consultas',
      data: appointmentsByMonth?.data || [],
      backgroundColor: 'rgba(59, 130, 246, 0.8)',
      borderColor: 'rgba(59, 130, 246, 1)',
      borderWidth: 2,
      borderRadius: 8,
    }]
  };

  const statusChartData = {
    labels: appointmentsByStatus?.labels || [],
    datasets: [{
      data: appointmentsByStatus?.data || [],
      backgroundColor: [
        'rgba(16, 185, 129, 0.8)',
        'rgba(59, 130, 246, 0.8)',
        'rgba(139, 92, 246, 0.8)',
        'rgba(239, 68, 68, 0.8)',
        'rgba(251, 146, 60, 0.8)',
      ],
      borderWidth: 2,
      borderColor: '#fff',
    }]
  };

  const genderChartData = {
    labels: patientsByGender?.labels || [],
    datasets: [{
      data: patientsByGender?.data || [],
      backgroundColor: [
        'rgba(59, 130, 246, 0.8)',
        'rgba(236, 72, 153, 0.8)',
        'rgba(168, 85, 247, 0.8)',
        'rgba(156, 163, 175, 0.8)',
      ],
      borderWidth: 2,
      borderColor: '#fff',
    }]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom' as const,
        labels: {
          padding: 15,
          font: { size: 12 }
        }
      }
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">📊 Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 mb-6">
        <StatCard
          icon={<Users className="w-6 h-6" />}
          label="Total de Pacientes"
          value={stats?.total_patients || 0}
          color="bg-blue-500"
        />
        <StatCard
          icon={<Calendar className="w-6 h-6" />}
          label="Total Consultas"
          value={stats?.total_appointments || 0}
          color="bg-green-500"
        />
        <StatCard
          icon={<Clock className="w-6 h-6" />}
          label="Consultas Hoje"
          value={stats?.appointments_today || 0}
          color="bg-purple-500"
        />
        <StatCard
          icon={<Activity className="w-6 h-6" />}
          label="Pendentes"
          value={stats?.pending_appointments || 0}
          color="bg-yellow-500"
        />
        <StatCard
          icon={<FileText className="w-6 h-6" />}
          label="Prescrições"
          value={stats?.total_prescriptions || 0}
          color="bg-indigo-500"
        />
        <StatCard
          icon={<TrendingUp className="w-6 h-6" />}
          label="Novos Este Mês"
          value={stats?.new_patients_month || 0}
          color="bg-pink-500"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">📈 Consultas por Mês</h2>
          <div className="h-64">
            <Bar data={monthChartData} options={chartOptions} />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">📊 Status das Consultas</h2>
          <div className="h-64">
            <Doughnut data={statusChartData} options={chartOptions} />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">👥 Distribuição por Gênero</h2>
          <div className="h-64">
            <Doughnut data={genderChartData} options={chartOptions} />
          </div>
        </div>

        <div className="bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg shadow p-6 text-white">
          <h2 className="text-lg font-semibold mb-4">⚡ Resumo Rápido</h2>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span>Consultas Pendentes:</span>
              <span className="font-bold text-2xl">{stats?.pending_appointments || 0}</span>
            </div>
            <div className="flex justify-between items-center">
              <span>Consultas Hoje:</span>
              <span className="font-bold text-2xl">{stats?.appointments_today || 0}</span>
            </div>
            <div className="border-t border-white/20 pt-3 mt-3">
              <p className="text-sm opacity-90">
                Sistema com {stats?.total_patients || 0} pacientes ativos e{' '}
                {stats?.total_prescriptions || 0} prescrições emitidas.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

interface StatCardProps {
  icon: React.ReactNode;
  label: string;
  value: number;
  color: string;
}

function StatCard({ icon, label, value, color }: StatCardProps) {
  return (
    <div className="bg-white rounded-lg shadow p-4 hover:shadow-lg transition-shadow">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-600 mb-1">{label}</p>
          <p className="text-2xl font-bold">{value}</p>
        </div>
        <div className={`${color} text-white p-3 rounded-lg`}>
          {icon}
        </div>
      </div>
    </div>
  );
}
