'use client';

import { useEffect, useState } from 'react';
import { FileText, Plus, Eye, Edit, Calendar, User } from 'lucide-react';
import { medicalRecordsService, MedicalRecord } from '@/services/medical-records.service';
import { patientsService, Patient } from '@/services/patients.service';

export default function ProntuariosPage() {
  const [records, setRecords] = useState<MedicalRecord[]>([]);
  const [patients, setPatients] = useState<Record<string, Patient>>({});
  const [loading, setLoading] = useState(true);
  const [selectedRecord, setSelectedRecord] = useState<MedicalRecord | null>(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [showFormModal, setShowFormModal] = useState(false);
  const [editingRecord, setEditingRecord] = useState<MedicalRecord | null>(null);
  const [formData, setFormData] = useState({
    patient_id: '',
    chief_complaint: '',
    history_of_present_illness: '',
    past_medical_history: '',
    medications: '',
    allergies: '',
    diagnosis: '',
    treatment_plan: '',
    prescriptions: '',
    exams_requested: '',
    observations: '',
  });

  useEffect(() => {
    loadData();
  }, []);

  const handleNew = () => {
    setEditingRecord(null);
    setFormData({
      patient_id: '',
      chief_complaint: '',
      history_of_present_illness: '',
      past_medical_history: '',
      medications: '',
      allergies: '',
      diagnosis: '',
      treatment_plan: '',
      prescriptions: '',
      exams_requested: '',
      observations: '',
    });
    setShowFormModal(true);
  };

  const handleEdit = (record: MedicalRecord) => {
    setEditingRecord(record);
    setFormData({
      patient_id: record.patient_id,
      chief_complaint: record.chief_complaint || '',
      history_of_present_illness: record.history_of_present_illness || '',
      past_medical_history: record.past_medical_history || '',
      medications: record.medications || '',
      allergies: record.allergies || '',
      diagnosis: record.diagnosis || '',
      treatment_plan: record.treatment_plan || '',
      prescriptions: record.prescriptions || '',
      exams_requested: record.exams_requested || '',
      observations: record.observations || '',
    });
    setShowFormModal(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.patient_id) {
      alert('Selecione um paciente');
      return;
    }

    try {
      if (editingRecord) {
        // Editar
        await medicalRecordsService.update(editingRecord.id, formData);
        alert('Prontuário atualizado!');
      } else {
        // Criar novo
        await medicalRecordsService.create({
          ...formData,
          healthcare_professional_id: 'doctor-001',
        });
        alert('Prontuário criado!');
      }
      
      setShowFormModal(false);
      loadData();
    } catch (error: any) {
      console.error('Erro ao salvar:', error);
      alert(error.response?.data?.detail || 'Erro ao salvar prontuário');
    }
  };

  const loadData = async () => {
    try {
      setLoading(true);
      
      // Carregar prontuários
      const recordsData = await medicalRecordsService.list({ limit: 50 });
      setRecords(recordsData);
      
      // Carregar pacientes
      const patientsData = await patientsService.list();
      const patientsMap: Record<string, Patient> = {};
      patientsData.forEach(p => patientsMap[p.id] = p);
      setPatients(patientsMap);
      
    } catch (error) {
      console.error('Erro ao carregar prontuários:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetails = async (record: MedicalRecord) => {
    try {
      // Buscar detalhes completos da API
      const fullRecord = await medicalRecordsService.get(record.id);
      setSelectedRecord(fullRecord);
      setShowDetailsModal(true);
    } catch (error) {
      console.error('Erro ao buscar detalhes:', error);
      alert('Erro ao carregar detalhes do prontuário');
    }
  };

  const getRecordTypeLabel = (type: string) => {
    const labels = {
      consultation: 'Consulta',
      emergency: 'Emergência',
      followup: 'Retorno',
      telemedicine: 'Telemedicina',
    };
    return labels[type as keyof typeof labels] || type;
  };

  const getRecordTypeBadge = (type: string) => {
    const styles = {
      consultation: 'bg-blue-100 text-blue-800',
      emergency: 'bg-red-100 text-red-800',
      followup: 'bg-green-100 text-green-800',
      telemedicine: 'bg-purple-100 text-purple-800',
    };
    return styles[type as keyof typeof styles] || 'bg-gray-100 text-gray-800';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR');
  };

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString('pt-BR');
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
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold">Prontuários Eletrônicos</h1>
          <p className="text-gray-600 mt-1">{records.length} prontuário(s)</p>
        </div>
        <button
          onClick={handleNew}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition flex items-center gap-2"
        >
          <Plus size={20} />
          Novo Prontuário
        </button>
      </div>

      {/* Lista de Prontuários */}
      <div className="space-y-4">
        {records.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center text-gray-500">
            Nenhum prontuário encontrado
          </div>
        ) : (
          records.map((record) => {
            const patient = patients[record.patient_id];

            return (
              <div key={record.id} className="bg-white rounded-lg shadow p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <FileText className="text-gray-400" size={20} />
                      <h3 className="text-lg font-semibold">
                        {patient?.full_name || 'Paciente não encontrado'}
                      </h3>
                      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getRecordTypeBadge(record.record_type)}`}>
                        {getRecordTypeLabel(record.record_type)}
                      </span>
                      {record.is_completed && (
                        <span className="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                          Finalizado
                        </span>
                      )}
                      {record.is_locked && (
                        <span className="px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">
                          Bloqueado
                        </span>
                      )}
                    </div>

                    <div className="flex items-center gap-6 text-sm text-gray-600 ml-8">
                      <div className="flex items-center gap-2">
                        <Calendar size={16} />
                        <span>{formatDate(record.record_date)}</span>
                      </div>
                      {record.chief_complaint && (
                        <div>
                          <span className="font-medium">Queixa:</span> {record.chief_complaint}
                        </div>
                      )}
                    </div>

                    {record.diagnosis && (
                      <div className="mt-2 ml-8 text-sm">
                        <span className="font-medium text-gray-700">Diagnóstico:</span>{' '}
                        <span className="text-gray-600">{record.diagnosis}</span>
                      </div>
                    )}
                  </div>

                  {/* Ações */}
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleViewDetails(record)}
                      className="px-3 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition flex items-center gap-2"
                      title="Ver detalhes"
                    >
                      <Eye size={16} />
                      Ver Detalhes
                    </button>
                    {!record.is_locked && (
                      <button
                        onClick={() => handleEdit(record)}
                        className="px-3 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition flex items-center gap-2"
                        title="Editar"
                      >
                        <Edit size={16} />
                        Editar
                      </button>
                    )}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Modal de Formulário */}
      {showFormModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg w-full max-w-4xl max-h-[90vh] flex flex-col">
            <div className="sticky top-0 bg-white border-b p-6 flex justify-between items-center">
              <h2 className="text-xl font-bold">
                {editingRecord ? 'Editar Prontuário' : 'Novo Prontuário'}
              </h2>
              <button
                onClick={() => setShowFormModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-6 space-y-4">
              {/* Paciente */}
              <div>
                <label className="block text-sm font-medium mb-1">
                  Paciente *
                </label>
                <select
                  value={formData.patient_id}
                  onChange={(e) => setFormData({...formData, patient_id: e.target.value})}
                  className="w-full border rounded-lg p-2"
                  required
                  disabled={!!editingRecord}
                >
                  <option value="">Selecione um paciente</option>
                  {Object.values(patients).map(patient => (
                    <option key={patient.id} value={patient.id}>
                      {patient.full_name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Queixa Principal */}
              <div>
                <label className="block text-sm font-medium mb-1">Queixa Principal</label>
                <input
                  type="text"
                  value={formData.chief_complaint}
                  onChange={(e) => setFormData({...formData, chief_complaint: e.target.value})}
                  className="w-full border rounded-lg p-2"
                  placeholder="Ex: Dor de cabeça intensa"
                />
              </div>

              {/* História da Doença Atual */}
              <div>
                <label className="block text-sm font-medium mb-1">História da Doença Atual (HDA)</label>
                <textarea
                  value={formData.history_of_present_illness}
                  onChange={(e) => setFormData({...formData, history_of_present_illness: e.target.value})}
                  className="w-full border rounded-lg p-2"
                  rows={3}
                  placeholder="Descreva a história da doença..."
                />
              </div>

              {/* História Pregressa */}
              <div>
                <label className="block text-sm font-medium mb-1">História Patológica Pregressa</label>
                <textarea
                  value={formData.past_medical_history}
                  onChange={(e) => setFormData({...formData, past_medical_history: e.target.value})}
                  className="w-full border rounded-lg p-2"
                  rows={2}
                  placeholder="Doenças anteriores, cirurgias..."
                />
              </div>

              {/* Medicamentos */}
              <div>
                <label className="block text-sm font-medium mb-1">Medicamentos em Uso</label>
                <textarea
                  value={formData.medications}
                  onChange={(e) => setFormData({...formData, medications: e.target.value})}
                  className="w-full border rounded-lg p-2"
                  rows={2}
                  placeholder="Liste os medicamentos em uso..."
                />
              </div>

              {/* Alergias */}
              <div>
                <label className="block text-sm font-medium mb-1">Alergias</label>
                <input
                  type="text"
                  value={formData.allergies}
                  onChange={(e) => setFormData({...formData, allergies: e.target.value})}
                  className="w-full border rounded-lg p-2"
                  placeholder="Ex: Dipirona, Penicilina"
                />
              </div>

              {/* Diagnóstico */}
              <div>
                <label className="block text-sm font-medium mb-1">Diagnóstico</label>
                <input
                  type="text"
                  value={formData.diagnosis}
                  onChange={(e) => setFormData({...formData, diagnosis: e.target.value})}
                  className="w-full border rounded-lg p-2"
                  placeholder="Ex: Enxaqueca com aura"
                />
              </div>

              {/* Plano de Tratamento */}
              <div>
                <label className="block text-sm font-medium mb-1">Plano de Tratamento</label>
                <textarea
                  value={formData.treatment_plan}
                  onChange={(e) => setFormData({...formData, treatment_plan: e.target.value})}
                  className="w-full border rounded-lg p-2"
                  rows={3}
                  placeholder="Descreva o plano de tratamento..."
                />
              </div>

              {/* Prescrições */}
              <div>
                <label className="block text-sm font-medium mb-1">Prescrições</label>
                <textarea
                  value={formData.prescriptions}
                  onChange={(e) => setFormData({...formData, prescriptions: e.target.value})}
                  className="w-full border rounded-lg p-2"
                  rows={3}
                  placeholder="Liste os medicamentos prescritos..."
                />
              </div>

              {/* Exames Solicitados */}
              <div>
                <label className="block text-sm font-medium mb-1">Exames Solicitados</label>
                <textarea
                  value={formData.exams_requested}
                  onChange={(e) => setFormData({...formData, exams_requested: e.target.value})}
                  className="w-full border rounded-lg p-2"
                  rows={2}
                  placeholder="Liste os exames solicitados..."
                />
              </div>

              {/* Observações */}
              <div>
                <label className="block text-sm font-medium mb-1">Observações</label>
                <textarea
                  value={formData.observations}
                  onChange={(e) => setFormData({...formData, observations: e.target.value})}
                  className="w-full border rounded-lg p-2"
                  rows={2}
                  placeholder="Observações adicionais..."
                />
              </div>
            </form>

            <div className="sticky bottom-0 bg-gray-50 border-t p-4 flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setShowFormModal(false)}
                className="px-4 py-2 bg-gray-200 rounded-lg hover:bg-gray-300"
              >
                Cancelar
              </button>
              <button
                onClick={handleSubmit}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                {editingRecord ? 'Salvar Alterações' : 'Criar Prontuário'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Detalhes */}
      {showDetailsModal && selectedRecord && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg w-full max-w-4xl h-[90vh] flex flex-col">
            {/* Header do Modal */}
            <div className="sticky top-0 bg-white border-b p-6 flex justify-between items-center">
              <h2 className="text-xl font-bold">Detalhes do Prontuário</h2>
              <button
                onClick={() => setShowDetailsModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>

            {/* Conteúdo do Modal */}
            <div className="p-6 space-y-6 overflow-y-scroll flex-1" style={{maxHeight: "calc(90vh - 180px)"}}>
              {/* Informações Gerais */}
              <div>
                <h3 className="text-lg font-semibold mb-3 text-blue-600">Informações Gerais</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="font-medium">Paciente:</span>{' '}
                    {patients[selectedRecord.patient_id]?.full_name}
                  </div>
                  <div>
                    <span className="font-medium">Data:</span> {formatDateTime(selectedRecord.record_date)}
                  </div>
                  <div>
                    <span className="font-medium">Tipo:</span> {getRecordTypeLabel(selectedRecord.record_type)}
                  </div>
                  <div>
                    <span className="font-medium">Status:</span>{' '}
                    {selectedRecord.is_completed ? 'Finalizado' : 'Em andamento'}
                  </div>
                </div>
              </div>

              {/* Queixa Principal */}
              {selectedRecord.chief_complaint && (
                <div>
                  <h3 className="text-lg font-semibold mb-2 text-blue-600">Queixa Principal</h3>
                  <p className="text-gray-700 whitespace-pre-wrap">{selectedRecord.chief_complaint}</p>
                </div>
              )}

              {/* História da Doença Atual */}
              {selectedRecord.history_of_present_illness && (
                <div>
                  <h3 className="text-lg font-semibold mb-2 text-blue-600">História da Doença Atual (HDA)</h3>
                  <p className="text-gray-700 whitespace-pre-wrap">{selectedRecord.history_of_present_illness}</p>
                </div>
              )}

              {/* Anamnese */}
              {(selectedRecord.past_medical_history || selectedRecord.medications || selectedRecord.allergies) && (
                <div>
                  <h3 className="text-lg font-semibold mb-3 text-blue-600">Anamnese</h3>
                  <div className="space-y-3">
                    {selectedRecord.past_medical_history && (
                      <div>
                        <span className="font-medium">História Pregressa:</span>
                        <p className="text-gray-700 mt-1 whitespace-pre-wrap">{selectedRecord.past_medical_history}</p>
                      </div>
                    )}
                    {selectedRecord.medications && (
                      <div>
                        <span className="font-medium">Medicamentos em Uso:</span>
                        <p className="text-gray-700 mt-1 whitespace-pre-wrap">{selectedRecord.medications}</p>
                      </div>
                    )}
                    {selectedRecord.allergies && (
                      <div>
                        <span className="font-medium">Alergias:</span>
                        <p className="text-gray-700 mt-1 whitespace-pre-wrap">{selectedRecord.allergies}</p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Diagnóstico */}
              {selectedRecord.diagnosis && (
                <div>
                  <h3 className="text-lg font-semibold mb-2 text-blue-600">Diagnóstico</h3>
                  <p className="text-gray-700 whitespace-pre-wrap">{selectedRecord.diagnosis}</p>
                  {selectedRecord.icd10_codes && (
                    <p className="text-sm text-gray-500 mt-2">CID-10: {selectedRecord.icd10_codes}</p>
                  )}
                </div>
              )}

              {/* Conduta */}
              {(selectedRecord.treatment_plan || selectedRecord.prescriptions || selectedRecord.exams_requested) && (
                <div>
                  <h3 className="text-lg font-semibold mb-3 text-blue-600">Conduta</h3>
                  <div className="space-y-3">
                    {selectedRecord.treatment_plan && (
                      <div>
                        <span className="font-medium">Plano de Tratamento:</span>
                        <p className="text-gray-700 mt-1 whitespace-pre-wrap">{selectedRecord.treatment_plan}</p>
                      </div>
                    )}
                    {selectedRecord.prescriptions && (
                      <div>
                        <span className="font-medium">Prescrições:</span>
                        <p className="text-gray-700 mt-1 whitespace-pre-wrap">{selectedRecord.prescriptions}</p>
                      </div>
                    )}
                    {selectedRecord.exams_requested && (
                      <div>
                        <span className="font-medium">Exames Solicitados:</span>
                        <p className="text-gray-700 mt-1 whitespace-pre-wrap">{selectedRecord.exams_requested}</p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Observações */}
              {selectedRecord.observations && (
                <div>
                  <h3 className="text-lg font-semibold mb-2 text-blue-600">Observações</h3>
                  <p className="text-gray-700 whitespace-pre-wrap">{selectedRecord.observations}</p>
                </div>
              )}

              {/* Retorno */}
              {selectedRecord.followup_date && (
                <div>
                  <h3 className="text-lg font-semibold mb-2 text-blue-600">Retorno</h3>
                  <p className="text-gray-700">
                    <span className="font-medium">Data:</span> {formatDate(selectedRecord.followup_date)}
                  </p>
                  {selectedRecord.followup_notes && (
                    <p className="text-gray-700 mt-2 whitespace-pre-wrap">{selectedRecord.followup_notes}</p>
                  )}
                </div>
              )}
            </div>

            {/* Footer do Modal */}
            <div className="sticky bottom-0 bg-gray-50 border-t p-4 flex justify-end">
              <button
                onClick={() => setShowDetailsModal(false)}
                className="px-4 py-2 bg-gray-200 rounded-lg hover:bg-gray-300"
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
