'use client';

import { useEffect, useState } from 'react';
import { Calendar, Clock, User, Filter, Plus, CheckCircle, XCircle, Play, Check, ArrowLeft } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { appointmentsService, Appointment, AppointmentStatus } from '@/services/appointments.service';
import { patientsService, Patient } from '@/services/patients.service';

export default function AgendaPage() {
  const router = useRouter();
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [patients, setPatients] = useState<Record<string, Patient>>({});
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<AppointmentStatus | ''>('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [showNewModal, setShowNewModal] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const filters: any = {};
      if (statusFilter) filters.status_filter = statusFilter;
      if (dateFrom) filters.date_from = dateFrom;
      if (dateTo) filters.date_to = dateTo;
      
      const appointmentsData = await appointmentsService.list(filters);
      setAppointments(appointmentsData);
      
      const patientsData = await patientsService.list();
      const patientsMap: Record<string, Patient> = {};
      patientsData.forEach(p => patientsMap[p.id] = p);
      setPatients(patientsMap);
    } catch (error) {
      console.error('Erro ao carregar agenda:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleConfirm = async (id: string) => {
    if (!confirm('Confirmar este agendamento?')) return;
    try {
      await appointmentsService.confirm(id, 'whatsapp' as any);
      alert('Agendamento confirmado!');
      loadData();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Erro ao confirmar');
    }
  };

  const handleCancel = async (id: string) => {
    const reason = prompt('Motivo do cancelamento:');
    if (!reason) return;
    try {
      await appointmentsService.cancel(id, reason);
      alert('Agendamento cancelado!');
      loadData();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Erro ao cancelar');
    }
  };

  const handleStart = async (id: string) => {
    if (!confirm('Iniciar atendimento?')) return;
    try {
      await appointmentsService.start(id);
      alert('Atendimento iniciado!');
      loadData();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Erro ao iniciar');
    }
  };

  const handleComplete = async (id: string) => {
    if (!confirm('Finalizar atendimento?')) return;
    try {
      await appointmentsService.complete(id);
      alert('Atendimento finalizado!');
      loadData();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Erro ao finalizar');
    }
  };

  const getStatusBadge = (status: AppointmentStatus) => {
    const styles = {
      scheduled: 'bg-blue-100 text-blue-800',
      confirmed: 'bg-green-100 text-green-800',
      in_progress: 'bg-yellow-100 text-yellow-800',
      completed: 'bg-gray-100 text-gray-800',
      cancelled: 'bg-red-100 text-red-800',
      no_show: 'bg-orange-100 text-orange-800',
    };

    const labels = {
      scheduled: 'Agendado',
      confirmed: 'Confirmado',
      in_progress: 'Em Atendimento',
      completed: 'Concluído',
      cancelled: 'Cancelado',
      no_show: 'Faltou',
    };

    return (
      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${styles[status]}`}>
        {labels[status]}
      </span>
    );
  };

  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString);
    return {
      date: date.toLocaleDateString('pt-BR'),
      time: date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }),
    };
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-96">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="ml-4 text-gray-600">Carregando agenda...</p>
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
          <h1 className="text-2xl font-bold">Agenda</h1>
          <p className="text-gray-600 mt-1">{appointments.length} agendamento(s)</p>
        </div>
        <button onClick={() => setShowNewModal(true)} className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition flex items-center gap-2">
          <Plus size={20} />
          Novo Agendamento
        </button>
      </div>

      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value as any)} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="">Todos</option>
              <option value="scheduled">Agendado</option>
              <option value="confirmed">Confirmado</option>
              <option value="in_progress">Em Atendimento</option>
              <option value="completed">Concluído</option>
              <option value="cancelled">Cancelado</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Data Início</label>
            <input type="date" value={dateFrom} onChange={(e) => setDateFrom(e.target.value)} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Data Fim</label>
            <input type="date" value={dateTo} onChange={(e) => setDateTo(e.target.value)} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div className="flex items-end">
            <button onClick={loadData} className="w-full bg-gray-100 px-4 py-2 rounded-lg hover:bg-gray-200 transition flex items-center justify-center gap-2">
              <Filter size={20} />
              Filtrar
            </button>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        {appointments.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center text-gray-500">Nenhum agendamento encontrado</div>
        ) : (
          appointments.map((appointment) => {
            const { date, time } = formatDateTime(appointment.scheduled_date);
            const patient = patients[appointment.patient_id];
            return (
              <div key={appointment.id} className="bg-white rounded-lg shadow p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <User className="text-gray-400" size={20} />
                      <h3 className="text-lg font-semibold">{patient?.full_name || 'Paciente não encontrado'}</h3>
                      {getStatusBadge(appointment.status)}
                    </div>
                    <div className="flex items-center gap-6 text-sm text-gray-600 ml-8">
                      <div className="flex items-center gap-2">
                        <Calendar size={16} />
                        <span>{date}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Clock size={16} />
                        <span>{time}</span>
                      </div>
                      <div>
                        <span className="font-medium">{appointment.duration_minutes} min</span>
                      </div>
                    </div>
                    {appointment.reason && (
                      <p className="mt-2 ml-8 text-sm text-gray-600">
                        <span className="font-medium">Motivo:</span> {appointment.reason}
                      </p>
                    )}
                  </div>
                  <div className="flex gap-2">
                    {appointment.status === 'scheduled' && (
                      <>
                        <button onClick={() => handleConfirm(appointment.id)} className="px-3 py-2 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition flex items-center gap-2" title="Confirmar">
                          <CheckCircle size={16} />
                          Confirmar
                        </button>
                        <button onClick={() => handleCancel(appointment.id)} className="px-3 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition flex items-center gap-2" title="Cancelar">
                          <XCircle size={16} />
                          Cancelar
                        </button>
                      </>
                    )}
                    {appointment.status === 'confirmed' && (
                      <>
                        <button onClick={() => handleStart(appointment.id)} className="px-3 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition flex items-center gap-2" title="Iniciar">
                          <Play size={16} />
                          Iniciar
                        </button>
                        <button onClick={() => handleCancel(appointment.id)} className="px-3 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition flex items-center gap-2" title="Cancelar">
                          <XCircle size={16} />
                          Cancelar
                        </button>
                      </>
                    )}
                    {appointment.status === 'in_progress' && (
                      <button onClick={() => handleComplete(appointment.id)} className="px-3 py-2 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition flex items-center gap-2" title="Finalizar">
                        <Check size={16} />
                        Finalizar
                      </button>
                    )}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      {showNewModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl p-6 w-full max-w-lg">
            <h2 className="text-2xl font-bold mb-6">Novo Agendamento</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Paciente</label>
                <select className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600">
                  <option value="">Selecione um paciente</option>
                  {Object.values(patients).map(patient => (
                    <option key={patient.id} value={patient.id}>{patient.full_name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Data e Hora</label>
                <input type="datetime-local" className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Duração (minutos)</label>
                <input type="number" defaultValue={30} className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Motivo da Consulta</label>
                <textarea rows={3} className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600" placeholder="Descreva o motivo da consulta..." />
              </div>
            </div>
            <div className="flex gap-2 mt-6">
              <button onClick={() => setShowNewModal(false)} className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">Cancelar</button>
              <button onClick={() => { alert('Funcionalidade de criar agendamento será implementada em breve!'); setShowNewModal(false); }} className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">Agendar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
