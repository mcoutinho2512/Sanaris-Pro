'use client';

import { useState, useEffect } from 'react';
import { tissGuiasAPI, tissOperadorasAPI, tissTabelasAPI } from '@/lib/api/tiss';
import { api } from '@/lib/api';
import { prestadoresAPI } from '@/lib/api/tiss';
import { Plus, FileText, Edit, Trash2, Eye } from 'lucide-react';
import { toast } from 'react-hot-toast';

export default function GuiasPage() {
  const [guias, setGuias] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  
  // Dados para dropdowns
  const [pacientes, setPacientes] = useState([]);
  const [operadoras, setOperadoras] = useState([]);
  const [prestadores, setPrestadores] = useState([]);
  const [lotes, setLotes] = useState([]);

  const [formData, setFormData] = useState({
    lote_id: '',
    patient_id: '',
    tipo_guia: 'consulta',
    indicacao_clinica: 'C',
    data_atendimento: '',
    hora_inicial: '',
    hora_final: '',
    numero_carteira: '',
    nome_beneficiario: '',
    codigo_prestador_na_operadora: '',
    nome_contratado: '',
    cnpj_contratado: '',
    cnes: '',
    nome_profissional: '',
    numero_conselho_profissional: '',
    uf_conselho: '',
    cid10_principal: '',
    observacoes_clinicas: '',
  });

  useEffect(() => {
    loadGuias();
    loadDependencies();
  }, []);

  const loadDependencies = async () => {
    try {
      const [pacRes, opRes, prestRes, loteRes] = await Promise.all([
        api.get('/patients/'),
        tissOperadorasAPI.list(),
        prestadoresAPI.list(),
        api.get('/tiss/lotes/'),
      ]);
      
      setPacientes(pacRes.data);
      setOperadoras(opRes.data);
      setPrestadores(prestRes.data);
      setLotes(loteRes.data);
    } catch (error) {
      console.error('Erro ao carregar dependências:', error);
    }
  };

  const loadGuias = async () => {
    try {
      const response = await tissGuiasAPI.list();
      setGuias(response.data);
    } catch (error) {
      toast.error('Erro ao carregar guias');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      await tissGuiasAPI.create(formData);
      toast.success('Guia criada com sucesso!');
      setShowModal(false);
      resetForm();
      loadGuias();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Erro ao criar guia');
    }
  };

  const resetForm = () => {
    setFormData({
      lote_id: '',
      patient_id: '',
      tipo_guia: 'consulta',
    indicacao_clinica: 'C',
      data_atendimento: '',
      hora_inicial: '',
      hora_final: '',
      numero_carteira: '',
      nome_beneficiario: '',
      codigo_prestador_na_operadora: '',
      nome_contratado: '',
      cnpj_contratado: '',
      cnes: '',
      nome_profissional: '',
      numero_conselho_profissional: '',
      uf_conselho: '',
      cid10_principal: '',
      observacoes_clinicas: '',
    });
  };

  const handlePacienteChange = (patientId: string) => {
    const paciente = pacientes.find((p: any) => p.id === patientId);
    if (paciente) {
      setFormData({
        ...formData,
        patient_id: patientId,
        nome_beneficiario: (paciente as any).full_name,
        numero_carteira: (paciente as any).numero_carteira || '',
      });
    }
  };

  const handlePrestadorChange = (prestadorId: string) => {
    const prestador = prestadores.find((p: any) => p.id === prestadorId);
    if (prestador) {
      setFormData({
        ...formData,
        nome_contratado: (prestador as any).nome,
        cnpj_contratado: (prestador as any).cnpj || (prestador as any).cpf || '',
        cnes: (prestador as any).cnes || '',
        nome_profissional: (prestador as any).tipo_prestador === 'medico' ? (prestador as any).nome : '',
        numero_conselho_profissional: (prestador as any).crm || '',
        uf_conselho: (prestador as any).uf_crm || '',
      });
    }
  };

  const getStatusColor = (status: string) => {
    const colors: any = {
      pendente: "bg-yellow-100 text-yellow-800",
      enviada: "bg-blue-100 text-blue-800",
      processada: "bg-green-100 text-green-800",
      glosada: "bg-red-100 text-red-800",
      paga: "bg-emerald-100 text-emerald-800",
    };
    return colors[status] || "bg-gray-100 text-gray-800";
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Guias TISS</h1>
          <p className="text-gray-600">Gestão de guias de atendimento</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-blue-700"
        >
          <Plus className="w-5 h-5" />
          Nova Guia
        </button>
      </div>

      {loading ? (
        <div className="text-center py-12">Carregando...</div>
      ) : guias.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 mb-2">Nenhuma guia cadastrada</p>
          <button
            onClick={() => setShowModal(true)}
            className="mt-4 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            Criar primeira guia
          </button>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Número Guia
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Tipo
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Beneficiário
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Data
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Valor
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                  Ações
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {guias.map((guia: any) => (
                <tr key={guia.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {guia.numero_guia_prestador}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {guia.tipo_guia}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {guia.nome_beneficiario}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(guia.data_atendimento).toLocaleDateString('pt-BR')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(guia.status)}`}>
                      {guia.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    R$ {guia.valor_total_informado?.toFixed(2) || '0.00'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button className="text-blue-600 hover:text-blue-900 mr-3">
                      <Eye className="w-4 h-4" />
                    </button>
                    <button className="text-red-600 hover:text-red-900">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* MODAL CRIAR GUIA */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 overflow-y-auto">
          <div className="bg-white rounded-lg p-6 w-full max-w-4xl my-8 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">Nova Guia TISS</h2>
              <button onClick={() => setShowModal(false)}>
                <span className="text-2xl text-gray-500 hover:text-gray-700">×</span>
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Lote *
                  </label>
                  <select
                    required
                    value={formData.lote_id}
                    onChange={(e) => setFormData({ ...formData, lote_id: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Selecione o lote</option>
                    {lotes.map((lote: any) => (
                      <option key={lote.id} value={lote.id}>
                        {lote.numero_lote} - {lote.operadora?.nome_fantasia}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Tipo de Guia *
                  </label>
                  <select
                    required
                    value={formData.tipo_guia}
                    onChange={(e) => setFormData({ ...formData, tipo_guia: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="consulta">Consulta</option>
                    <option value="sadt">SP/SADT</option>
                    <option value="internacao">Internação</option>
                    <option value="resumo_internacao">Resumo Internação</option>
                  </select>
                </div>

                <div className="col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Paciente *
                  </label>
                  <select
                    required
                    value={formData.patient_id}
                    onChange={(e) => handlePacienteChange(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Selecione o paciente</option>
                    {pacientes.map((pac: any) => (
                      <option key={pac.id} value={pac.id}>
                        {pac.full_name} {pac.cpf && `- CPF: ${pac.cpf}`}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Prestador *
                  </label>
                  <select
                    required
                    onChange={(e) => handlePrestadorChange(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Selecione o prestador</option>
                    {prestadores.map((prest: any) => (
                      <option key={prest.id} value={prest.id}>
                        {prest.nome} - {prest.tipo_prestador}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Data do Atendimento *
                  </label>
                  <input
                    type="date"
                    required
                    value={formData.data_atendimento}
                    onChange={(e) => setFormData({ ...formData, data_atendimento: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Hora Inicial
                    </label>
                    <input
                      type="time"
                      value={formData.hora_inicial}
                      onChange={(e) => setFormData({ ...formData, hora_inicial: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Hora Final
                    </label>
                    <input
                      type="time"
                      value={formData.hora_final}
                      onChange={(e) => setFormData({ ...formData, hora_final: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    CID10 Principal
                  </label>
                  <input
                    type="text"
                    maxLength={10}
                    value={formData.cid10_principal}
                    onChange={(e) => setFormData({ ...formData, cid10_principal: e.target.value.toUpperCase() })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="A00.0"
                  />
                </div>

                <div className="col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Observações Clínicas
                  </label>
                  <textarea
                    rows={3}
                    value={formData.observacoes_clinicas}
                    onChange={(e) => setFormData({ ...formData, observacoes_clinicas: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
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
                  Criar Guia
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
