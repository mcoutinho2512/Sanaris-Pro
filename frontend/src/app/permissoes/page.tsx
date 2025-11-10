'use client';

import { useState, useEffect } from 'react';
import { Shield, Users, Check, X, Save, ArrowLeft } from 'lucide-react';
import { useRouter } from 'next/navigation';

interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  organization_name?: string;
  allowed_modules: string[];
}

interface Module {
  id: string;
  name: string;
  icon: string;
}

const AVAILABLE_MODULES: Module[] = [
  { id: 'dashboard', name: 'Dashboard', icon: 'LayoutDashboard' },
  { id: 'pacientes', name: 'Pacientes', icon: 'Users' },
  { id: 'agenda', name: 'Agenda', icon: 'Calendar' },
  { id: 'prontuarios', name: 'Prontuários', icon: 'FileText' },
  { id: 'prescricoes', name: 'Prescrições', icon: 'FileEdit' },
  { id: 'cfm', name: 'CFM', icon: 'Shield' },
  { id: 'financeiro', name: 'Financeiro', icon: 'DollarSign' },
  { id: 'faturamento_tiss', name: 'Faturamento TISS', icon: 'Receipt' },
  { id: 'relatorios', name: 'Relatórios', icon: 'BarChart' },
  { id: 'configuracoes', name: 'Configurações', icon: 'Settings' },
  { id: 'chat', name: 'Chat', icon: 'MessageSquare' },
];

export default function PermissoesPage() {
  const router = useRouter();
  const [users, setUsers] = useState<User[]>([]);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [selectedModules, setSelectedModules] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8888/api/v1/users-management/users', {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        // Filtrar apenas usuários comuns (role='user')
        const commonUsers = data.filter((u: any) => u.role === 'user');
        setUsers(commonUsers);
      }
    } catch (error) {
      console.error('Erro ao carregar usuários:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadUserPermissions = async (userId: string) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8888/api/v1/permissions/user/${userId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setSelectedModules(data.allowed_modules || []);
      }
    } catch (error) {
      console.error('Erro ao carregar permissões:', error);
    }
  };

  const handleSelectUser = (user: User) => {
    setSelectedUser(user);
    loadUserPermissions(user.id);
  };

  const toggleModule = (moduleId: string) => {
    setSelectedModules(prev => 
      prev.includes(moduleId)
        ? prev.filter(m => m !== moduleId)
        : [...prev, moduleId]
    );
  };

  const handleSave = async () => {
    if (!selectedUser) return;

    setIsSaving(true);
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8888/api/v1/permissions/user/${selectedUser.id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          allowed_modules: selectedModules
        })
      });

      if (response.ok) {
        alert('Permissões atualizadas com sucesso!');
        loadUsers();
      } else {
        const error = await response.json();
        alert(error.detail || 'Erro ao atualizar permissões');
      }
    } catch (error) {
      console.error('Erro:', error);
      alert('Erro ao salvar permissões');
    } finally {
      setIsSaving(false);
    }
  };

  const selectAll = () => {
    setSelectedModules(AVAILABLE_MODULES.map(m => m.id));
  };

  const deselectAll = () => {
    setSelectedModules([]);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Carregando...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="mb-4">
        <button
          onClick={() => router.push('/')}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
        >
          <ArrowLeft className="w-5 h-5" />
          <span>Voltar ao Dashboard</span>
        </button>
      </div>

      <div className="flex items-center gap-3 mb-6">
        <Shield className="w-8 h-8 text-blue-600" />
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gerenciamento de Permissões</h1>
          <p className="text-sm text-gray-500">Configure os módulos que cada usuário pode acessar</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Lista de Usuários */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow">
            <div className="p-4 border-b border-gray-200">
              <div className="flex items-center gap-2">
                <Users className="w-5 h-5 text-gray-600" />
                <h2 className="text-lg font-semibold">Usuários</h2>
              </div>
              <p className="text-sm text-gray-500 mt-1">{users.length} usuário(s) comum(ns)</p>
            </div>
            <div className="divide-y divide-gray-200 max-h-[600px] overflow-y-auto">
              {users.map(user => (
                <button
                  key={user.id}
                  onClick={() => handleSelectUser(user)}
                  className={`w-full p-4 text-left hover:bg-gray-50 transition-colors ${
                    selectedUser?.id === user.id ? 'bg-blue-50' : ''
                  }`}
                >
                  <p className="font-medium text-gray-900">{user.full_name}</p>
                  <p className="text-sm text-gray-500">{user.email}</p>
                  {user.organization_name && (
                    <p className="text-xs text-gray-400 mt-1">{user.organization_name}</p>
                  )}
                </button>
              ))}
              {users.length === 0 && (
                <div className="p-8 text-center text-gray-500">
                  <Users className="w-12 h-12 mx-auto mb-2 text-gray-300" />
                  <p>Nenhum usuário comum encontrado</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Configuração de Permissões */}
        <div className="lg:col-span-2">
          {selectedUser ? (
            <div className="bg-white rounded-lg shadow">
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-xl font-semibold text-gray-900">{selectedUser.full_name}</h2>
                    <p className="text-sm text-gray-500">{selectedUser.email}</p>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={selectAll}
                      className="px-3 py-2 text-sm bg-green-100 text-green-700 rounded-lg hover:bg-green-200"
                    >
                      Selecionar Todos
                    </button>
                    <button
                      onClick={deselectAll}
                      className="px-3 py-2 text-sm bg-red-100 text-red-700 rounded-lg hover:bg-red-200"
                    >
                      Desmarcar Todos
                    </button>
                  </div>
                </div>
              </div>

              <div className="p-6">
                <h3 className="text-lg font-semibold mb-4">Módulos Disponíveis</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {AVAILABLE_MODULES.map(module => {
                    const isSelected = selectedModules.includes(module.id);
                    return (
                      <button
                        key={module.id}
                        onClick={() => toggleModule(module.id)}
                        className={`flex items-center gap-3 p-4 rounded-lg border-2 transition-all ${
                          isSelected
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-200 hover:border-gray-300 bg-white'
                        }`}
                      >
                        <div className={`w-6 h-6 rounded flex items-center justify-center ${
                          isSelected ? 'bg-blue-600' : 'bg-gray-200'
                        }`}>
                          {isSelected && <Check className="w-4 h-4 text-white" />}
                        </div>
                        <div className="flex-1 text-left">
                          <p className="font-medium text-gray-900">{module.name}</p>
                        </div>
                      </button>
                    );
                  })}
                </div>

                <div className="mt-6 flex gap-3">
                  <button
                    onClick={handleSave}
                    disabled={isSaving}
                    className="flex-1 flex items-center justify-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50"
                  >
                    <Save className="w-5 h-5" />
                    {isSaving ? 'Salvando...' : 'Salvar Permissões'}
                  </button>
                  <button
                    onClick={() => setSelectedUser(null)}
                    className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50"
                  >
                    Cancelar
                  </button>
                </div>

                <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <p className="text-sm text-yellow-800">
                    <strong>Atenção:</strong> As alterações entrarão em vigor na próxima vez que o usuário fizer login.
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow p-12">
              <div className="text-center">
                <Shield className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Selecione um Usuário
                </h3>
                <p className="text-gray-500">
                  Escolha um usuário na lista ao lado para configurar suas permissões
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
