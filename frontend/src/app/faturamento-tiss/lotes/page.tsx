"use client";

import { useState, useEffect } from "react";
import { tissLotesAPI, tissOperadorasAPI } from "@/lib/api/tiss";
import { Plus, Edit, Trash2, Package, Lock } from "lucide-react";
import XMLGenerator from "@/components/tiss/XMLGenerator";
import { toast } from "react-hot-toast";

interface Lote {
  id: string;
  numero_lote: string;
  operadora_id: string;
  competencia: string;
  status: string;
  quantidade_guias: number;
  valor_total_informado: number;
  valor_total_processado?: number;
  data_envio?: string;
  data_processamento?: string;
}

interface Operadora {
  id: string;
  registro_ans: string;
  razao_social: string;
}

export default function LotesPage() {
  const [lotes, setLotes] = useState<Lote[]>([]);
  const [operadoras, setOperadoras] = useState<Operadora[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    operadora_id: "",
    competencia: "",
    observacoes: "",
  });

  useEffect(() => {
    loadLotes();
    loadOperadoras();
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

  const loadOperadoras = async () => {
    try {
      const response = await tissOperadorasAPI.list();
      setOperadoras(response.data);
    } catch (error) {
      console.error("Erro ao carregar operadoras");
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      // Converter competência de YYYY-MM para MM/YYYY
      const [ano, mes] = formData.competencia.split('-');
      const competenciaFormatada = `${mes}/${ano}`;
      
      const dataToSend = {
        ...formData,
        competencia: competenciaFormatada,
      };
      
      if (editingId) {
        await tissLotesAPI.update(editingId, dataToSend);
        toast.success("Lote atualizado com sucesso!");
      } else {
        await tissLotesAPI.create(dataToSend);
        toast.success("Lote criado com sucesso!");
      }

      setShowModal(false);
      resetForm();
      loadLotes();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Erro ao salvar lote");
    }
  };

  const handleEdit = (lote: Lote) => {
    // Converter competência de MM/YYYY para YYYY-MM para o input
    const [mes, ano] = lote.competencia.split('/');
    const competenciaInput = `${ano}-${mes}`;
    
    setFormData({
      operadora_id: lote.operadora_id,
      competencia: competenciaInput,
      observacoes: "",
    });
    setEditingId(lote.id);
    setShowModal(true);
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Deseja realmente excluir este lote?")) return;

    try {
      await tissLotesAPI.delete(id);
      toast.success("Lote excluído com sucesso!");
      loadLotes();
    } catch (error) {
      toast.error("Erro ao excluir lote");
    }
  };

  const handleFechar = async (id: string) => {
    if (!confirm("Deseja realmente fechar este lote? Não será possível editá-lo depois.")) return;

    try {
      await tissLotesAPI.fechar(id);
      toast.success("Lote fechado com sucesso!");
      loadLotes();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Erro ao fechar lote");
    }
  };

  const resetForm = () => {
    setFormData({
      operadora_id: "",
      competencia: "",
      observacoes: "",
    });
    setEditingId(null);
  };

  const openNewModal = () => {
    resetForm();
    setShowModal(true);
  };

  const getStatusColor = (status: string) => {
    const colors: any = {
      rascunho: "bg-gray-100 text-gray-800",
      enviado: "bg-blue-100 text-blue-800",
      processado: "bg-green-100 text-green-800",
      pago: "bg-emerald-100 text-emerald-800",
      rejeitado: "bg-red-100 text-red-800",
    };
    return colors[status] || "bg-gray-100 text-gray-800";
  };

  const getStatusLabel = (status: string) => {
    const labels: any = {
      rascunho: "Rascunho",
      enviado: "Enviado",
      processado: "Processado",
      pago: "Pago",
      rejeitado: "Rejeitado",
    };
    return labels[status] || status;
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Lotes de Faturamento</h1>
          <p className="text-gray-600">Gestão de lotes TISS</p>
        </div>
        <button
          onClick={openNewModal}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-blue-700"
        >
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
          <button
            onClick={openNewModal}
            className="mt-4 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            Criar primeiro lote
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {lotes.map((lote) => (
            <div key={lote.id} className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{lote.numero_lote}</h3>
                  <p className="text-sm text-gray-500">Competência: {lote.competencia}</p>
                </div>
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(lote.status)}`}>
                  {getStatusLabel(lote.status)}
                </span>
              </div>

              <div className="space-y-2 text-sm mb-4">
                <div className="flex justify-between">
                  <span className="text-gray-600">Guias:</span>
                  <span className="font-medium">{lote.quantidade_guias}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Valor Total:</span>
                  <span className="font-medium">
                    {new Intl.NumberFormat("pt-BR", {
                      style: "currency",
                      currency: "BRL",
                    }).format(lote.valor_total_informado)}
                  </span>
                </div>
                {lote.valor_total_processado && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Valor Processado:</span>
                    <span className="font-medium text-green-600">
                      {new Intl.NumberFormat("pt-BR", {
                        style: "currency",
                        currency: "BRL",
                      }).format(lote.valor_total_processado)}
                    </span>
                  </div>
                )}
              </div>

              <div className="flex gap-2">
                {lote.status === "rascunho" && (
                  <>
                    <button
                      onClick={() => handleEdit(lote)}
                      className="flex-1 text-blue-600 hover:text-blue-900 text-sm flex items-center justify-center gap-1"
                    >
                      <Edit className="w-4 h-4" />
                      Editar
                    </button>
                    <button
                      onClick={() => handleFechar(lote.id)}
                      className="flex-1 text-green-600 hover:text-green-900 text-sm flex items-center justify-center gap-1"
                    >
                      <Lock className="w-4 h-4" />
                      Fechar
                    </button>
                  </>
                )}
                <button
                  onClick={() => handleDelete(lote.id)}
                  className="flex-1 text-red-600 hover:text-red-900 text-sm flex items-center justify-center gap-1"
                >
                  <Trash2 className="w-4 h-4" />
                  Excluir
                </button>
              </div>
              <div className="mt-4 pt-4 border-t border-gray-200">
              <XMLGenerator 
                loteId={lote.id} 
                numeroLote={lote.numero_lote}
                onSuccess={loadLotes}
              />
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-lg">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">
                {editingId ? "Editar Lote" : "Novo Lote"}
              </h2>
              <button onClick={() => setShowModal(false)}>
                <span className="text-2xl text-gray-500 hover:text-gray-700">×</span>
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Operadora *
                </label>
                <select
                  required
                  value={formData.operadora_id}
                  onChange={(e) =>
                    setFormData({ ...formData, operadora_id: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Selecione uma operadora</option>
                  {operadoras.map((op) => (
                    <option key={op.id} value={op.id}>
                      {op.registro_ans} - {op.razao_social}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Competência *
                </label>
                <input
                  type="month"
                  required
                  value={formData.competencia}
                  onChange={(e) =>
                    setFormData({ ...formData, competencia: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Observações
                </label>
                <textarea
                  rows={3}
                  value={formData.observacoes}
                  onChange={(e) =>
                    setFormData({ ...formData, observacoes: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="Observações sobre o lote..."
                />
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  {editingId ? "Atualizar" : "Criar Lote"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
