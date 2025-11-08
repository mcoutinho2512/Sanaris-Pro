'use client';

import { useEffect, useState } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#FF6B9D'];

export default function DashboardPage() {
  const [overview, setOverview] = useState<any>(null);
  const [monthData, setMonthData] = useState<any[]>([]);
  const [statusData, setStatusData] = useState<any[]>([]);
  const [activityData, setActivityData] = useState<any[]>([]);

  useEffect(() => {
    fetch('http://localhost:8888/api/v1/statistics/overview')
      .then(res => res.json())
      .then(data => setOverview(data))
      .catch(err => console.error(err));

    fetch('http://localhost:8888/api/v1/statistics/patients-by-month')
      .then(res => res.json())
      .then(data => setMonthData(data))
      .catch(err => console.error(err));

    fetch('http://localhost:8888/api/v1/statistics/appointments-by-status')
      .then(res => res.json())
      .then(data => setStatusData(data))
      .catch(err => console.error(err));

    fetch('http://localhost:8888/api/v1/statistics/patients-activity')
      .then(res => res.json())
      .then(data => setActivityData(data))
      .catch(err => console.error(err));
  }, []);

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold text-gray-800">📊 Dashboard Analítico</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg shadow-lg p-6 text-white">
          <p className="text-sm opacity-90">Total de Pacientes</p>
          <p className="text-4xl font-bold mt-2">{overview?.metricas?.total_pacientes || 0}</p>
          <p className="text-xs mt-1 opacity-75">+{overview?.metricas?.pacientes_periodo || 0} no período</p>
        </div>

        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg shadow-lg p-6 text-white">
          <p className="text-sm opacity-90">Consultas Previstas</p>
          <p className="text-4xl font-bold mt-2">{overview?.metricas?.consultas_previstas || 0}</p>
          <p className="text-xs mt-1 opacity-75">{overview?.metricas?.consultas_realizadas || 0} realizadas</p>
        </div>

        <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg shadow-lg p-6 text-white">
          <p className="text-sm opacity-90">Taxa de Realização</p>
          <p className="text-4xl font-bold mt-2">{overview?.metricas?.taxa_realizacao || 0}%</p>
        </div>

        <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-lg shadow-lg p-6 text-white">
          <p className="text-sm opacity-90">Total Prontuários</p>
          <p className="text-4xl font-bold mt-2">{overview?.metricas?.total_prontuarios || 0}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-lg font-bold text-gray-800 mb-4">📈 Novos Pacientes (Últimos 6 meses)</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={monthData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="period" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#0088FE" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-lg font-bold text-gray-800 mb-4">👥 Status dos Pacientes</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={activityData} dataKey="count" nameKey="status" cx="50%" cy="50%" outerRadius={100} label>
                {activityData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {statusData.length > 0 && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-lg font-bold text-gray-800 mb-4">📅 Status dos Agendamentos</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={statusData} dataKey="count" nameKey="status" cx="50%" cy="50%" outerRadius={100} label>
                {statusData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
