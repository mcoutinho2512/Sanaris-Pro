'use client';

import { useEffect, useState } from 'react';
import { FileText, Plus, Eye, Edit, ArrowLeft } from 'lucide-react';
import { useRouter } from 'next/navigation';

interface MedicalRecord {
  id: string;
  patient_id: string;
  appointment_id?: string;
  chief_complaint: string;
  diagnosis: string;
  created_at: string;
}

interface Patient {
  id: string;
  full_name: string;
}

export default function ProntuariosPage() {
  const router = useRouter();
  const [records, setRecords] = useState<MedicalRecord[]>([]);
  const [patients, setPatients] = useState<Record<string, Patient>>({});
  const [loading, setLoading] = useState(true);
  const [showNewModal, setShowNewModal] = useState(false);
  
  const [newRecord, setNewRecord] = useState({
    patient_id: '',
    chief_complaint: '',
    diagnosis: ''
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      
      const recordsRes = await fetch('http://localhost:8888/api/v1/medical-records/', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      const recordsData = await recordsRes.json();
      setRecords(recordsData);
      
      const patientsRes = await fetch('http://localhost:8888/api/v1/patients/', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      const patientsData = await patientsRes.json();
      const patientsMap: Record<string, Patient> = {};
      patientsData.forEach((p: Patient) => patientsMap[p.id] = p);
      setPatients(patientsMap);
      
    } catch (error) {
      console.error('Erro ao carregar prontuários:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRecord = async () => {
    if (!newRecord.patient_id || !newRecord.chief_complaint) {
      alert('Preencha paciente e queixa principal!');
      return;
    }

    try {
      const response = await fetch('http://localhost:8888/api/v1/medical-records/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(newRecord)
      });

      if (!response.ok) throw new Error('Erro ao criar prontuário');

      alert('Prontuário criado com sucesso!');
      setShowNewModal(false);
      setNewRecord({ patient_id: '', chief_complaint: '', diagnosis: '' });
      loadData();
    } catch (error: any) {
      console.error('Erro ao criar prontuário:', error);
      alert('Erro ao criar prontuário');
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-96">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="ml-4 text-gray-600">Carregando prontuários...</p>
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
          <h1 className="text-2xl font-bold">Prontuários Eletrônicos</h1>
          <p className="text-gray-600 mt-1">{records.length} prontuário(s)</p>
        </div>
        <button onClick={() => setShowNewModal(true)} className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition flex items-center gap-2">
          <Plus size={20} />
          Novo Prontuário
        </button>
      </div>

      <div className="space-y-4">
        {records.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center text-gray-500">
            Nenhum prontuário encontrado
          </div>
        ) : (
          records.map((record) => {
            const patient = patients[record.patient_id];
            const date = new Date(record.created_at).toLocaleDateString('pt-BR');
            
            return (
              <div key={record.id} className="bg-white rounded-lg shadow p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <FileText className="text-gray-400" size={20} />
                      <h3 className="text-lg font-semibold">{patient?.full_name || 'Paciente não encontrado'}</h3>
                      <span className="px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">Consulta</span>
                    </div>
                    <div className="ml-8 space-y-1">
                      <p className="text-sm text-gray-600"><span className="font-medium">Data:</span> {date}</p>
                      <p className="text-sm text-gray-600"><span className="font-medium">Queixa:</span> {record.chief_complaint}</p>
                      {record.diagnosis && (
                        <p className="text-sm text-gray-600"><span className="font-medium">Diagnóstico:</span> {record.diagnosis}</p>
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
            <h2 className="text-2xl font-bold mb-6">Novo Prontuário</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Paciente *</label>
                <select 
                  value={newRecord.patient_id}
                  onChange={(e) => setNewRecord({...newRecord, patient_id: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600"
                >
                  <option value="">Selecione um paciente</option>
                  {Object.values(patients).map(patient => (
                    <option key={patient.id} value={patient.id}>{patient.full_name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Queixa Principal *</label>
                <textarea 
                  rows={3}
                  value={newRecord.chief_complaint}
                  onChange={(e) => setNewRecord({...newRecord, chief_complaint: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600" 
                  placeholder="Descreva a queixa principal do paciente..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Diagnóstico</label>
                <textarea 
                  rows={3}
                  value={newRecord.diagnosis}
                  onChange={(e) => setNewRecord({...newRecord, diagnosis: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600" 
                  placeholder="Diagnóstico (opcional)"
                />
              </div>
            </div>

            <div className="flex gap-2 mt-6">
              <button onClick={() => setShowNewModal(false)} className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                Cancelar
              </button>
              <button onClick={handleCreateRecord} className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                Criar Prontuário
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
