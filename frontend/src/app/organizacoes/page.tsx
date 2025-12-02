'use client';

import { useState, useEffect } from 'react';
import { Building2, Plus, Edit, Save, X, Users, DollarSign, ArrowLeft } from 'lucide-react';
import { useRouter } from 'next/navigation';

interface Organization {
  id: string;
  name: string;
  cnpj?: string;
  max_users: number;
  is_active: boolean;
  created_at: string;
}

export default function OrganizationsPage() {
  const router = useRouter();
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [showModal, setShowModal] = useState(false);
  const [editingOrg, setEditingOrg] = useState<Organization | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [currentUser, setCurrentUser] = useState<any>(null);

  const [formData, setFormData] = useState({
    name: '',
    cnpj: '',
    max_users: 10
  });

  useEffect(() => {
    loadCurrentUser();
    loadOrganizations();
  }, []);

  const loadCurrentUser = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        router.push('/login');
        return;
      }

      const response = await fetch('/api/v1/auth/me', {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setCurrentUser(data);
        
        // Verificar se é super_admin
        if (data.role !== 'super_admin') {
          alert('Acesso negado! Apenas super administradores podem acessar esta área.');
          router.push('/');
        }
      } else {
        router.push('/login');
      }
    } catch (error) {
      console.error('Erro ao carregar usuário:', error);
      router.push('/login');
    }
  };

  const loadOrganizations = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/v1/organizations/', {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setOrganizations(data);
      }
    } catch (error) {
      console.error('Erro ao carregar organizações:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const token = localStorage.getItem('token');
      const url = editingOrg
        ? `/api/v1/organizations/${editingOrg.id}`
        : '/api/v1/organizations/';

      const response = await fetch(url, {
        method: editingOrg ? 'PUT' : 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        alert(editingOrg ? 'Organização atualizada!' : 'Organização criada!');
        setShowModal(false);
        setEditingOrg(null);
        resetForm();
        loadOrganizations();
      } else {
        const error = await response.json();
        alert(error.detail || 'Erro ao salvar organização');
      }
    } catch (error) {
      console.error('Erro:', error);
      alert('Erro ao salvar organização');
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      cnpj: '',
      max_users: 10
    });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Carregando organizações...</p>
        </div>
      </div>
    );
  }

  // Só renderiza se for super_admin
  if (!currentUser || currentUser.role !== 'super_admin') {
    return null;
  }

  return (
    <div className="p-6">
      <div className="mb-4">
        <button
          onClick={() => router.push('/')}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
        >
          <ArrowLeft className="w-5 h-5" />
          <span>Voltar ao Sistema</span>
        </button>
      </div>

      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Building2 className="w-8 h-8 text-blue-600" />
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Gerenciamento de Organizações</h1>
            <p className="text-sm text-gray-500">{organizations.length} organização(ões) cadastrada(s)</p>
          </div>
        </div>
        <button
          onClick={() => {
            setEditingOrg(null);
            resetForm();
            setShowModal(true);
          }}
          className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
        >
          <Plus className="w-5 h-5" />
          Nova Organização
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {organizations.map((org) => (
          <div key={org.id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                  <Building2 className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-lg text-gray-900">{org.name}</h3>
                  {org.cnpj && (
                    <p className="text-sm text-gray-500">CNPJ: {org.cnpj}</p>
                  )}
                </div>
              </div>
              <button
                onClick={() => {
                  setEditingOrg(org);
                  setFormData({
                    name: org.name,
                    cnpj: org.cnpj || '',
                    max_users: org.max_users
                  });
                  setShowModal(true);
                }}
                className="p-2 hover:bg-gray-100 rounded-lg"
              >
                <Edit className="w-4 h-4 text-gray-600" />
              </button>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600 flex items-center gap-2">
                  <Users className="w-4 h-4" />
                  Limite de Usuários
                </span>
                <span className="font-semibold text-gray-900">{org.max_users}</span>
              </div>

              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Status</span>
                <span className={`px-2 py-1 rounded-full text-xs ${
                  org.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                }`}>
                  {org.is_active ? 'Ativa' : 'Inativa'}
                </span>
              </div>

              <div className="text-xs text-gray-500 pt-2 border-t border-gray-100">
                Criada em: {new Date(org.created_at).toLocaleDateString('pt-BR')}
              </div>
            </div>
          </div>
        ))}
      </div>

      {organizations.length === 0 && (
        <div className="text-center py-12">
          <Building2 className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">Nenhuma organização cadastrada</p>
        </div>
      )}

      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold">
                {editingOrg ? 'Editar Organização' : 'Nova Organização'}
              </h2>
              <button
                onClick={() => {
                  setShowModal(false);
                  setEditingOrg(null);
                  resetForm();
                }}
                className="p-2 hover:bg-gray-100 rounded"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nome da Organização *
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600"
                  placeholder="Ex: Clínica Médica ABC"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  CNPJ
                </label>
                <input
                  type="text"
                  value={formData.cnpj}
                  onChange={(e) => setFormData({ ...formData, cnpj: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600"
                  placeholder="00.000.000/0000-00"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Limite de Usuários *
                </label>
                <input
                  type="number"
                  value={formData.max_users}
                  onChange={(e) => setFormData({ ...formData, max_users: parseInt(e.target.value) })}
                  required
                  min="1"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600"
                />
              </div>

              <div className="flex gap-2 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowModal(false);
                    setEditingOrg(null);
                    resetForm();
                  }}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="flex-1 flex items-center justify-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
                >
                  <Save className="w-4 h-4" />
                  {editingOrg ? 'Atualizar' : 'Criar'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
