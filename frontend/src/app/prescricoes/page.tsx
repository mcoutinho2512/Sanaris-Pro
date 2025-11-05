'use client';

import { useEffect, useState } from 'react';
import { Pill, Plus, Eye, FileText, CheckCircle } from 'lucide-react';
import { prescriptionsService, Prescription } from '@/services/prescriptions.service';
import { patientsService, Patient } from '@/services/patients.service';

export default function PrescricoesPage() {
  const [prescriptions, setPrescriptions] = useState<Prescription[]>([]);
  const [patients, setPatients] = useState<Record<string, Patient>>({});
  const [loading, setLoading] = useState(true);
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
          onClick={() => alert('Formulário de nova prescrição em desenvolvimento')}
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
