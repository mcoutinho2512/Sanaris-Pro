'use client';

import { useEffect, useState } from 'react';
import { Pill, Plus, Eye, Edit, ArrowLeft } from 'lucide-react';
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
  const [showNewModal, setShowNewModal] = useState(false);
  
  const [newPrescription, setNewPrescription] = useState({
    patient_id: '',
    prescription_type: 'simple',
    general_instructions: '',
    medication_name: '',
    dosage: '',
    frequency: '',
    duration: ''
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      
      const prescriptionsRes = await fetch('http://localhost:8888/api/v1/prescriptions/', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      const prescriptionsData = await prescriptionsRes.json();
      setPrescriptions(prescriptionsData);
      
      const patientsRes = await fetch('http://localhost:8888/api/v1/patients/', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
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

  const handleCreatePrescription = async () => {
    if (!newPrescription.patient_id || !newPrescription.medication_name) {
      alert('Preencha paciente e medicamento!');
      return;
    }

    try {
      const payload = {
        patient_id: newPrescription.patient_id,
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

      const response = await fetch('http://localhost:8888/api/v1/prescriptions/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) throw new Error('Erro ao criar prescrição');

      alert('Prescrição criada com sucesso!');
      setShowNewModal(false);
      setNewPrescription({
        patient_id: '',
        prescription_type: 'simple',
        general_instructions: '',
        medication_name: '',
        dosage: '',
        frequency: '',
        duration: ''
      });
      loadData();
    } catch (error: any) {
      console.error('Erro ao criar prescrição:', error);
      alert('Erro ao criar prescrição');
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
                    <button className="px-3 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition flex items-center gap-2">
                      <Eye size={16} />
                      Ver Detalhes
                    </button>
                    <button className="px-3 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition flex items-center gap-2">
                      <Edit size={16} />
                      Editar
                    </button>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      {showNewModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl p-6 w-full max-w-2xl">
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
    </div>
  );
}
