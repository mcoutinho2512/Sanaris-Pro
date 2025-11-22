"use client";

import { useState, useEffect } from "react";
import { tissProcedimentosAPI, tissGuiasAPI, tissTabelasAPI } from "@/lib/api/tiss";
import { Plus, Edit, Trash2, Stethoscope } from "lucide-react";
import { toast } from "react-hot-toast";

interface Procedimento {
  id: string;
  guia_id: string;
  codigo_procedimento: string;
  descricao_procedimento: string;
  quantidade_executada: number;
  valor_unitario_informado: number;
  valor_total: number;
  data_realizacao: string;
  nome_profissional_executante?: string;
  conselho_profissional?: string;
  numero_conselho?: string;
  uf_conselho?: string;
  codigo_cbo?: string;
  grau_participacao?: string;
}

interface Guia {
  id: string;
  numero_guia_prestador: string;
  nome_beneficiario: string;
}

export default function ProcedimentosPage() {
  const [procedimentos, setProcedimentos] = useState<Procedimento[]>([]);
  const [guias, setGuias] = useState<Guia[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [selectedGuiaId, setSelectedGuiaId] = useState<string>("");
  const [formData, setFormData] = useState({
    guia_id: "",
    tabela: "22",
    codigo_procedimento: "",
    descricao_procedimento: "",
    quantidade_executada: "1",
    valor_unitario_informado: "",
    data_realizacao: "",
    nome_profissional_executante: "",
    conselho_profissional: "",
    numero_conselho: "",
    uf_conselho: "",
    codigo_cbo: "",
    grau_participacao: "00",
  });

  useEffect(() => {
    loadGuias();
  }, []);

  useEffect(() => {
    if (selectedGuiaId) {
      loadProcedimentos(selectedGuiaId);
    }
  }, [selectedGuiaId]);

  const loadGuias = async () => {
    try {
      const response = await tissGuiasAPI.list();
      setGuias(response.data);
      if (response.data.length > 0) {
        setSelectedGuiaId(response.data[0].id);
      }
    } catch (error) {
      toast.error("Erro ao carregar guias");
    } finally {
      setLoading(false);
    }
  };

  const loadProcedimentos = async (guiaId: string) => {
    try {
      const response = await tissProcedimentosAPI.listByGuia(guiaId);
      setProcedimentos(response.data);
    } catch (error) {
      toast.error("Erro ao carregar procedimentos");
    }
  };


  const buscarTUSS = async (codigo: string) => {
    if (!codigo || codigo.length < 6) return;
    
    try {
      const response = await tissTabelasAPI.buscarPorCodigo(codigo, "TUSS");
      if (response.data) {
        setFormData(prev => ({
          ...prev,
          descricao_procedimento: response.data.descricao,
          valor_unitario_informado: response.data.valor_referencia?.toString() || prev.valor_unitario_informado,
        }));
        toast.success("Procedimento encontrado na TUSS!");
      }
    } catch (error) {
      console.log("Procedimento não encontrado na TUSS");
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const data = {
      ...formData,
      quantidade_executada: parseInt(formData.quantidade_executada),
      valor_unitario_informado: parseFloat(formData.valor_unitario_informado),
    };

    try {
      if (editingId) {
        await tissProcedimentosAPI.update(editingId, data);
        toast.success("Procedimento atualizado com sucesso!");
      } else {
        await tissProcedimentosAPI.create(data);
        toast.success("Procedimento criado com sucesso!");
      }

      setShowModal(false);
      resetForm();
      if (selectedGuiaId) {
        loadProcedimentos(selectedGuiaId);
      }
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Erro ao salvar procedimento");
    }
  };

  const handleEdit = (proc: Procedimento) => {
    setFormData({
      guia_id: proc.guia_id,
      tabela: "22",
      codigo_procedimento: proc.codigo_procedimento,
      descricao_procedimento: proc.descricao_procedimento,
      quantidade_executada: proc.quantidade_executada.toString(),
      valor_unitario_informado: proc.valor_unitario_informado?.toString() || "",
      data_realizacao: proc.data_realizacao?.split("T")[0] || "",
      nome_profissional_executante: proc.nome_profissional_executante || "",
      conselho_profissional: proc.conselho_profissional || "",
      numero_conselho: proc.numero_conselho || "",
      uf_conselho: proc.uf_conselho || "",
      codigo_cbo: proc.codigo_cbo || "",
      grau_participacao: proc.grau_participacao || "00",
    });
    setEditingId(proc.id);
    setShowModal(true);
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Deseja realmente excluir este procedimento?")) return;

    try {
      await tissProcedimentosAPI.delete(id);
      toast.success("Procedimento excluído com sucesso!");
      if (selectedGuiaId) {
        loadProcedimentos(selectedGuiaId);
      }
    } catch (error) {
      toast.error("Erro ao excluir procedimento");
    }
  };

  const resetForm = () => {
    setFormData({
      guia_id: selectedGuiaId,
      tabela: "22",
      codigo_procedimento: "",
      descricao_procedimento: "",
      quantidade_executada: "1",
      valor_unitario_informado: "",
      data_realizacao: "",
      nome_profissional_executante: "",
      conselho_profissional: "",
      numero_conselho: "",
      uf_conselho: "",
      codigo_cbo: "",
      grau_participacao: "00",
    });
    setEditingId(null);
  };

  const openNewModal = async () => {
    resetForm();
    
    // Buscar dados completos da guia para copiar informações
    try {
      const guiaResponse = await tissGuiasAPI.get(selectedGuiaId);
      const guia = guiaResponse.data;
      
      setFormData(prev => ({
        ...prev,
        guia_id: selectedGuiaId,
        nome_profissional_executante: guia.nome_profissional || '',
        conselho_profissional: guia.sigla_conselho || '',
        numero_conselho: guia.numero_conselho_profissional || '',
        uf_conselho: guia.uf_conselho || '',
        codigo_cbo: guia.codigo_cbo || '',
        data_realizacao: guia.data_atendimento || new Date().toISOString().split('T')[0],
        grau_participacao: '00',
      }));
    } catch (error) {
      // Se não conseguir buscar, só seta o guia_id
      setFormData(prev => ({ 
        ...prev, 
        guia_id: selectedGuiaId,
        data_realizacao: new Date().toISOString().split('T')[0],
        grau_participacao: '00',
      }));
    }
    
    setShowModal(true);
  };

  const selectedGuia = guias.find((g) => g.id === selectedGuiaId);

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Procedimentos</h1>
          <p className="text-gray-600">Procedimentos executados nas guias</p>
        </div>
        <button
          onClick={openNewModal}
          disabled={!selectedGuiaId}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-blue-700 disabled:bg-gray-400"
        >
          <Plus className="w-5 h-5" />
          Novo Procedimento
        </button>
      </div>

      {loading ? (
        <div className="text-center py-12">Carregando...</div>
      ) : guias.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <Stethoscope className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 mb-2">Nenhuma guia cadastrada</p>
          <p className="text-sm text-gray-500">
            Cadastre guias primeiro para poder adicionar procedimentos.
          </p>
        </div>
      ) : (
        <>
          {/* Seletor de Guia */}
          <div className="bg-white rounded-lg shadow p-4 mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Selecionar Guia
            </label>
            <select
              value={selectedGuiaId}
              onChange={(e) => setSelectedGuiaId(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              {guias.map((guia) => (
                <option key={guia.id} value={guia.id}>
                  {guia.numero_guia_prestador} - {guia.nome_beneficiario}
                </option>
              ))}
            </select>
          </div>

          {procedimentos.length === 0 ? (
            <div className="text-center py-12 bg-gray-50 rounded-lg">
              <Stethoscope className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 mb-2">Nenhum procedimento nesta guia</p>
              {selectedGuia && (
                <p className="text-sm text-gray-500 mb-4">
                  Guia: {selectedGuia.numero_guia_prestador}
                </p>
              )}
              <button
                onClick={openNewModal}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
              >
                Adicionar primeiro procedimento
              </button>
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Código
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Descrição
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Qtd
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Valor Unit.
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Valor Total
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Data
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                      Ações
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {procedimentos.map((proc) => (
                    <tr key={proc.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {proc.codigo_procedimento}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900">
                        {proc.descricao_procedimento}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {proc.quantidade_executada}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {new Intl.NumberFormat("pt-BR", {
                          style: "currency",
                          currency: "BRL",
                        }).format(proc.valor_unitario_informado || 0)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {new Intl.NumberFormat("pt-BR", {
                          style: "currency",
                          currency: "BRL",
                        }).format(proc.valor_total || (proc.quantidade_executada * (proc.valor_unitario_informado || 0)))}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(proc.data_realizacao).toLocaleDateString("pt-BR")}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button
                          onClick={() => handleEdit(proc)}
                          className="text-blue-600 hover:text-blue-900 mr-3"
                        >
                          <Edit className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(proc.id)}
                          className="text-red-600 hover:text-red-900"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">
                {editingId ? "Editar Procedimento" : "Novo Procedimento"}
              </h2>
              <button onClick={() => setShowModal(false)}>
                <span className="text-2xl text-gray-500 hover:text-gray-700">×</span>
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Código TUSS *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.codigo_procedimento}
                    onChange={(e) =>
                      setFormData({ ...formData, codigo_procedimento: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="10101012"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Data de Realização *
                  </label>
                  <input
                    type="date"
                    required
                    value={formData.data_realizacao}
                    onChange={(e) =>
                      setFormData({ ...formData, data_realizacao: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Descrição *
                </label>
                <input
                  type="text"
                  required
                  value={formData.descricao_procedimento}
                  onChange={(e) =>
                    setFormData({ ...formData, descricao_procedimento: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="Consulta em consultório"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Quantidade *
                  </label>
                  <input
                    type="number"
                    required
                    min="1"
                    value={formData.quantidade_executada}
                    onChange={(e) =>
                      setFormData({ ...formData, quantidade_executada: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Valor Unitário *
                  </label>
                  <input
                    type="number"
                    required
                    step="0.01"
                    min="0"
                    value={formData.valor_unitario_informado}
                    onChange={(e) =>
                      setFormData({ ...formData, valor_unitario_informado: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="0.00"
                  />
                </div>
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
                  {editingId ? "Atualizar" : "Criar Procedimento"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
