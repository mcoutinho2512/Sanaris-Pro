'use client';

import { useEffect, useState } from 'react';
import { Chart as ChartJS, ArcElement, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';
import { Pie, Bar } from 'react-chartjs-2';
import { FileText, TrendingUp, DollarSign, FileCheck } from 'lucide-react';

ChartJS.register(ArcElement, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

interface RelatorioData {
  resumo: {
    total_lotes: number;
    total_guias: number;
    valor_total: number;
  };
  por_operadora: Array<{
    nome: string;
    quantidade_lotes: number;
    quantidade_guias: number;
    valor_total: number;
  }>;
  por_status: Array<{
    status: string;
    quantidade: number;
    valor: number;
  }>;
}

export default function RelatoriosTISSPage() {
  const [data, setData] = useState<RelatorioData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRelatorios();
  }, []);

  const loadRelatorios = async () => {
    try {
      const response = await fetch('http://localhost:8888/api/v1/tiss-xml/relatorios/dashboard');
      const result = await response.json();
      setData(result);
    } catch (error) {
      console.error('Erro ao carregar relatórios:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Carregando relatórios...</p>
        </div>
      </div>
    );
  }

  if (!data) return <div>Erro ao carregar dados</div>;

  const operadorasData = {
    labels: data.por_operadora.map(op => op.nome),
    datasets: [{
      label: 'Valor Total (R$)',
      data: data.por_operadora.map(op => op.valor_total),
      backgroundColor: [
        'rgba(255, 99, 132, 0.7)',
        'rgba(54, 162, 235, 0.7)',
        'rgba(255, 206, 86, 0.7)',
        'rgba(75, 192, 192, 0.7)',
        'rgba(153, 102, 255, 0.7)',
      ],
    }]
  };

  const statusData = {
    labels: data.por_status.map(s => s.status),
    datasets: [{
      label: 'Quantidade de Lotes',
      data: data.por_status.map(s => s.quantidade),
      backgroundColor: 'rgba(54, 162, 235, 0.7)',
    }]
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Relatórios de Faturamento TISS</h1>
          <p className="text-gray-600 mt-2">Análise completa do faturamento</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm font-medium">Total de Lotes</p>
                <p className="text-3xl font-bold text-blue-600 mt-2">{data.resumo.total_lotes}</p>
              </div>
              <FileText className="w-12 h-12 text-blue-600 opacity-20" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm font-medium">Total de Guias</p>
                <p className="text-3xl font-bold text-green-600 mt-2">{data.resumo.total_guias}</p>
              </div>
              <FileCheck className="w-12 h-12 text-green-600 opacity-20" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm font-medium">Valor Total</p>
                <p className="text-3xl font-bold text-purple-600 mt-2">
                  {new Intl.NumberFormat('pt-BR', {
                    style: 'currency',
                    currency: 'BRL'
                  }).format(data.resumo.valor_total)}
                </p>
              </div>
              <DollarSign className="w-12 h-12 text-purple-600 opacity-20" />
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Faturamento por Operadora</h2>
            <div className="h-80">
              <Pie data={operadorasData} options={{ maintainAspectRatio: false }} />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Lotes por Status</h2>
            <div className="h-80">
              <Bar 
                data={statusData} 
                options={{ 
                  maintainAspectRatio: false,
                  scales: {
                    y: {
                      beginAtZero: true
                    }
                  }
                }} 
              />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6 mt-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Detalhamento por Operadora</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Operadora</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Lotes</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Guias</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Valor Total</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {data.por_operadora.map((op, idx) => (
                  <tr key={idx}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{op.nome}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{op.quantidade_lotes}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{op.quantidade_guias}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600 font-semibold">
                      {new Intl.NumberFormat('pt-BR', {
                        style: 'currency',
                        currency: 'BRL'
                      }).format(op.valor_total)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
