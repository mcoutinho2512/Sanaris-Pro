'use client';

import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { Search, Plus, Edit, Trash2, Eye, X } from 'lucide-react';
import { patientsService, Patient } from '@/services/patients.service';
import { PatientModal } from '@/components/patients/PatientModal';

export default function PacientesPage() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const searchParams = useSearchParams();

  useEffect(() => {
    loadPatients();
  }, []);

  // Detectar query params para abrir modal de detalhes
  useEffect(() => {
    const patientId = searchParams.get('id');
    const action = searchParams.get('action');
    
    if (patientId && action === 'view') {
      // Buscar paciente e abrir modal
      const patient = patients.find(p => p.id === patientId);
      if (patient) {
        setSelectedPatient(patient);
        setShowDetailsModal(true);
      } else {
        // Se não encontrou na lista, buscar da API
        patientsService.get(patientId).then(patient => {
          setSelectedPatient(patient);
          setShowDetailsModal(true);
        }).catch(error => {
          console.error('Erro ao buscar paciente:', error);
        });
      }
    }
  }, [searchParams, patients]);

  const loadPatients = async () => {
    try {
      setLoading(true);
      const data = await patientsService.list(search);
      setPatients(data);
    } catch (error) {
      console.error('Erro ao carregar pacientes:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    loadPatients();
  };

  const handleNew = () => {
    setSelectedPatient(null);
    setShowModal(true);
  };

  const handleEdit = (patient: Patient) => {
    setSelectedPatient(patient);
    setShowModal(true);
  };

  const handleDelete = async (patient: Patient) => {
    if (!confirm(`Deseja realmente excluir o paciente ${patient.full_name}?`)) {
      return;
    }

    try {
      await patientsService.delete(patient.id);
      alert('Paciente excluído com sucesso!');
      loadPatients();
    } catch (error: any) {
      console.error('Erro ao excluir paciente:', error);
      alert(error.response?.data?.detail || 'Erro ao excluir paciente');
    }
  };

  const handleViewDetails = (patient: Patient) => {
    setSelectedPatient(patient);
    setShowDetailsModal(true);
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('pt-BR');
  };

  const formatCPF = (cpf: string | null) => {
    if (!cpf) return '-';
    return cpf;
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-96">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="ml-4 text-gray-600">Carregando pacientes...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold">Pacientes</h1>
          <p className="text-gray-600 mt-1">{patients.length} paciente(s) cadastrado(s)</p>
        </div>
        <button
          onClick={handleNew}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition flex items-center gap-2"
        >
          <Plus size={20} />
          Novo Paciente
        </button>
      </div>

      {/* Busca */}
      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <div className="flex gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Buscar por nome, CPF ou email..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <button
            onClick={handleSearch}
            className="bg-gray-100 px-6 py-2 rounded-lg hover:bg-gray-200 transition"
          >
            Buscar
          </button>
        </div>
      </div>

      {/* Tabela */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Nome
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  CPF
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Data Nascimento
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Telefone
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Email
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Ações
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {patients.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-gray-500">
                    Nenhum paciente encontrado
                  </td>
                </tr>
              ) : (
                patients.map((patient) => (
                  <tr key={patient.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="font-medium text-gray-900">{patient.full_name}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatCPF(patient.cpf)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(patient.birth_date)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {patient.phone || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {patient.email || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`px-2 py-1 text-xs font-semibold rounded-full ${
                          patient.is_active
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {patient.is_active ? 'Ativo' : 'Inativo'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex justify-end gap-2">
                        <button
                          onClick={() => handleViewDetails(patient)}
                          className="text-blue-600 hover:text-blue-900"
                          title="Ver detalhes"
                        >
                          <Eye size={18} />
                        </button>
                        <button
                          onClick={() => handleEdit(patient)}
                          className="text-green-600 hover:text-green-900"
                          title="Editar"
                        >
                          <Edit size={18} />
                        </button>
                        <button
                          onClick={() => handleDelete(patient)}
                          className="text-red-600 hover:text-red-900"
                          title="Excluir"
                        >
                          <Trash2 size={18} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal de Cadastro/Edição */}
      <PatientModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        onSuccess={loadPatients}
        patient={selectedPatient}
      />

      {/* Modal de Detalhes */}
      {showDetailsModal && selectedPatient && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">Detalhes do Paciente</h2>
              <button
                onClick={() => setShowDetailsModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X size={24} />
              </button>
            </div>

            <div className="space-y-3">
              <div>
                <span className="font-semibold">Nome:</span> {selectedPatient.full_name}
              </div>
              <div>
                <span className="font-semibold">CPF:</span> {formatCPF(selectedPatient.cpf)}
              </div>
              <div>
                <span className="font-semibold">Data de Nascimento:</span> {formatDate(selectedPatient.birth_date)}
              </div>
              <div>
                <span className="font-semibold">Telefone:</span> {selectedPatient.phone || '-'}
              </div>
              <div>
                <span className="font-semibold">Email:</span> {selectedPatient.email || '-'}
              </div>
              <div>
                <span className="font-semibold">Status:</span>{' '}
                <span
                  className={`px-2 py-1 text-xs font-semibold rounded-full ${
                    selectedPatient.is_active
                      ? 'bg-green-100 text-green-800'
                      : 'bg-red-100 text-red-800'
                  }`}
                >
                  {selectedPatient.is_active ? 'Ativo' : 'Inativo'}
                </span>
              </div>
              <div>
                <span className="font-semibold">Cadastrado em:</span>{' '}
                {new Date(selectedPatient.created_at).toLocaleString('pt-BR')}
              </div>
            </div>

            <div className="flex justify-end mt-6">
              <button
                onClick={() => setShowDetailsModal(false)}
                className="bg-gray-200 px-4 py-2 rounded-lg hover:bg-gray-300"
              >
                Fechar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
