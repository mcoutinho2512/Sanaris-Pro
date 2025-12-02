"use client";

import { useState, useEffect } from "react";
import { tissTabelasAPI } from "@/lib/api/tiss";
import { Plus, Edit, Trash2, Database, Search, Download } from "lucide-react";
import { toast } from "react-hot-toast";

interface Tabela {
  id: string;
  codigo: string;
  descricao: string;
  tipo_tabela: string;
  valor_referencia?: number;
  vigencia_inicio?: string;
  vigencia_fim?: string;
  ativo: boolean;
}

export default function TabelasPage() {
  const [tabelas, setTabelas] = useState<Tabela[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [searchCodigo, setSearchCodigo] = useState("");
  const [filterTipo, setFilterTipo] = useState("");
  const [formData, setFormData] = useState({
    codigo: "",
    descricao: "",
    tipo_tabela: "TUSS",
    valor_referencia: "",
    vigencia_inicio: "",
    vigencia_fim: "",
    ativo: true,
  });

  const tiposTabela = ["TUSS", "CBHPM", "SIMPRO", "BRASINDICE", "AMB"];

  useEffect(() => {
    loadTabelas();
  }, []);


  const handleImportCSV = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const response = await fetch('/api/v1/tiss/tabelas/importar-csv', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: formData,
      });
      
      const data = await response.json();
      toast.success(`${data.total_importados} procedimentos importados!`);
      loadTabelas();
    } catch (error) {
      toast.error('Erro ao importar CSV');
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  const loadTabelas = async () => {
    try {
      const params: any = {};
      if (filterTipo) params.tipo_tabela = filterTipo;
      
      const response = await tissTabelasAPI.list(params);
      setTabelas(response.data);
    } catch (error) {
      toast.error("Erro ao carregar tabelas");
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchCodigo.trim()) {
      toast.error("Digite um código para buscar");
      return;
    }

    try {
      const response = await tissTabelasAPI.buscarPorCodigo(searchCodigo, filterTipo);
      if (response.data) {
        setTabelas([response.data]);
        toast.success("Procedimento encontrado!");
      }
    } catch (error) {
      toast.error("Procedimento não encontrado");
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const data = {
      ...formData,
      valor_referencia: formData.valor_referencia ? parseFloat(formData.valor_referencia) : undefined,
      vigencia_inicio: formData.vigencia_inicio || undefined,
      vigencia_fim: formData.vigencia_fim || undefined,
    };

    try {
      if (editingId) {
        await tissTabelasAPI.update(editingId, data);
        toast.success("Tabela atualizada com sucesso!");
      } else {
        await tissTabelasAPI.create(data);
        toast.success("Tabela cadastrada com sucesso!");
      }

      setShowModal(false);
      resetForm();
      loadTabelas();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Erro ao salvar tabela");
    }
  };

  const handleEdit = (tabela: Tabela) => {
    setFormData({
      codigo: tabela.codigo,
      descricao: tabela.descricao,
      tipo_tabela: tabela.tipo_tabela,
      valor_referencia: tabela.valor_referencia?.toString() || "",
      vigencia_inicio: tabela.vigencia_inicio || "",
      vigencia_fim: tabela.vigencia_fim || "",
      ativo: tabela.ativo,
    });
    setEditingId(tabela.id);
    setShowModal(true);
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Deseja realmente excluir esta tabela?")) return;

    try {
      await tissTabelasAPI.delete(id);
      toast.success("Tabela excluída com sucesso!");
      loadTabelas();
    } catch (error) {
      toast.error("Erro ao excluir tabela");
    }
  };

  const handleImportarTUSS = async () => {
    try {
      await tissTabelasAPI.importarTuss();
      toast.success("Importação TUSS iniciada!");
      loadTabelas();
    } catch (error) {
      toast.error("Erro ao importar TUSS");
    }
  };

  const resetForm = () => {
    setFormData({
      codigo: "",
      descricao: "",
      tipo_tabela: "TUSS",
      valor_referencia: "",
      vigencia_inicio: "",
      vigencia_fim: "",
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
          <h1 className="text-2xl font-bold text-gray-900">Tabelas de Referência</h1>
          <p className="text-gray-600">TUSS, CBHPM e outras tabelas</p>
        </div>
        <div className="flex gap-2">
          <label className="bg-green-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-green-700 cursor-pointer">
            <Download className="w-5 h-5" />
            {uploading ? 'Importando...' : 'Importar TUSS'}
            <input
              type="file"
              accept=".csv"
              onChange={handleImportCSV}
              className="hidden"
              disabled={uploading}
            />
          </label>
          <button
            onClick={openNewModal}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-blue-700"
          >
            <Plus className="w-5 h-5" />
            Nova Tabela
          </button>
        </div>
      </div>

      {/* Filtros */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Buscar por Código
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={searchCodigo}
                onChange={(e) => setSearchCodigo(e.target.value)}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="Ex: 10101012"
              />
              <button
                onClick={handleSearch}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
              >
                <Search className="w-5 h-5" />
              </button>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tipo de Tabela
            </label>
            <select
              value={filterTipo}
              onChange={(e) => setFilterTipo(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Todos</option>
              {tiposTabela.map((tipo) => (
                <option key={tipo} value={tipo}>
                  {tipo}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-end">
            <button
              onClick={loadTabelas}
              className="w-full bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700"
            >
              Aplicar Filtros
            </button>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12">Carregando...</div>
      ) : tabelas.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <Database className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">Nenhuma tabela cadastrada</p>
          <button
            onClick={openNewModal}
            className="mt-4 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            Cadastrar primeira tabela
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
                  Tipo
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Valor Ref.
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
              {tabelas.map((tabela) => (
                <tr key={tabela.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {tabela.codigo}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {tabela.descricao}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <span className="px-2 py-1 text-xs font-medium rounded-full bg-purple-100 text-purple-800">
                      {tabela.tipo_tabela}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {tabela.valor_referencia
                      ? new Intl.NumberFormat("pt-BR", {
                          style: "currency",
                          currency: "BRL",
                        }).format(tabela.valor_referencia)
                      : "-"}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-2 py-1 text-xs font-medium rounded-full ${
                        tabela.ativo
                          ? "bg-green-100 text-green-800"
                          : "bg-red-100 text-red-800"
                      }`}
                    >
                      {tabela.ativo ? "Ativo" : "Inativo"}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                      onClick={() => handleEdit(tabela)}
                      className="text-blue-600 hover:text-blue-900 mr-3"
                    >
                      <Edit className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(tabela.id)}
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
                {editingId ? "Editar Tabela" : "Nova Tabela"}
              </h2>
              <button onClick={() => setShowModal(false)}>
                <span className="text-2xl text-gray-500 hover:text-gray-700">×</span>
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Código *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.codigo}
                    onChange={(e) =>
                      setFormData({ ...formData, codigo: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="10101012"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Tipo de Tabela *
                  </label>
                  <select
                    required
                    value={formData.tipo_tabela}
                    onChange={(e) =>
                      setFormData({ ...formData, tipo_tabela: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    {tiposTabela.map((tipo) => (
                      <option key={tipo} value={tipo}>
                        {tipo}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Descrição *
                </label>
                <textarea
                  required
                  rows={3}
                  value={formData.descricao}
                  onChange={(e) =>
                    setFormData({ ...formData, descricao: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="Consulta médica em consultório"
                />
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Valor Referência
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.valor_referencia}
                    onChange={(e) =>
                      setFormData({ ...formData, valor_referencia: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="0.00"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Vigência Início
                  </label>
                  <input
                    type="date"
                    value={formData.vigencia_inicio}
                    onChange={(e) =>
                      setFormData({ ...formData, vigencia_inicio: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Vigência Fim
                  </label>
                  <input
                    type="date"
                    value={formData.vigencia_fim}
                    onChange={(e) =>
                      setFormData({ ...formData, vigencia_fim: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.ativo}
                  onChange={(e) =>
                    setFormData({ ...formData, ativo: e.target.checked })
                  }
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <label className="ml-2 text-sm text-gray-700">Tabela ativa</label>
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
