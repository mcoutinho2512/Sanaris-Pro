'use client';

import { useEffect, useState } from 'react';
import { Pill, Plus, Eye, FileText, CheckCircle, Trash2, PlusCircle } from 'lucide-react';
import { prescriptionsService, Prescription } from '@/services/prescriptions.service';
import { patientsService, Patient } from '@/services/patients.service';

export default function PrescricoesPage() {
  const [prescriptions, setPrescriptions] = useState<Prescription[]>([]);
  const [patients, setPatients] = useState<Record<string, Patient>>({});
  const [loading, setLoading] = useState(true);
  const [showFormModal, setShowFormModal] = useState(false);
  const [formData, setFormData] = useState({
    patient_id: '',
    general_instructions: '',
  });
  const [medications, setMedications] = useState([{
    medication_name: '',
    concentration: '',
    dosage: '',
    frequency: '',
    duration: '',
    quantity: 0,
    instructions: '',
    is_generic: true,
  }]);
  const [editingPrescription, setEditingPrescription] = useState<Prescription | null>(null);
  const [selectedPrescription, setSelectedPrescription] = useState<Prescription | null>(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const handleView = async (prescription: Prescription) => {
    try {
      // Buscar detalhes completos
      const fullPrescription = await prescriptionsService.get(prescription.id);
      setSelectedPrescription(fullPrescription);
      setShowDetailsModal(true);
    } catch (error) {
      console.error('Erro ao buscar prescrição:', error);
      alert('Erro ao carregar prescrição');
    }
  };

  const handleEdit = async (prescription: Prescription) => {
    try {
      // Buscar detalhes completos
      const fullPrescription = await prescriptionsService.get(prescription.id);
      
      setEditingPrescription(fullPrescription);
      setFormData({
        patient_id: fullPrescription.patient_id,
        general_instructions: fullPrescription.general_instructions || '',
      });
      
      // Carregar medicamentos
      const loadedMeds = fullPrescription.items.map(item => ({
        medication_name: item.medication_name,
        concentration: item.concentration || '',
        dosage: item.dosage,
        frequency: item.frequency,
        duration: item.duration || '',
        quantity: item.quantity || 0,
        instructions: item.instructions || '',
        is_generic: item.is_generic,
      }));
      
      setMedications(loadedMeds.length > 0 ? loadedMeds : [{
        medication_name: '',
        concentration: '',
        dosage: '',
        frequency: '',
        duration: '',
        quantity: 0,
        instructions: '',
        is_generic: true,
      }]);
      
      setShowFormModal(true);
    } catch (error) {
      console.error('Erro ao buscar prescrição:', error);
      alert('Erro ao carregar prescrição');
    }
  };

  const handleNew = () => {
    setEditingPrescription(null);
    setFormData({
      patient_id: '',
      general_instructions: '',
    });
    setMedications([{
      medication_name: '',
      concentration: '',
      dosage: '',
      frequency: '',
      duration: '',
      quantity: 0,
      instructions: '',
      is_generic: true,
    }]);
    setShowFormModal(true);
  };

  const addMedication = () => {
    setMedications([...medications, {
      medication_name: '',
      concentration: '',
      dosage: '',
      frequency: '',
      duration: '',
      quantity: 0,
      instructions: '',
      is_generic: true,
    }]);
  };

  const removeMedication = (index: number) => {
    setMedications(medications.filter((_, i) => i !== index));
  };

  const updateMedication = (index: number, field: string, value: any) => {
    const newMeds = [...medications];
    (newMeds[index] as any)[field] = value;
    setMedications(newMeds);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.patient_id) {
      alert('Selecione um paciente');
      return;
    }

    if (medications.length === 0 || !medications[0].medication_name) {
      alert('Adicione pelo menos um medicamento');
      return;
    }

    try {
      if (editingPrescription) {
        // Atualizar (apenas instruções gerais - medicamentos não podem ser editados após criação)
        await prescriptionsService.update(editingPrescription.id, {
          general_instructions: formData.general_instructions,
        });
        alert('Prescrição atualizada com sucesso!');
      } else {
        // Criar nova
        await prescriptionsService.create({
        ...formData,
        healthcare_professional_id: 'doctor-001',
        crm_number: '12345-RJ',
        crm_state: 'RJ',
        items: medications.map((med, idx) => ({
          ...med,
          pharmaceutical_form: 'comprimido',
          route_of_administration: 'oral',
          quantity_unit: 'unidades',
          is_controlled: false,
          display_order: idx,
        })),
      });
      
        alert('Prescrição criada com sucesso!');
      }
      
      setShowFormModal(false);
      setEditingPrescription(null);
      loadData();
    } catch (error: any) {
      console.error('Erro ao criar:', error);
      alert(error.response?.data?.detail || 'Erro ao criar prescrição');
    }
  };

  const loadData = async () => {
    try {
      setLoading(true);
      
      // Carregar prescrições
      const prescriptionsData = await prescriptionsService.list({ limit: 50 });
      setPrescriptions(prescriptionsData);
      
      // Carregar pacientes
      const patientsData = await patientsService.list();
      const patientsMap: Record<string, Patient> = {};
      patientsData.forEach(p => patientsMap[p.id] = p);
      setPatients(patientsMap);
      
    } catch (error) {
      console.error('Erro ao carregar prescrições:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR');
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
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold">Prescrições Digitais</h1>
          <p className="text-gray-600 mt-1">{prescriptions.length} prescrição(ões)</p>
        </div>
        <button
          onClick={handleNew}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition flex items-center gap-2"
        >
          <Plus size={20} />
          Nova Prescrição
        </button>
      </div>

      {/* Modal de Detalhes */}
      {showDetailsModal && selectedPrescription && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg w-full max-w-4xl h-[90vh] flex flex-col">
            {/* Header */}
            <div className="sticky top-0 bg-white border-b p-6 flex justify-between items-center">
              <h2 className="text-xl font-bold">Prescrição Médica</h2>
              <button
                onClick={() => setShowDetailsModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>

            {/* Conteúdo */}
            <div className="p-6 space-y-6 overflow-y-scroll flex-1" style={{maxHeight: "calc(90vh - 180px)"}}>
              {/* Informações do Paciente */}
              <div>
                <h3 className="text-lg font-semibold mb-3 text-blue-600">Paciente</h3>
                <p className="text-gray-700 font-medium">
                  {patients[selectedPrescription.patient_id]?.full_name || 'Não encontrado'}
                </p>
              </div>

              {/* Informações da Prescrição */}
              <div>
                <h3 className="text-lg font-semibold mb-3 text-blue-600">Dados da Prescrição</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium">Data:</span>{' '}
                    {formatDate(selectedPrescription.prescription_date)}
                  </div>
                  {selectedPrescription.valid_until && (
                    <div>
                      <span className="font-medium">Válida até:</span>{' '}
                      {formatDate(selectedPrescription.valid_until)}
                    </div>
                  )}
                  {selectedPrescription.crm_number && (
                    <div>
                      <span className="font-medium">CRM:</span>{' '}
                      {selectedPrescription.crm_number}-{selectedPrescription.crm_state}
                    </div>
                  )}
                </div>
              </div>

              {/* Medicamentos */}
              <div>
                <h3 className="text-lg font-semibold mb-3 text-blue-600">Medicamentos Prescritos</h3>
                <div className="space-y-4">
                  {selectedPrescription.items.map((item, index) => (
                    <div key={item.id || index} className="border-l-4 border-blue-400 pl-4 py-2 bg-blue-50 rounded">
                      <div className="font-semibold text-gray-900 mb-2">
                        {index + 1}. {item.medication_name}
                        {item.concentration && ` - ${item.concentration}`}
                      </div>
                      
                      <div className="text-sm space-y-1 text-gray-700">
                        {item.pharmaceutical_form && (
                          <div><span className="font-medium">Forma:</span> {item.pharmaceutical_form}</div>
                        )}
                        
                        <div><span className="font-medium">Posologia:</span> {item.dosage}</div>
                        <div><span className="font-medium">Frequência:</span> {item.frequency}</div>
                        
                        {item.duration && (
                          <div><span className="font-medium">Duração:</span> {item.duration}</div>
                        )}
                        
                        {item.route_of_administration && (
                          <div><span className="font-medium">Via:</span> {item.route_of_administration}</div>
                        )}
                        
                        {item.quantity && (
                          <div>
                            <span className="font-medium">Quantidade:</span> {item.quantity} {item.quantity_unit || 'unidades'}
                          </div>
                        )}
                        
                        {item.instructions && (
                          <div className="mt-2 p-2 bg-yellow-50 border border-yellow-200 rounded">
                            <span className="font-medium">⚠️ Instruções:</span> {item.instructions}
                          </div>
                        )}
                        
                        {item.is_generic && (
                          <div className="text-green-600 text-xs mt-1">✓ Aceita genérico</div>
                        )}
                        
                        {item.is_controlled && (
                          <div className="text-red-600 text-xs mt-1">🔒 Medicamento controlado</div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Instruções Gerais */}
              {selectedPrescription.general_instructions && (
                <div>
                  <h3 className="text-lg font-semibold mb-2 text-blue-600">Instruções Gerais</h3>
                  <p className="text-gray-700 whitespace-pre-wrap bg-gray-50 p-4 rounded">
                    {selectedPrescription.general_instructions}
                  </p>
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="sticky bottom-0 bg-gray-50 border-t p-4 flex justify-end gap-2">
              <button
                onClick={() => setShowDetailsModal(false)}
                className="px-4 py-2 bg-gray-200 rounded-lg hover:bg-gray-300"
              >
                Fechar
              </button>
              {selectedPrescription.is_signed && (
                <button
                  onClick={() => alert('Impressão em desenvolvimento')}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Imprimir
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Modal de Formulário */}
      {showFormModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg w-full max-w-5xl max-h-[90vh] flex flex-col">
            <div className="sticky top-0 bg-white border-b p-6 flex justify-between items-center">
              <h2 className="text-xl font-bold">{editingPrescription ? 'Editar Prescrição' : 'Nova Prescrição'}</h2>
              <button
                onClick={() => setShowFormModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-6 space-y-6">
              {/* Paciente */}
              <div>
                <label className="block text-sm font-medium mb-1">Paciente *</label>
                <select
                  value={formData.patient_id}
                  onChange={(e) => setFormData({...formData, patient_id: e.target.value})}
                  className="w-full border rounded-lg p-2"
                  required
                  disabled={!!editingPrescription}
                >
                  <option value="">Selecione um paciente</option>
                  {Object.values(patients).map(patient => (
                    <option key={patient.id} value={patient.id}>
                      {patient.full_name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Medicamentos */}
              <div>
                <div className="flex justify-between items-center mb-3">
                  <h3 className="text-lg font-semibold text-blue-600">Medicamentos</h3>
                  {editingPrescription && (
                    <span className="text-xs text-gray-500 italic">
                      ⓘ Medicamentos não podem ser editados após criação
                    </span>
                  )}
                  <button
                    type="button"
                    onClick={addMedication}
                    className="flex items-center gap-2 px-3 py-1 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 text-sm"
                  >
                    <PlusCircle size={16} />
                    Adicionar Medicamento
                  </button>
                </div>

                <div className="space-y-4">
                  {medications.map((med, index) => (
                    <div key={index} className="border border-blue-200 rounded-lg p-4 bg-blue-50 relative">
                      {medications.length > 1 && (
                        <button
                          type="button"
                          onClick={() => removeMedication(index)}
                          className="absolute top-2 right-2 text-red-500 hover:text-red-700"
                          title="Remover medicamento"
                        >
                          <Trash2 size={18} />
                        </button>
                      )}

                      <div className="font-semibold mb-3 text-gray-700">
                        Medicamento {index + 1}
                      </div>

                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <label className="block text-xs font-medium mb-1">Nome do Medicamento *</label>
                          <input
                            type="text"
                            value={med.medication_name}
                            onChange={(e) => updateMedication(index, 'medication_name', e.target.value)}
                            className="w-full border rounded p-2 text-sm"
                            placeholder="Ex: Paracetamol"
                            required
                            disabled={!!editingPrescription}
                          />
                        </div>

                        <div>
                          <label className="block text-xs font-medium mb-1">Concentração</label>
                          <input
                            type="text"
                            value={med.concentration}
                            onChange={(e) => updateMedication(index, 'concentration', e.target.value)}
                            className="w-full border rounded p-2 text-sm"
                            placeholder="Ex: 750mg"
                          />
                        </div>

                        <div>
                          <label className="block text-xs font-medium mb-1">Posologia *</label>
                          <input
                            type="text"
                            value={med.dosage}
                            onChange={(e) => updateMedication(index, 'dosage', e.target.value)}
                            className="w-full border rounded p-2 text-sm"
                            placeholder="Ex: 1 comprimido"
                            required
                          />
                        </div>

                        <div>
                          <label className="block text-xs font-medium mb-1">Frequência *</label>
                          <input
                            type="text"
                            value={med.frequency}
                            onChange={(e) => updateMedication(index, 'frequency', e.target.value)}
                            className="w-full border rounded p-2 text-sm"
                            placeholder="Ex: de 8 em 8 horas"
                            required
                          />
                        </div>

                        <div>
                          <label className="block text-xs font-medium mb-1">Duração</label>
                          <input
                            type="text"
                            value={med.duration}
                            onChange={(e) => updateMedication(index, 'duration', e.target.value)}
                            className="w-full border rounded p-2 text-sm"
                            placeholder="Ex: por 7 dias"
                          />
                        </div>

                        <div>
                          <label className="block text-xs font-medium mb-1">Quantidade</label>
                          <input
                            type="number"
                            value={med.quantity}
                            onChange={(e) => updateMedication(index, 'quantity', parseInt(e.target.value) || 0)}
                            className="w-full border rounded p-2 text-sm"
                            placeholder="Ex: 21"
                          />
                        </div>
                      </div>

                      <div className="mt-3">
                        <label className="block text-xs font-medium mb-1">Instruções Específicas</label>
                        <textarea
                          value={med.instructions}
                          onChange={(e) => updateMedication(index, 'instructions', e.target.value)}
                          className="w-full border rounded p-2 text-sm"
                          rows={2}
                          placeholder="Ex: Tomar após as refeições"
                        />
                      </div>

                      <div className="mt-2">
                        <label className="flex items-center gap-2 text-sm">
                          <input
                            type="checkbox"
                            checked={med.is_generic}
                            onChange={(e) => updateMedication(index, 'is_generic', e.target.checked)}
                          />
                          Aceita genérico
                        </label>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Instruções Gerais */}
              <div>
                <label className="block text-sm font-medium mb-1">Instruções Gerais</label>
                <textarea
                  value={formData.general_instructions}
                  onChange={(e) => setFormData({...formData, general_instructions: e.target.value})}
                  className="w-full border rounded-lg p-2"
                  rows={3}
                  placeholder="Instruções gerais para o paciente..."
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
                {editingPrescription ? 'Salvar Alterações' : 'Criar Prescrição'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Lista de Prescrições */}
      <div className="space-y-4">
        {prescriptions.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center text-gray-500">
            Nenhuma prescrição encontrada
          </div>
        ) : (
          prescriptions.map((prescription) => {
            const patient = patients[prescription.patient_id];
            const itemsCount = (prescription as any).items_count || prescription.items?.length || 0;

            return (
              <div key={prescription.id} className="bg-white rounded-lg shadow p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <Pill className="text-gray-400" size={20} />
                      <h3 className="text-lg font-semibold">
                        {patient?.full_name || 'Paciente não encontrado'}
                      </h3>
                      {prescription.is_signed && (
                        <span className="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800 flex items-center gap-1">
                          <CheckCircle size={14} />
                          Assinada
                        </span>
                      )}
                      {prescription.is_printed && (
                        <span className="px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                          Impressa
                        </span>
                      )}
                      {prescription.is_dispensed && (
                        <span className="px-2 py-1 text-xs font-semibold rounded-full bg-purple-100 text-purple-800">
                          Dispensada
                        </span>
                      )}
                    </div>

                    <div className="flex items-center gap-6 text-sm text-gray-600 ml-8">
                      <div>
                        <span className="font-medium">Data:</span> {formatDate(prescription.prescription_date)}
                      </div>
                      <div>
                        <span className="font-medium">Medicamentos:</span> {itemsCount}
                      </div>
                      {prescription.valid_until && (
                        <div>
                          <span className="font-medium">Válida até:</span> {formatDate(prescription.valid_until)}
                        </div>
                      )}
                    </div>

                    {prescription.general_instructions && (
                      <div className="mt-2 ml-8 text-sm text-gray-600">
                        <span className="font-medium">Instruções:</span> {prescription.general_instructions}
                      </div>
                    )}
                  </div>

                  {/* Ações */}
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleView(prescription)}
                      className="px-3 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition flex items-center gap-2"
                      title="Ver prescrição"
                    >
                      <Eye size={16} />
                      Ver
                    </button>
                    {!prescription.is_signed && (
                      <button
                        onClick={() => handleEdit(prescription)}
                        className="px-3 py-2 bg-yellow-100 text-yellow-700 rounded-lg hover:bg-yellow-200 transition"
                        title="Editar prescrição"
                      >
                        Editar
                      </button>
                    )}
                    {prescription.is_signed && (
                      <button
                        onClick={() => alert('Impressão em desenvolvimento')}
                        className="px-3 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition flex items-center gap-2"
                        title="Imprimir"
                      >
                        <FileText size={16} />
                        Imprimir
                      </button>
                    )}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
