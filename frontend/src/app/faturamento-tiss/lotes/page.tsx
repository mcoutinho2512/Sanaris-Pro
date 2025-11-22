"use client";

import { useState, useEffect } from "react";
import { tissLotesAPI } from "@/lib/api/tiss";
import { Plus, Package } from "lucide-react";
import { toast } from "react-hot-toast";

export default function LotesPage() {
  const [lotes, setLotes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadLotes();
  }, []);

  const loadLotes = async () => {
    try {
      const response = await tissLotesAPI.list();
      setLotes(response.data);
    } catch (error) {
      toast.error("Erro ao carregar lotes");
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    const colors: any = {
      rascunho: 'bg-gray-100 text-gray-800',
      enviado: 'bg-blue-100 text-blue-800',
      processado: 'bg-green-100 text-green-800',
      pago: 'bg-emerald-100 text-emerald-800',
      rejeitado: 'bg-red-100 text-red-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Lotes de Faturamento</h1>
          <p className="text-gray-600">Gestão de lotes TISS</p>
        </div>
        <button className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-blue-700">
          <Plus className="w-5 h-5" />
          Novo Lote
        </button>
      </div>

      {loading ? (
        <div className="text-center py-12">Carregando...</div>
      ) : lotes.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <Package className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">Nenhum lote cadastrado</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {lotes.map((lote: any) => (
            <div key={lote.id} className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{lote.numero_lote}</h3>
                  <p className="text-sm text-gray-500">Competência: {lote.competencia}</p>
                </div>
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(lote.status)}`}>
                  {lote.status}
                </span>
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Guias:</span>
                  <span className="font-medium">{lote.quantidade_guias}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Valor Total:</span>
                  <span className="font-medium">
                    {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })
                      .format(lote.valor_total_informado)}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
