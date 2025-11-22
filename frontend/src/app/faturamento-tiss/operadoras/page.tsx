"use client";

import { useState, useEffect } from "react";
import { tissOperadorasAPI } from "@/lib/api/tiss";
import { Plus, Edit, Trash2, Building2, X } from "lucide-react";
import { toast } from "react-hot-toast";

interface Operadora {
  id: string;
  registro_ans: string;
  razao_social: string;
  nome_fantasia?: string;
  cnpj: string;
  telefone?: string;
  email?: string;
  ativo: boolean;
}

export default function OperadorasPage() {
  const [operadoras, setOperadoras] = useState<Operadora[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    registro_ans: "",
    razao_social: "",
    nome_fantasia: "",
    cnpj: "",
    telefone: "",
    email: "",
    ativo: true,
  });

  useEffect(() => {
    loadOperadoras();
  }, []);

  const loadOperadoras = async () => {
    try {
      const response = await tissOperadorasAPI.list();
      setOperadoras(response.data);
    } catch (error) {
      toast.error("Erro ao carregar operadoras");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      if (editingId) {
        await tissOperadorasAPI.update(editingId, formData);
        toast.success("Operadora atualizada com sucesso!");
      } else {
        await tissOperadorasAPI.create(formData);
        toast.success("Operadora cadastrada com sucesso!");
      }
      
      setShowModal(false);
      resetForm();
      loadOperadoras();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Erro ao salvar operadora");
    }
  };

  const handleEdit = (operadora: Operadora) => {
    setFormData({
      registro_ans: operadora.registro_ans,
      razao_social: operadora.razao_social,
      nome_fantasia: operadora.nome_fantasia || "",
      cnpj: operadora.cnpj,
      telefone: operadora.telefone || "",
      email: operadora.email || "",
      ativo: operadora.ativo,
    });
    setEditingId(operadora.id);
    setShowModal(true);
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Deseja realmente excluir esta operadora?")) return;
    
    try {
      await tissOperadorasAPI.delete(id);
      toast.success("Operadora excluída com sucesso!");
      loadOperadoras();
    } catch (error) {
      toast.error("Erro ao excluir operadora");
    }
  };

  const resetForm = () => {
    setFormData({
      registro_ans: "",
      razao_social: "",
      nome_fantasia: "",
      cnpj: "",
      telefone: "",
      email: "",
      ativo: true,
    });
    setEditingId(null);
  };

  const openNewModal = () => {
    resetForm();
    setShowModal(true);
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Operadoras</h1>
          <p className="text-gray-600">Cadastro de operadoras de planos de saúde</p>
        </div>
        <button
          onClick={openNewModal}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-blue-700"
        >
          <Plus className="w-5 h-5" />
          Nova Operadora
        </button>
      </div>

      {loading ? (
        <div className="text-center py-12">Carregando...</div>
      ) : operadoras.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <Building2 className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">Nenhuma operadora cadastrada</p>
          <button
            onClick={openNewModal}
            className="mt-4 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            Cadastrar primeira operadora
          </button>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Registro ANS
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Razão Social
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  CNPJ
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Status
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                  Ações
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {operadoras.map((op) => (
                <tr key={op.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {op.registro_ans}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {op.razao_social}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {op.cnpj}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-2 py-1 text-xs font-medium rounded-full ${
                        op.ativo ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
                      }`}
                    >
                      {op.ativo ? "Ativo" : "Inativo"}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                      onClick={() => handleEdit(op)}
                      className="text-blue-600 hover:text-blue-900 mr-3"
                    >
                      <Edit className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(op.id)}
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

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">
                {editingId ? "Editar Operadora" : "Nova Operadora"}
              </h2>
              <button onClick={() => setShowModal(false)}>
                <X className="w-6 h-6 text-gray-500 hover:text-gray-700" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Registro ANS *
                  </label>
                  <input
                    type="text"
                    required
                    maxLength={6}
                    value={formData.registro_ans}
                    onChange={(e) =>
                      setFormData({ ...formData, registro_ans: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="123456"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    CNPJ *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.cnpj}
                    onChange={(e) => setFormData({ ...formData, cnpj: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="00.000.000/0000-00"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Razão Social *
                </label>
                <input
                  type="text"
                  required
                  value={formData.razao_social}
                  onChange={(e) =>
                    setFormData({ ...formData, razao_social: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nome Fantasia
                </label>
                <input
                  type="text"
                  value={formData.nome_fantasia}
                  onChange={(e) =>
                    setFormData({ ...formData, nome_fantasia: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Telefone
                  </label>
                  <input
                    type="text"
                    value={formData.telefone}
                    onChange={(e) =>
                      setFormData({ ...formData, telefone: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="(11) 98765-4321"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    E-mail
                  </label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="contato@operadora.com.br"
                  />
                </div>
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.ativo}
                  onChange={(e) => setFormData({ ...formData, ativo: e.target.checked })}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <label className="ml-2 text-sm text-gray-700">Operadora ativa</label>
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
                  {editingId ? "Atualizar" : "Cadastrar"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
