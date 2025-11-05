'use client';

import { useState, useEffect, useRef } from 'react';
import { Search, User, Calendar, X } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { patientsService, Patient } from '@/services/patients.service';
import { appointmentsService, Appointment } from '@/services/appointments.service';

export function GlobalSearch() {
  const [query, setQuery] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [patients, setPatients] = useState<Patient[]>([]);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const router = useRouter();
  const searchRef = useRef<HTMLDivElement>(null);

  // Fechar dropdown ao clicar fora
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Buscar ao digitar
  useEffect(() => {
    if (query.trim().length < 2) {
      setPatients([]);
      setAppointments([]);
      return;
    }

    const searchTimeout = setTimeout(() => {
      performSearch();
    }, 500); // Debounce de 500ms

    return () => clearTimeout(searchTimeout);
  }, [query]);

  const performSearch = async () => {
    try {
      setLoading(true);
      
      // Buscar pacientes
      const patientsResults = await patientsService.list(query);
      setPatients(patientsResults.slice(0, 5)); // Limitar a 5 resultados

      // Buscar agendamentos (apenas se a query parecer uma data ou nome)
      try {
        const appointmentsResults = await appointmentsService.list();
        // Filtrar agendamentos que correspondem à busca
        const filtered = appointmentsResults.filter(apt => {
          const patient = patientsResults.find(p => p.id === apt.patient_id);
          return patient?.full_name.toLowerCase().includes(query.toLowerCase());
        });
        setAppointments(filtered.slice(0, 5));
      } catch (error) {
        console.error('Erro ao buscar agendamentos:', error);
      }

    } catch (error) {
      console.error('Erro na busca:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePatientClick = (patientId: string) => {
    console.log('Abrindo paciente:', patientId);
    setIsOpen(false);
    setQuery('');
    router.push('/pacientes?id=' + patientId + '&action=view');
  };

  const handleAppointmentClick = (appointmentId: string) => {
    console.log('Abrindo agendamento:', appointmentId);
    setIsOpen(false);
    setQuery('');
    router.push('/agenda');
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR');
  };

  const formatTime = (dateString: string) => {
    return new Date(dateString).toLocaleTimeString('pt-BR', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const hasResults = patients.length > 0 || appointments.length > 0;

  return (
    <div ref={searchRef} className="relative flex-1 max-w-md">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
        <input
          type="search"
          placeholder="Buscar pacientes, agendamentos..."
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setIsOpen(true);
          }}
          onFocus={() => query.length >= 2 && setIsOpen(true)}
          className="w-full pl-10 pr-10 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        {query && (
          <button
            onClick={() => {
              setQuery('');
              setPatients([]);
              setAppointments([]);
              setIsOpen(false);
            }}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>

      {/* Dropdown de Resultados */}
      {isOpen && query.length >= 2 && (
        <div className="absolute top-full mt-2 w-full bg-white rounded-lg shadow-lg border border-gray-200 max-h-96 overflow-y-auto z-50">
          {loading ? (
            <div className="p-4 text-center text-gray-500">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-2 text-sm">Buscando...</p>
            </div>
          ) : hasResults ? (
            <>
              {/* Pacientes */}
              {patients.length > 0 && (
                <div className="p-2">
                  <div className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase">
                    Pacientes
                  </div>
                  {patients.map((patient) => (
                    <button
                      key={patient.id}
                      onClick={() => handlePatientClick(patient.id)}
                      className="w-full px-3 py-2 hover:bg-gray-50 rounded-lg flex items-center gap-3 text-left"
                    >
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                          <User className="h-4 w-4 text-blue-600" />
                        </div>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {patient.full_name}
                        </p>
                        <p className="text-xs text-gray-500 truncate">
                          {patient.cpf && `CPF: ${patient.cpf}`}
                          {patient.email && ` • ${patient.email}`}
                        </p>
                      </div>
                    </button>
                  ))}
                </div>
              )}

              {/* Agendamentos */}
              {appointments.length > 0 && (
                <div className="p-2 border-t">
                  <div className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase">
                    Agendamentos
                  </div>
                  {appointments.map((appointment) => {
                    const patient = patients.find(p => p.id === appointment.patient_id);
                    return (
                      <button
                        key={appointment.id}
                        onClick={() => handleAppointmentClick(appointment.id)}
                        className="w-full px-3 py-2 hover:bg-gray-50 rounded-lg flex items-center gap-3 text-left"
                      >
                        <div className="flex-shrink-0">
                          <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                            <Calendar className="h-4 w-4 text-green-600" />
                          </div>
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-900 truncate">
                            {patient?.full_name || 'Paciente'}
                          </p>
                          <p className="text-xs text-gray-500">
                            {formatDate(appointment.scheduled_date)} às {formatTime(appointment.scheduled_date)}
                          </p>
                        </div>
                      </button>
                    );
                  })}
                </div>
              )}
            </>
          ) : (
            <div className="p-4 text-center text-gray-500">
              <p className="text-sm">Nenhum resultado encontrado</p>
              <p className="text-xs mt-1">Tente buscar por nome, CPF ou email</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
