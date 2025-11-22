"use client";

import { useState, useEffect } from "react";
import { prestadoresAPI } from "@/lib/api/tiss";
import { Plus, Edit, Trash2, UserCheck, Building2 } from "lucide-react";
import { toast } from "react-hot-toast";

interface Prestador {
  id: string;
  tipo_prestador: string;
  nome: string;
  razao_social?: string;
  cnpj?: string;
  cpf?: string;
  crm?: string;
  uf_crm?: string;
  especialidade?: string;
  cnes?: string;
  telefone?: string;
  email?: string;
  ativo: boolean;
}

export default function PrestadoresPage() {
  const [prestadores, setPrestadores] = useState<Prestador[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [filterTipo, setFilterTipo] = useState("");
  const [formData, setFormData] = useState({
    tipo_prestador: "medico",
    nome: "",
    razao_social: "",
    cnpj: "",
    cpf: "",
    crm: "",
    uf_crm: "",
    especialidade: "",
    codigo_cbo: "",
    cnes: "",
    telefone: "",
    email: "",
    cep: "",
    logradouro: "",
    numero: "",
    complemento: "",
    bairro: "",
    cidade: "",
    estado: "",
    ativo: true,
  });

  const tiposPrestador = [
    { value: "medico", label: "Médico", icon: UserCheck },
    { value: "clinica", label: "Clínica", icon: Building2 },
    { value: "laboratorio", label: "Laboratório", icon: Building2 },
    { value: "hospital", label: "Hospital", icon: Building2 },
  ];

  useEffect(() => {
    loadPrestadores();
  }, [filterTipo]);

  const loadPrestadores = async () => {
    try {
      const params: any = {};
      if (filterTipo) params.tipo_prestador = filterTipo;
      
      const response = await prestadoresAPI.list(params);
      setPrestadores(response.data);
    } catch (error) {
      toast.error("Erro ao carregar prestadores");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Filtrar campos vazios
    const cleanData: any = {
      tipo_prestador: formData.tipo_prestador,
      nome: formData.nome,
      ativo: formData.ativo,
    };

    // Adicionar apenas campos preenchidos
    if (formData.razao_social) cleanData.razao_social = formData.razao_social;
    if (formData.cnpj) cleanData.cnpj = formData.cnpj;
    if (formData.cpf) cleanData.cpf = formData.cpf;
    if (formData.crm) cleanData.crm = formData.crm;
    if (formData.uf_crm) cleanData.uf_crm = formData.uf_crm;
    if (formData.especialidade) cleanData.especialidade = formData.especialidade;
    if (formData.codigo_cbo) cleanData.codigo_cbo = formData.codigo_cbo;
    if (formData.cnes) cleanData.cnes = formData.cnes;
    if (formData.telefone) cleanData.telefone = formData.telefone;
    if (formData.email) cleanData.email = formData.email;

    try {
      if (editingId) {
        await prestadoresAPI.update(editingId, cleanData);
        toast.success("Prestador atualizado com sucesso!");
      } else {
        await prestadoresAPI.create(cleanData);
        toast.success("Prestador cadastrado com sucesso!");
      }

      setShowModal(false);
      resetForm();
      loadPrestadores();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Erro ao salvar prestador");
    }
  };

  const handleEdit = (prestador: Prestador) => {
    setFormData({
      tipo_prestador: prestador.tipo_prestador,
      nome: prestador.nome,
      razao_social: prestador.razao_social || "",
      cnpj: prestador.cnpj || "",
      cpf: prestador.cpf || "",
      crm: prestador.crm || "",
      uf_crm: prestador.uf_crm || "",
      especialidade: prestador.especialidade || "",
      codigo_cbo: "",
      cnes: prestador.cnes || "",
      telefone: prestador.telefone || "",
      email: prestador.email || "",
      cep: "",
      logradouro: "",
      numero: "",
      complemento: "",
      bairro: "",
      cidade: "",
      estado: "",
      ativo: prestador.ativo,
    });
    setEditingId(prestador.id);
    setShowModal(true);
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Deseja realmente excluir este prestador?")) return;

    try {
      await prestadoresAPI.delete(id);
      toast.success("Prestador excluído com sucesso!");
      loadPrestadores();
    } catch (error) {
      toast.error("Erro ao excluir prestador");
    }
  };

  const resetForm = () => {
    setFormData({
      tipo_prestador: "medico",
      nome: "",
      razao_social: "",
      cnpj: "",
      cpf: "",
      crm: "",
      uf_crm: "",
      especialidade: "",
      codigo_cbo: "",
      cnes: "",
      telefone: "",
      email: "",
      cep: "",
      logradouro: "",
      numero: "",
      complemento: "",
      bairro: "",
      cidade: "",
      estado: "",
      ativo: true,
    });
    setEditingId(null);
  };

  const getTipoLabel = (tipo: string) => {
    const item = tiposPrestador.find((t) => t.value === tipo);
    return item?.label || tipo;
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Prestadores</h1>
          <p className="text-gray-600">Médicos, clínicas e estabelecimentos</p>
        </div>
        <button
          onClick={() => { resetForm(); setShowModal(true); }}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-blue-700"
        >
          <Plus className="w-5 h-5" />
          Novo Prestador
        </button>
      </div>

      {/* Filtros */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="flex gap-4">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tipo de Prestador
            </label>
            <select
              value={filterTipo}
              onChange={(e) => setFilterTipo(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Todos</option>
              {tiposPrestador.map((tipo) => (
                <option key={tipo.value} value={tipo.value}>
                  {tipo.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12">Carregando...</div>
      ) : prestadores.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <UserCheck className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">Nenhum prestador cadastrado</p>
          <button
            onClick={() => { resetForm(); setShowModal(true); }}
            className="mt-4 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            Cadastrar primeiro prestador
          </button>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Tipo
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Nome
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Documento
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Especialidade/CRM
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Contato
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
              {prestadores.map((prestador) => (
                <tr key={prestador.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {getTipoLabel(prestador.tipo_prestador)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {prestador.nome}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {prestador.cnpj || prestador.cpf || "-"}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {prestador.especialidade && `${prestador.especialidade}`}
                    {prestador.crm && ` - CRM ${prestador.crm}/${prestador.uf_crm}`}
                    {!prestador.especialidade && !prestador.crm && "-"}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {prestador.telefone || prestador.email || "-"}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-2 py-1 text-xs font-medium rounded-full ${
                        prestador.ativo
                          ? "bg-green-100 text-green-800"
                          : "bg-red-100 text-red-800"
                      }`}
                    >
                      {prestador.ativo ? "Ativo" : "Inativo"}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                      onClick={() => handleEdit(prestador)}
                      className="text-blue-600 hover:text-blue-900 mr-3"
                    >
                      <Edit className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(prestador.id)}
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
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 overflow-y-auto">
          <div className="bg-white rounded-lg p-6 w-full max-w-4xl my-8 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">
                {editingId ? "Editar Prestador" : "Novo Prestador"}
              </h2>
              <button onClick={() => setShowModal(false)}>
                <span className="text-2xl text-gray-500 hover:text-gray-700">×</span>
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tipo de Prestador *
                </label>
                <select
                  required
                  value={formData.tipo_prestador}
                  onChange={(e) =>
                    setFormData({ ...formData, tipo_prestador: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  {tiposPrestador.map((tipo) => (
                    <option key={tipo.value} value={tipo.value}>
                      {tipo.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Nome *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.nome}
                    onChange={(e) =>
                      setFormData({ ...formData, nome: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="Nome completo ou nome fantasia"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Razão Social
                  </label>
                  <input
                    type="text"
                    value={formData.razao_social}
                    onChange={(e) =>
                      setFormData({ ...formData, razao_social: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    CPF
                  </label>
                  <input
                    type="text"
                    value={formData.cpf}
                    onChange={(e) =>
                      setFormData({ ...formData, cpf: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="000.000.000-00"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    CNPJ
                  </label>
                  <input
                    type="text"
                    value={formData.cnpj}
                    onChange={(e) =>
                      setFormData({ ...formData, cnpj: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="00.000.000/0000-00"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    CNES
                  </label>
                  <input
                    type="text"
                    value={formData.cnes}
                    onChange={(e) =>
                      setFormData({ ...formData, cnes: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              {formData.tipo_prestador === "medico" && (
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      CRM
                    </label>
                    <input
                      type="text"
                      value={formData.crm}
                      onChange={(e) =>
                        setFormData({ ...formData, crm: e.target.value })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      UF CRM
                    </label>
                    <input
                      type="text"
                      maxLength={2}
                      value={formData.uf_crm}
                      onChange={(e) =>
                        setFormData({ ...formData, uf_crm: e.target.value.toUpperCase() })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      placeholder="RJ"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Especialidade
                    </label>
                    <input
                      type="text"
                      value={formData.especialidade}
                      onChange={(e) =>
                        setFormData({ ...formData, especialidade: e.target.value })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
              )}

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
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email
                  </label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) =>
                      setFormData({ ...formData, email: e.target.value })
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
                <label className="ml-2 text-sm text-gray-700">Prestador ativo</label>
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
