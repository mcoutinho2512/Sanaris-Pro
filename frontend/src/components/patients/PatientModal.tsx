'use client';

import { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import { patientsService, Patient, PatientCreate, PatientUpdate } from '@/services/patients.service';

interface PatientModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  patient?: Patient | null;
}

export function PatientModal({ isOpen, onClose, onSuccess, patient }: PatientModalProps) {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    full_name: '',
    cpf: '',
    birth_date: '',
    phone: '',
    email: '',
  });

  useEffect(() => {
    if (patient) {
      setFormData({
        full_name: patient.full_name,
        cpf: patient.cpf || '',
        birth_date: patient.birth_date || '',
        phone: patient.phone || '',
        email: patient.email || '',
      });
    } else {
      setFormData({
        full_name: '',
        cpf: '',
        birth_date: '',
        phone: '',
        email: '',
      });
    }
  }, [patient, isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.full_name.trim()) {
      alert('Nome completo é obrigatório');
      return;
    }

    try {
      setLoading(true);
      
      if (patient) {
        // Atualizar paciente existente
        const updateData: PatientUpdate = {};
        if (formData.full_name) updateData.full_name = formData.full_name;
        if (formData.cpf) updateData.cpf = formData.cpf;
        if (formData.birth_date) updateData.birth_date = formData.birth_date;
        if (formData.phone) updateData.phone = formData.phone;
        if (formData.email) updateData.email = formData.email;
        
        await patientsService.update(patient.id, updateData);
        alert('Paciente atualizado com sucesso!');
      } else {
        // Criar novo paciente
        const createData: PatientCreate = {
          tenant_id: 'clinic-001', // TODO: Pegar do contexto de autenticação
          full_name: formData.full_name,
          cpf: formData.cpf || undefined,
          birth_date: formData.birth_date || undefined,
          phone: formData.phone || undefined,
          email: formData.email || undefined,
        };
        
        await patientsService.create(createData);
        alert('Paciente cadastrado com sucesso!');
      }
      
      onSuccess();
      onClose();
    } catch (error: any) {
      console.error('Erro ao salvar paciente:', error);
      alert(error.response?.data?.detail || 'Erro ao salvar paciente');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b">
          <h2 className="text-xl font-bold">
            {patient ? 'Editar Paciente' : 'Novo Paciente'}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
            disabled={loading}
          >
            <X size={24} />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6">
          <div className="space-y-4">
            {/* Nome Completo */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nome Completo <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.full_name}
                onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
                disabled={loading}
              />
            </div>

            {/* CPF */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                CPF
              </label>
              <input
                type="text"
                value={formData.cpf}
                onChange={(e) => setFormData({ ...formData, cpf: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="000.000.000-00"
                maxLength={14}
                disabled={loading}
              />
            </div>

            {/* Data de Nascimento */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Data de Nascimento
              </label>
              <input
                type="date"
                value={formData.birth_date}
                onChange={(e) => setFormData({ ...formData, birth_date: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={loading}
              />
            </div>

            {/* Telefone */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Telefone
              </label>
              <input
                type="tel"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="(00) 00000-0000"
                disabled={loading}
              />
            </div>

            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email
              </label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="email@exemplo.com"
                disabled={loading}
              />
            </div>
          </div>

          {/* Buttons */}
          <div className="flex justify-end gap-3 mt-6">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
              disabled={loading}
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:bg-blue-300"
              disabled={loading}
            >
              {loading ? 'Salvando...' : patient ? 'Atualizar' : 'Cadastrar'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
