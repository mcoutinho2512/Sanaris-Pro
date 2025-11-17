'use client';

import { useEffect, useState } from 'react';
import { Shield, Save, ArrowLeft, Users, Check } from 'lucide-react';
import { useRouter } from 'next/navigation';

interface User {
  id: string;
  full_name: string;
  email: string;
  role: string;
  allowed_modules: string[];
}

const AVAILABLE_MODULES = [
  { id: 'dashboard', name: 'Dashboard', description: 'Página inicial com visão geral' },
  { id: 'pacientes', name: 'Pacientes', description: 'Cadastro e gestão de pacientes' },
  { id: 'agenda', name: 'Agenda', description: 'Agendamentos e calendário' },
  { id: 'prontuarios', name: 'Prontuários', description: 'Prontuários eletrônicos' },
  { id: 'prescricoes', name: 'Prescrições', description: 'Prescrições médicas' },
  { id: 'cfm', name: 'CFM', description: 'Portal do CFM' },
  { id: 'relatorios', name: 'Relatórios', description: 'Relatórios e estatísticas' },
  { id: 'chat', name: 'Chat', description: 'Mensagens internas' },
  { id: 'configuracoes', name: 'Configurações', description: 'Configurações pessoais' }
];

export default function PermissoesPage() {
  const router = useRouter();
  const [users, setUsers] = useState<User[]>([]);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [selectedModules, setSelectedModules] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8888/api/v1/users-management/users', {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        // Filtrar apenas usuários básicos (role='user')
        const basicUsers = data.filter((u: User) => u.role === 'user');
        setUsers(basicUsers);
      }
    } catch (error) {
      console.error('Erro ao carregar usuários:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectUser = (user: User) => {
    setSelectedUser(user);
    setSelectedModules(user.allowed_modules || []);
    setMessage('');
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

    setSaving(true);
    setMessage('');

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8888/api/v1/users-management/users/${selectedUser.id}/modules`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ allowed_modules: selectedModules })
      });

      if (response.ok) {
        setMessage('✅ Permissões salvas com sucesso!');
        // Atualizar lista de usuários
        await loadUsers();
      } else {
        setMessage('❌ Erro ao salvar permissões');
      }
    } catch (error) {
      console.error('Erro:', error);
      setMessage('❌ Erro ao conectar com o servidor');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Carregando...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => router.push('/configuracoes')}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
          >
            <ArrowLeft className="w-4 h-4" />
            Voltar para Configurações
          </button>

          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <Shield className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Gerenciar Permissões</h1>
              <p className="text-gray-500">Controle quais módulos os usuários podem acessar</p>
            </div>
          </div>
        </div>

        {/* Mensagem */}
        {message && (
          <div className={`mb-4 p-4 rounded-lg ${message.includes('✅') ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'}`}>
            {message}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Lista de Usuários */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center gap-2 mb-4">
              <Users className="w-5 h-5 text-gray-600" />
              <h2 className="text-lg font-semibold text-gray-900">
                Usuários ({users.length})
              </h2>
            </div>

            <div className="space-y-2 max-h-[600px] overflow-y-auto">
              {users.length === 0 ? (
                <p className="text-sm text-gray-500 text-center py-8">
                  Nenhum usuário básico cadastrado
                </p>
              ) : (
                users.map(user => (
                  <button
                    key={user.id}
                    onClick={() => handleSelectUser(user)}
                    className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                      selectedUser?.id === user.id
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                    }`}
                  >
                    <p className="font-medium text-gray-900">{user.full_name}</p>
                    <p className="text-sm text-gray-500">{user.email}</p>
                    <p className="text-xs text-gray-400 mt-1">
                      {user.allowed_modules?.length || 0} módulos permitidos
                    </p>
                  </button>
                ))
              )}
            </div>
          </div>

          {/* Módulos Disponíveis */}
          <div className="lg:col-span-2 bg-white rounded-xl shadow-sm p-6">
            {selectedUser ? (
              <>
                <div className="mb-6">
                  <h2 className="text-lg font-semibold text-gray-900 mb-1">
                    {selectedUser.full_name}
                  </h2>
                  <p className="text-sm text-gray-500">{selectedUser.email}</p>
                </div>

                <div className="mb-6">
                  <h3 className="text-md font-semibold text-gray-700 mb-4">
                    Selecione os módulos permitidos:
                  </h3>

                  <div className="space-y-3">
                    {AVAILABLE_MODULES.map(module => (
                      <label
                        key={module.id}
                        className="flex items-start gap-3 p-4 border-2 border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-all"
                      >
                        <input
                          type="checkbox"
                          checked={selectedModules.includes(module.id)}
                          onChange={() => toggleModule(module.id)}
                          className="mt-1 w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                        />
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <p className="font-medium text-gray-900">{module.name}</p>
                            {selectedModules.includes(module.id) && (
                              <Check className="w-4 h-4 text-green-600" />
                            )}
                          </div>
                          <p className="text-sm text-gray-500">{module.description}</p>
                        </div>
                      </label>
                    ))}
                  </div>
                </div>

                <div className="flex gap-3">
                  <button
                    onClick={handleSave}
                    disabled={saving}
                    className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
                  >
                    <Save className="w-5 h-5" />
                    {saving ? 'Salvando...' : 'Salvar Permissões'}
                  </button>
                </div>
              </>
            ) : (
              <div className="text-center py-20">
                <Shield className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Selecione um usuário
                </h3>
                <p className="text-gray-500">
                  Escolha um usuário na lista ao lado para gerenciar suas permissões
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
