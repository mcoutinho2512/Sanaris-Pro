'use client';

import { useState, useEffect, useCallback } from 'react';
import { Calendar, momentLocalizer, View } from 'react-big-calendar';
import moment from 'moment';
import 'moment/locale/pt-br';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import './calendar.css';
import { Plus, User, Clock, X, Check } from 'lucide-react';

moment.locale('pt-br');
const localizer = momentLocalizer(moment);

interface Professional {
  id: string;
  full_name: string;
  job_title_name: string | null;
}

interface Patient {
  id: string;
  full_name: string;
}

interface Appointment {
  id: string;
  patient_id: string;
  healthcare_professional_id: string;
  scheduled_date: string;
  duration_minutes: number;
  status: string;
  appointment_type: string | null;
}

interface CalendarEvent {
  id: string;
  title: string;
  start: Date;
  end: Date;
  resource: Appointment & { 
    patient_name?: string;
    professional_name?: string;
    professional_color?: string;
  };
}

// Cores para cada profissional
const PROFESSIONAL_COLORS = [
  '#3b82f6', // blue
  '#10b981', // green
  '#f59e0b', // amber
  '#8b5cf6', // purple
  '#ef4444', // red
  '#06b6d4', // cyan
  '#f97316', // orange
  '#84cc16', // lime
];

export default function AgendaPage() {
  const [professionals, setProfessionals] = useState<Professional[]>([]);
  const [selectedProfessional, setSelectedProfessional] = useState<string>('all');
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [patients, setPatients] = useState<Patient[]>([]);
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [view, setView] = useState<View>('week');
  const [date, setDate] = useState(new Date());
  const [loading, setLoading] = useState(true);
  const [showNewAppointmentModal, setShowNewAppointmentModal] = useState(false);
  const [formData, setFormData] = useState({
    patient_id: '',
    healthcare_professional_id: '',
    scheduled_date: '',
    scheduled_time: '',
    duration_minutes: '30',
    appointment_type: 'first_time',
    notes: ''
  });
  const [showNewPatientForm, setShowNewPatientForm] = useState(false);
  const [newPatientData, setNewPatientData] = useState({
    full_name: '',
    cpf: '',
    phone: '',
    email: ''
  });
  const [professionalColors, setProfessionalColors] = useState<Map<string, string>>(new Map());

  useEffect(() => {
    loadInitialData();
  }, []);

  useEffect(() => {
    if (professionals.length > 0) {
      // Atribuir cores aos profissionais
      const colorMap = new Map<string, string>();
      professionals.forEach((prof, index) => {
        colorMap.set(prof.id, PROFESSIONAL_COLORS[index % PROFESSIONAL_COLORS.length]);
      });
      setProfessionalColors(colorMap);
    }
  }, [professionals]);

  useEffect(() => {
    if (professionals.length > 0 && patients.length > 0) {
      loadAppointments();
    }
  }, [selectedProfessional, date, professionals, patients]);

  const loadInitialData = async () => {
    await Promise.all([
      loadProfessionals(),
      loadPatients()
    ]);
  };

  const loadProfessionals = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8888/api/v1/users-management/users', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        
        // Filtrar usuários com cargo de profissional de saúde
        const healthProfessionals = data.filter((user: Professional) => 
          user.job_title_name && 
          (user.job_title_name.includes('Médico') || 
           user.job_title_name.includes('Enfermeiro') ||
           user.job_title_name.includes('Psicólogo') ||
           user.job_title_name.includes('Fisioterapeuta') ||
           user.job_title_name.includes('Dentista') ||
           user.job_title_name.includes('Nutricionista'))
        );
        
        setProfessionals(healthProfessionals);
      }
    } catch (error) {
      console.error('Erro ao carregar profissionais:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadPatients = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8888/api/v1/patients', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setPatients(data);
      }
    } catch (error) {
      console.error('Erro ao carregar pacientes:', error);
    }
  };

  const loadAppointments = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8888/api/v1/appointments', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        
        // Filtrar por profissional selecionado
        const filteredAppointments = selectedProfessional === 'all' 
          ? data.filter((apt: Appointment) => 
              professionals.some(p => p.id === apt.healthcare_professional_id)
            )
          : data.filter((apt: Appointment) => 
              apt.healthcare_professional_id === selectedProfessional
            );
        
        setAppointments(filteredAppointments);
        
        // Converter para eventos do calendário
        const calendarEvents: CalendarEvent[] = filteredAppointments.map((apt: Appointment) => {
          const start = new Date(apt.scheduled_date);
          const end = new Date(start.getTime() + apt.duration_minutes * 60000);
          
          const patient = patients.find(p => p.id === apt.patient_id);
          const professional = professionals.find(p => p.id === apt.healthcare_professional_id);
          const professionalColor = professionalColors.get(apt.healthcare_professional_id) || '#3b82f6';
          
          return {
            id: apt.id,
            title: patient ? patient.full_name : 'Paciente',
            start,
            end,
            resource: {
              ...apt,
              patient_name: patient?.full_name,
              professional_name: professional?.full_name,
              professional_color: professionalColor
            }
          };
        });
        
        setEvents(calendarEvents);
      }
    } catch (error) {
      console.error('Erro ao carregar consultas:', error);
    }
  };

  const handleSelectSlot = useCallback(
    ({ start, end }: { start: Date; end: Date }) => {
      console.log('Slot selecionado:', start, end);
      // Pré-preencher data e hora ao clicar no calendário
      const selectedDate = start; // Usar 'start' em vez de 'slotInfo.start'
      const dateStr = selectedDate.toISOString().split('T')[0];
      const timeStr = selectedDate.toTimeString().slice(0, 5);
      
      setFormData(prev => ({
        ...prev,
        scheduled_date: dateStr,
        scheduled_time: timeStr
      }));
      
      setShowNewAppointmentModal(true);
    },
    []
  );

  const handleSelectEvent = useCallback((event: CalendarEvent) => {
    const professional = professionals.find(p => p.id === event.resource.healthcare_professional_id);
    alert(
      `Paciente: ${event.title}\n` +
      `Profissional: ${professional?.full_name || 'Não definido'}\n` +
      `Status: ${event.resource.status}\n` +
      `Horário: ${moment(event.start).format('DD/MM/YYYY HH:mm')}`
    );
  }, [professionals]);

  const eventStyleGetter = (event: CalendarEvent) => {
    let backgroundColor = event.resource.professional_color || '#3b82f6';
    
    // Ajustar opacidade baseado no status
    let opacity = 0.8;
    switch (event.resource.status) {
      case 'cancelled':
        opacity = 0.4;
        backgroundColor = '#ef4444';
        break;
      case 'completed':
        opacity = 0.6;
        break;
    }
    
    return {
      style: {
        backgroundColor,
        borderRadius: '5px',
        opacity,
        color: 'white',
        border: '0px',
        display: 'block'
      }
    };
  };

  const messages = {
    allDay: 'Dia inteiro',
    previous: 'Anterior',
    next: 'Próximo',
    today: 'Hoje',
    month: 'Mês',
    week: 'Semana',
    day: 'Dia',
    agenda: 'Agenda',
    date: 'Data',
    time: 'Hora',
    event: 'Evento',
    noEventsInRange: 'Não há consultas neste período.',
    showMore: (total: number) => `+ Ver mais (${total})`
  };

  if (loading) {
  

  const handleQuickPatientCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8888/api/v1/patients/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(newPatientData)
      });

      if (response.ok) {
        const patient = await response.json();
        alert('Paciente cadastrado com sucesso!');
        
        // Recarregar lista de pacientes
        await loadPatients();
        
        // Selecionar o novo paciente no formulário
        setFormData(prev => ({ ...prev, patient_id: patient.id }));
        
        // Fechar formulário de novo paciente
        setShowNewPatientForm(false);
        setNewPatientData({ full_name: '', cpf: '', phone: '', email: '' });
      } else {
        const error = await response.json();
        alert(`Erro: ${error.detail || 'Não foi possível cadastrar'}`);
      }
    } catch (error) {
      console.error('Erro ao cadastrar paciente:', error);
      alert('Erro ao conectar com o servidor');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const scheduledDateTime = new Date(`${formData.scheduled_date}T${formData.scheduled_time}`);
    
    const appointmentData = {
      patient_id: formData.patient_id,
      healthcare_professional_id: formData.healthcare_professional_id,
      scheduled_date: scheduledDateTime.toISOString(),
      duration_minutes: parseInt(formData.duration_minutes),
      appointment_type: formData.appointment_type,
      notes: formData.notes,
      status: 'scheduled'
    };

    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8888/api/v1/appointments/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(appointmentData)
      });

      if (response.ok) {
        alert('Consulta agendada com sucesso!');
        setShowNewAppointmentModal(false);
        loadAppointments();
        setFormData({
          patient_id: '',
          healthcare_professional_id: '',
          scheduled_date: '',
          scheduled_time: '',
          duration_minutes: '30',
          appointment_type: 'first_time',
          notes: ''
        });
      } else {
        const error = await response.json();
        alert(`Erro: ${error.detail || 'Não foi possível agendar'}`);
      }
    } catch (error) {
      console.error('Erro ao agendar:', error);
      alert('Erro ao conectar com o servidor');
    }
  };

  return (
      <div className="p-6 flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p>Carregando agenda...</p>
        </div>
      </div>
    );
  }

  if (professionals.length === 0) {
  

  const handleQuickPatientCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8888/api/v1/patients/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(newPatientData)
      });

      if (response.ok) {
        const patient = await response.json();
        alert('Paciente cadastrado com sucesso!');
        
        // Recarregar lista de pacientes
        await loadPatients();
        
        // Selecionar o novo paciente no formulário
        setFormData(prev => ({ ...prev, patient_id: patient.id }));
        
        // Fechar formulário de novo paciente
        setShowNewPatientForm(false);
        setNewPatientData({ full_name: '', cpf: '', phone: '', email: '' });
      } else {
        const error = await response.json();
        alert(`Erro: ${error.detail || 'Não foi possível cadastrar'}`);
      }
    } catch (error) {
      console.error('Erro ao cadastrar paciente:', error);
      alert('Erro ao conectar com o servidor');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const scheduledDateTime = new Date(`${formData.scheduled_date}T${formData.scheduled_time}`);
    
    const appointmentData = {
      patient_id: formData.patient_id,
      healthcare_professional_id: formData.healthcare_professional_id,
      scheduled_date: scheduledDateTime.toISOString(),
      duration_minutes: parseInt(formData.duration_minutes),
      appointment_type: formData.appointment_type,
      notes: formData.notes,
      status: 'scheduled'
    };

    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8888/api/v1/appointments/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(appointmentData)
      });

      if (response.ok) {
        alert('Consulta agendada com sucesso!');
        setShowNewAppointmentModal(false);
        loadAppointments();
        setFormData({
          patient_id: '',
          healthcare_professional_id: '',
          scheduled_date: '',
          scheduled_time: '',
          duration_minutes: '30',
          appointment_type: 'first_time',
          notes: ''
        });
      } else {
        const error = await response.json();
        alert(`Erro: ${error.detail || 'Não foi possível agendar'}`);
      }
    } catch (error) {
      console.error('Erro ao agendar:', error);
      alert('Erro ao conectar com o servidor');
    }
  };

  return (
      <div className="p-6">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <h2 className="text-lg font-semibold text-yellow-800 mb-2">Nenhum profissional encontrado</h2>
          <p className="text-yellow-700">
            É necessário ter usuários com cargos de profissionais de saúde cadastrados.
            Vá em <a href="/usuarios" className="underline font-semibold">Gerenciamento de Usuários</a> e 
            atribua cargos aos profissionais.
          </p>
        </div>
      </div>
    );
  }



  const handleQuickPatientCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8888/api/v1/patients/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(newPatientData)
      });

      if (response.ok) {
        const patient = await response.json();
        alert('Paciente cadastrado com sucesso!');
        
        // Recarregar lista de pacientes
        await loadPatients();
        
        // Selecionar o novo paciente no formulário
        setFormData(prev => ({ ...prev, patient_id: patient.id }));
        
        // Fechar formulário de novo paciente
        setShowNewPatientForm(false);
        setNewPatientData({ full_name: '', cpf: '', phone: '', email: '' });
      } else {
        const error = await response.json();
        alert(`Erro: ${error.detail || 'Não foi possível cadastrar'}`);
      }
    } catch (error) {
      console.error('Erro ao cadastrar paciente:', error);
      alert('Erro ao conectar com o servidor');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const scheduledDateTime = new Date(`${formData.scheduled_date}T${formData.scheduled_time}`);
    
    const appointmentData = {
      patient_id: formData.patient_id,
      healthcare_professional_id: formData.healthcare_professional_id,
      scheduled_date: scheduledDateTime.toISOString(),
      duration_minutes: parseInt(formData.duration_minutes),
      appointment_type: formData.appointment_type,
      notes: formData.notes,
      status: 'scheduled'
    };

    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8888/api/v1/appointments/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(appointmentData)
      });

      if (response.ok) {
        alert('Consulta agendada com sucesso!');
        setShowNewAppointmentModal(false);
        loadAppointments();
        setFormData({
          patient_id: '',
          healthcare_professional_id: '',
          scheduled_date: '',
          scheduled_time: '',
          duration_minutes: '30',
          appointment_type: 'first_time',
          notes: ''
        });
      } else {
        const error = await response.json();
        alert(`Erro: ${error.detail || 'Não foi possível agendar'}`);
      }
    } catch (error) {
      console.error('Erro ao agendar:', error);
      alert('Erro ao conectar com o servidor');
    }
  };

  return (
    <div className="p-6 h-screen flex flex-col">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Agenda de Consultas</h1>
        <button 
          onClick={() => setShowNewAppointmentModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <Plus className="w-5 h-5" />
          Nova Consulta
        </button>
      </div>

      {/* Filtro por Profissional */}
      <div className="mb-4">
        <label className="block text-sm font-medium mb-2">Profissional:</label>
        <select
          value={selectedProfessional}
          onChange={(e) => setSelectedProfessional(e.target.value)}
          className="px-4 py-2 border rounded-lg w-full max-w-md bg-white"
        >
          <option value="all">📋 Todos os Profissionais</option>
          {professionals.map((prof) => (
            <option key={prof.id} value={prof.id}>
              👨‍⚕️ {prof.full_name} {prof.job_title_name ? `- ${prof.job_title_name}` : ''}
            </option>
          ))}
        </select>
      </div>

      {/* Legenda de Profissionais (quando "Todos" estiver selecionado) */}
      {selectedProfessional === 'all' && professionals.length > 1 && (
        <div className="mb-4 p-3 bg-gray-50 rounded-lg">
          <p className="text-sm font-medium mb-2">Legenda de Profissionais:</p>
          <div className="flex flex-wrap gap-3">
            {professionals.map((prof) => (
              <div key={prof.id} className="flex items-center gap-2">
                <div 
                  className="w-4 h-4 rounded"
                  style={{ backgroundColor: professionalColors.get(prof.id) || '#3b82f6' }}
                ></div>
                <span className="text-sm">{prof.full_name}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Legenda de Status */}
      <div className="flex gap-4 mb-4 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-blue-500 rounded opacity-80"></div>
          <span>Agendada</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-green-500 rounded opacity-80"></div>
          <span>Confirmada</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-purple-500 rounded opacity-60"></div>
          <span>Concluída</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-red-500 rounded opacity-40"></div>
          <span>Cancelada</span>
        </div>
      </div>

      {/* Calendário */}
      <div className="flex-1 bg-white rounded-lg shadow p-4">
        <Calendar
          localizer={localizer}
          events={events}
          startAccessor="start"
          endAccessor="end"
          style={{ height: '100%' }}
          view={view}
          onView={setView}
          date={date}
          onNavigate={setDate}
          onSelectSlot={handleSelectSlot}
          onSelectEvent={handleSelectEvent}
          eventPropGetter={eventStyleGetter}
          selectable
          messages={messages}
          step={30}
          timeslots={1}
          min={new Date(2025, 0, 1, 8, 0, 0)}
          max={new Date(2025, 0, 1, 18, 0, 0)}
        />
      </div>

      {/* Modal Nova Consulta */}
      {showNewAppointmentModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900">Nova Consulta</h2>
              <button
                onClick={() => setShowNewAppointmentModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Paciente */}
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Paciente *
                  </label>
                  <div className="flex gap-2">
                    <select
                      required={!showNewPatientForm}
                      value={formData.patient_id}
                      onChange={(e) => setFormData({ ...formData, patient_id: e.target.value })}
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      disabled={showNewPatientForm}
                    >
                      <option value="">Selecione o paciente</option>
                      {patients.map((patient) => (
                        <option key={patient.id} value={patient.id}>
                          {patient.full_name}
                        </option>
                      ))}
                    </select>
                    <button
                      type="button"
                      onClick={() => setShowNewPatientForm(!showNewPatientForm)}
                      className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2"
                    >
                      <Plus className="w-4 h-4" />
                      {showNewPatientForm ? 'Cancelar' : 'Novo'}
                    </button>
                  </div>
                  
                  {/* Formulário de cadastro rápido */}
                  {showNewPatientForm && (
                    <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
                      <h4 className="font-medium text-gray-900 mb-3">Cadastro Rápido de Paciente</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Nome Completo *
                          </label>
                          <input
                            type="text"
                            required={showNewPatientForm}
                            value={newPatientData.full_name}
                            onChange={(e) => setNewPatientData({ ...newPatientData, full_name: e.target.value })}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                            placeholder="Nome completo do paciente"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            CPF *
                          </label>
                          <input
                            type="text"
                            required={showNewPatientForm}
                            value={newPatientData.cpf}
                            onChange={(e) => setNewPatientData({ ...newPatientData, cpf: e.target.value })}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                            placeholder="000.000.000-00"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Telefone *
                          </label>
                          <input
                            type="tel"
                            required={showNewPatientForm}
                            value={newPatientData.phone}
                            onChange={(e) => setNewPatientData({ ...newPatientData, phone: e.target.value })}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                            placeholder="(00) 00000-0000"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            E-mail
                          </label>
                          <input
                            type="email"
                            value={newPatientData.email}
                            onChange={(e) => setNewPatientData({ ...newPatientData, email: e.target.value })}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                            placeholder="email@exemplo.com"
                          />
                        </div>
                      </div>
                      <button
                        type="button"
                        onClick={handleQuickPatientCreate}
                        className="mt-3 w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                      >
                        Cadastrar e Selecionar
                      </button>
                    </div>
                  )}
                </div>

                {/* Profissional */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Profissional *
                  </label>
                  <select
                    required
                    value={formData.healthcare_professional_id}
                    onChange={(e) => setFormData({ ...formData, healthcare_professional_id: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Selecione o profissional</option>
                    {professionals.map((prof) => (
                      <option key={prof.id} value={prof.id}>
                        {prof.full_name} {prof.job_title_name ? `- ${prof.job_title_name}` : ''}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Data */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Data *
                  </label>
                  <input
                    type="date"
                    required
                    value={formData.scheduled_date}
                    onChange={(e) => setFormData({ ...formData, scheduled_date: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                {/* Hora */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Horário *
                  </label>
                  <input
                    type="time"
                    required
                    value={formData.scheduled_time}
                    onChange={(e) => setFormData({ ...formData, scheduled_time: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                {/* Duração */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Duração (minutos) *
                  </label>
                  <select
                    required
                    value={formData.duration_minutes}
                    onChange={(e) => setFormData({ ...formData, duration_minutes: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="15">15 minutos</option>
                    <option value="30">30 minutos</option>
                    <option value="45">45 minutos</option>
                    <option value="60">1 hora</option>
                    <option value="90">1h 30min</option>
                    <option value="120">2 horas</option>
                  </select>
                </div>

                {/* Tipo */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Tipo de Consulta *
                  </label>
                  <select
                    required
                    value={formData.appointment_type}
                    onChange={(e) => setFormData({ ...formData, appointment_type: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="first_time">Primeira Consulta</option>
                    <option value="return">Retorno</option>
                    <option value="emergency">Emergência</option>
                    <option value="telemedicine">Telemedicina</option>
                  </select>
                </div>
              </div>

              {/* Observações */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Observações
                </label>
                <textarea
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="Informações adicionais..."
                />
              </div>

              {/* Botões */}
              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowNewAppointmentModal(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Agendar Consulta
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
