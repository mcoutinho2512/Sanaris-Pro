'use client';

import { useEffect, useState } from 'react';
import { Pill, Plus, Eye, Edit, Trash2, ArrowLeft } from 'lucide-react';
import { useRouter } from 'next/navigation';

interface Prescription {
  id: string;
  patient_id: string;
  prescription_date: string;
  general_instructions?: string;
  is_signed: boolean;
}

interface Patient {
  id: string;
  full_name: string;
}

export default function PrescricoesPage() {
  const router = useRouter();
  const [prescriptions, setPrescriptions] = useState<Prescription[]>([]);
  const [patients, setPatients] = useState<Record<string, Patient>>({});
  const [loading, setLoading] = useState(true);
  const [currentUserId, setCurrentUserId] = useState<string>('');
  const [showNewModal, setShowNewModal] = useState(false);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedPrescription, setSelectedPrescription] = useState<Prescription | null>(null);
  
  const [newPrescription, setNewPrescription] = useState({
    patient_id: '',
    prescription_type: 'regular',
    general_instructions: '',
    medication_name: '',
    dosage: '',
    frequency: '',
    duration: ''
  });

  const [editPrescription, setEditPrescription] = useState({
    id: '',
    general_instructions: ''
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      if (!token) {
        alert('Faça login novamente!');
        router.push('/login');
        return;
      }
      
      // Pegar ID do usuário atual
      const meRes = await fetch('http://localhost:8888/api/v1/auth/me', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (meRes.ok) {
        const userData = await meRes.json();
        console.log('User data:', userData);
        setCurrentUserId(userData.id);
      } else {
        alert('Sessão expirada! Faça login novamente.');
        router.push('/login');
        return;
      }
      
      const prescriptionsRes = await fetch('http://localhost:8888/api/v1/prescriptions/', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const prescriptionsData = await prescriptionsRes.json();
      setPrescriptions(prescriptionsData);
      
      const patientsRes = await fetch('http://localhost:8888/api/v1/patients/', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const patientsData = await patientsRes.json();
      const patientsMap: Record<string, Patient> = {};
      patientsData.forEach((p: Patient) => patientsMap[p.id] = p);
      setPatients(patientsMap);
      
    } catch (error) {
      console.error('Erro ao carregar prescrições:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetails = (prescription: Prescription) => {
    setSelectedPrescription(prescription);
    setShowDetailsModal(true);
  };

  const handleEdit = (prescription: Prescription) => {
    setEditPrescription({
      id: prescription.id,
      general_instructions: prescription.general_instructions || ''
    });
    setShowEditModal(true);
  };

  const handleCreatePrescription = async () => {
    if (!newPrescription.patient_id || !newPrescription.medication_name) {
      alert('Preencha paciente e medicamento!');
      return;
    }

    if (!currentUserId) {
      alert('Sua sessão expirou! Faça login novamente.');
      router.push('/login');
      return;
    }

    try {
      const payload = {
        patient_id: newPrescription.patient_id,
        healthcare_professional_id: currentUserId,
        prescription_type: newPrescription.prescription_type,
        general_instructions: newPrescription.general_instructions,
        items: [
          {
            medication_name: newPrescription.medication_name,
            dosage: newPrescription.dosage,
            frequency: newPrescription.frequency,
            duration: newPrescription.duration,
            is_generic: true,
            is_controlled: false
          }
        ]
      };

      console.log('Payload completo:', JSON.stringify(payload, null, 2));

      const response = await fetch('http://localhost:8888/api/v1/prescriptions/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(payload)
      });

      const responseData = await response.json();

      if (!response.ok) {
        console.error('Erro da API:', responseData);
        throw new Error(responseData.detail || 'Erro ao criar prescrição');
      }

      alert('Prescrição criada com sucesso!');
      setShowNewModal(false);
      setNewPrescription({
        patient_id: '',
        prescription_type: 'regular',
        general_instructions: '',
        medication_name: '',
        dosage: '',
        frequency: '',
        duration: ''
      });
      loadData();
    } catch (error: any) {
      console.error('Erro:', error);
      alert(error.message || 'Erro ao criar prescrição');
    }
  };

  const handleUpdatePrescription = async () => {
    try {
      const response = await fetch(`http://localhost:8888/api/v1/prescriptions/${editPrescription.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          general_instructions: editPrescription.general_instructions
        })
      });

      if (!response.ok) throw new Error('Erro ao atualizar prescrição');

      alert('Prescrição atualizada com sucesso!');
      setShowEditModal(false);
      loadData();
    } catch (error: any) {
      console.error('Erro ao atualizar prescrição:', error);
      alert('Erro ao atualizar prescrição');
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Tem certeza que deseja excluir esta prescrição?')) return;

    try {
      const response = await fetch(`http://localhost:8888/api/v1/prescriptions/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });

      if (!response.ok) throw new Error('Erro ao excluir');

      alert('Prescrição excluída com sucesso!');
      loadData();
    } catch (error) {
      alert('Erro ao excluir prescrição');
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-96">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="ml-4 text-gray-600">Carregando prescrições...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="mb-4">
        <button onClick={() => router.push('/')} className="flex items-center gap-2 text-gray-600 hover:text-gray-900">
          <ArrowLeft className="w-5 h-5" />
          <span>Voltar ao Dashboard</span>
        </button>
      </div>

      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold">Prescrições Médicas</h1>
          <p className="text-gray-600 mt-1">{prescriptions.length} prescrição(ões)</p>
        </div>
        <button onClick={() => setShowNewModal(true)} className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition flex items-center gap-2">
          <Plus size={20} />
          Nova Prescrição
        </button>
      </div>

      <div className="space-y-4">
        {prescriptions.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center text-gray-500">
            Nenhuma prescrição encontrada
          </div>
        ) : (
          prescriptions.map((prescription) => {
            const patient = patients[prescription.patient_id];
            const date = new Date(prescription.prescription_date).toLocaleDateString('pt-BR');
            
            return (
              <div key={prescription.id} className="bg-white rounded-lg shadow p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <Pill className="text-gray-400" size={20} />
                      <h3 className="text-lg font-semibold">{patient?.full_name || 'Paciente não encontrado'}</h3>
                      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${prescription.is_signed ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                        {prescription.is_signed ? 'Assinada' : 'Pendente'}
                      </span>
                    </div>
                    <div className="ml-8 space-y-1">
                      <p className="text-sm text-gray-600"><span className="font-medium">Data:</span> {date}</p>
                      {prescription.general_instructions && (
                        <p className="text-sm text-gray-600"><span className="font-medium">Instruções:</span> {prescription.general_instructions}</p>
                      )}
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button onClick={() => handleViewDetails(prescription)} className="px-3 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition flex items-center gap-2">
                      <Eye size={16} />
                      Ver Detalhes
                    </button>
                    <button onClick={() => handleEdit(prescription)} className="px-3 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition flex items-center gap-2">
                      <Edit size={16} />
                      Editar
                    </button>
                    <button onClick={() => handleDelete(prescription.id)} className="px-3 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition flex items-center gap-2">
                      <Trash2 size={16} />
                      Excluir
                    </button>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Modal Nova Prescrição */}
      {showNewModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-6">Nova Prescrição</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Paciente *</label>
                <select 
                  value={newPrescription.patient_id}
                  onChange={(e) => setNewPrescription({...newPrescription, patient_id: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600"
                >
                  <option value="">Selecione um paciente</option>
                  {Object.values(patients).map(patient => (
                    <option key={patient.id} value={patient.id}>{patient.full_name}</option>
                  ))}
                </select>
              </div>

              <div className="border-t pt-4">
                <h3 className="font-semibold mb-3">Medicamento</h3>
                
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Nome do Medicamento *</label>
                    <input 
                      type="text"
                      value={newPrescription.medication_name}
                      onChange={(e) => setNewPrescription({...newPrescription, medication_name: e.target.value})}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600" 
                      placeholder="Ex: Dipirona 500mg"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Dosagem</label>
                      <input 
                        type="text"
                        value={newPrescription.dosage}
                        onChange={(e) => setNewPrescription({...newPrescription, dosage: e.target.value})}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600" 
                        placeholder="Ex: 1 comprimido"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Frequência</label>
                      <input 
                        type="text"
                        value={newPrescription.frequency}
                        onChange={(e) => setNewPrescription({...newPrescription, frequency: e.target.value})}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600" 
                        placeholder="Ex: a cada 6 horas"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Duração</label>
                    <input 
                      type="text"
                      value={newPrescription.duration}
                      onChange={(e) => setNewPrescription({...newPrescription, duration: e.target.value})}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600" 
                      placeholder="Ex: 7 dias"
                    />
                  </div>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Instruções Gerais</label>
                <textarea 
                  rows={2}
                  value={newPrescription.general_instructions}
                  onChange={(e) => setNewPrescription({...newPrescription, general_instructions: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600" 
                  placeholder="Ex: Tomar após as refeições"
                />
              </div>
            </div>

            <div className="flex gap-2 mt-6">
              <button onClick={() => setShowNewModal(false)} className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                Cancelar
              </button>
              <button onClick={handleCreatePrescription} className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                Criar Prescrição
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Detalhes */}
      {showDetailsModal && selectedPrescription && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl p-6 w-full max-w-3xl max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-start mb-6">
              <div>
                <h2 className="text-2xl font-bold">Detalhes da Prescrição</h2>
                <p className="text-gray-600 mt-1">{patients[selectedPrescription.patient_id]?.full_name}</p>
              </div>
              <button onClick={() => setShowDetailsModal(false)} className="text-gray-400 hover:text-gray-600">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="space-y-4">
              <div className="border-b pb-3">
                <h3 className="font-semibold text-gray-700 mb-1">Data da Prescrição</h3>
                <p className="text-gray-900">{new Date(selectedPrescription.prescription_date).toLocaleDateString('pt-BR')}</p>
              </div>

              <div className="border-b pb-3">
                <h3 className="font-semibold text-gray-700 mb-1">Status</h3>
                <span className={`px-2 py-1 text-xs font-semibold rounded-full ${selectedPrescription.is_signed ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                  {selectedPrescription.is_signed ? 'Assinada Digitalmente' : 'Pendente de Assinatura'}
                </span>
              </div>

              {selectedPrescription.general_instructions && (
                <div className="border-b pb-3">
                  <h3 className="font-semibold text-gray-700 mb-1">Instruções Gerais</h3>
                  <p className="text-gray-900 whitespace-pre-wrap">{selectedPrescription.general_instructions}</p>
                </div>
              )}

              <div className="border-b pb-3">
                <h3 className="font-semibold text-gray-700 mb-1">ID da Prescrição</h3>
                <p className="text-gray-600 text-sm font-mono">{selectedPrescription.id}</p>
              </div>
            </div>

            <div className="flex gap-2 mt-6">
              <button onClick={() => setShowDetailsModal(false)} className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                Fechar
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Edição */}
      {showEditModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl p-6 w-full max-w-2xl">
            <h2 className="text-2xl font-bold mb-6">Editar Prescrição</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Instruções Gerais</label>
                <textarea 
                  rows={4}
                  value={editPrescription.general_instructions}
                  onChange={(e) => setEditPrescription({...editPrescription, general_instructions: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600" 
                  placeholder="Instruções gerais da prescrição..."
                />
              </div>

              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <p className="text-sm text-yellow-800">
                  <strong>Nota:</strong> Para editar medicamentos específicos, crie uma nova prescrição.
                </p>
              </div>
            </div>

            <div className="flex gap-2 mt-6">
              <button onClick={() => setShowEditModal(false)} className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                Cancelar
              </button>
              <button onClick={handleUpdatePrescription} className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                Salvar Alterações
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
