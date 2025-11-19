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
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">Nova Consulta</h2>
            <p className="text-gray-600 mb-4">
              Funcionalidade de agendamento será implementada em breve.
            </p>
            <button
              onClick={() => setShowNewAppointmentModal(false)}
              className="w-full px-4 py-2 bg-gray-200 rounded-lg hover:bg-gray-300"
            >
              Fechar
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
