'use client';

import { useState, useEffect } from 'react';
import { Users, Plus, Edit, Trash2, Save, X, Building2, Shield, User as UserIcon, Filter, BarChart3, ArrowLeft } from 'lucide-react';
import { useRouter } from 'next/navigation';

interface User {
  id: string;
  email: string;
  full_name: string;
  organization_id?: string;
  organization_name?: string;
  role: string;
  is_active: boolean;
  crm?: string;
  specialty?: string;
  created_at: string;
}

interface Organization {
  id: string;
  name: string;
  max_users: number;
}

interface Statistics {
  organization_id: string;
  organization_name: string;
  max_users: number;
  current_users: number;
  available_slots: number;
  usage_percentage: number;
}

export default function UsersManagementPage() {
  const router = useRouter();
  const [users, setUsers] = useState<User[]>([]);
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [statistics, setStatistics] = useState<Statistics[]>([]);
  const [filteredUsers, setFilteredUsers] = useState<User[]>([]);
  const [currentUser, setCurrentUser] = useState<any>(null);
  
  const [showModal, setShowModal] = useState(false);
  const [showStatsModal, setShowStatsModal] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  
  const [filterOrg, setFilterOrg] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [filterRole, setFilterRole] = useState<string>('all');
  
  const [formData, setFormData] = useState({
    email: '',
    full_name: '',
    password: '',
    organization_id: '',
    role: 'user',
    crm: '',
    specialty: '',
    is_active: true
  });

  useEffect(() => {
    loadCurrentUser();
    loadUsers();
    loadOrganizations();
    loadStatistics();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [users, filterOrg, filterStatus, filterRole]);

  const loadCurrentUser = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8888/api/v1/auth/me', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setCurrentUser(data);
      }
    } catch (error) {
      console.error('Erro ao carregar usuário atual:', error);
    }
  };

  const applyFilters = () => {
    let filtered = [...users];
    
    if (filterOrg !== 'all') {
      filtered = filtered.filter(u => u.organization_id === filterOrg);
    }
    
    if (filterStatus !== 'all') {
      const isActive = filterStatus === 'active';
      filtered = filtered.filter(u => u.is_active === isActive);
    }
    
    if (filterRole !== 'all') {
      filtered = filtered.filter(u => u.role === filterRole);
    }
    
    setFilteredUsers(filtered);
  };

  const loadUsers = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8888/api/v1/users-management/', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setUsers(data);
        setFilteredUsers(data);
      }
    } catch (error) {
      console.error('Erro ao carregar usuários:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadOrganizations = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8888/api/v1/organizations/', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setOrganizations(data);
      }
    } catch (error) {
      console.error('Erro ao carregar organizações:', error);
    }
  };

  const loadStatistics = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8888/api/v1/users-management/statistics/by-organization', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setStatistics(data);
      }
    } catch (error) {
      console.error('Erro ao carregar estatísticas:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const token = localStorage.getItem('access_token');
      
      const response = await fetch('http://localhost:8888/api/v1/users-management/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        alert('Usuário criado!');
        setShowModal(false);
        resetForm();
        loadUsers();
        loadStatistics();
      } else {
        const error = await response.json();
        alert(error.detail || 'Erro ao criar usuário');
      }
    } catch (error) {
      console.error('Erro:', error);
      alert('Erro ao salvar usuário');
    }
  };

  const resetForm = () => {
    setFormData({
      email: '',
      full_name: '',
      password: '',
      organization_id: currentUser?.role === 'admin' ? currentUser.organization_id : '',
      role: 'user',
      crm: '',
      specialty: '',
      is_active: true
    });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Carregando usuários...</p>
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
          <span>Voltar ao Sistema</span>
        </button>
      </div>

      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Users className="w-8 h-8 text-blue-600" />
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Gerenciamento de Usuários</h1>
            <p className="text-sm text-gray-500">{filteredUsers.length} usuário(s) encontrado(s)</p>
          </div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setShowStatsModal(true)}
            className="flex items-center gap-2 bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200"
          >
            <BarChart3 className="w-5 h-5" />
            Estatísticas
          </button>
          <button
            onClick={() => {
              setEditingUser(null);
              resetForm();
              setShowModal(true);
            }}
            className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            <Plus className="w-5 h-5" />
            Novo Usuário
          </button>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="flex items-center gap-2 mb-3">
          <Filter className="w-5 h-5 text-gray-600" />
          <h3 className="font-semibold text-gray-900">Filtros</h3>
        </div>
        <div className={`grid ${currentUser?.role === 'super_admin' ? 'grid-cols-3' : 'grid-cols-2'} gap-4`}>
          {currentUser?.role === 'super_admin' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Organização</label>
              <select
                value={filterOrg}
                onChange={(e) => setFilterOrg(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600"
              >
                <option value="all">Todas</option>
                {organizations.map(org => (
                  <option key={org.id} value={org.id}>{org.name}</option>
                ))}
              </select>
            </div>
          )}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600"
            >
              <option value="all">Todos</option>
              <option value="active">Ativos</option>
              <option value="inactive">Inativos</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Papel</label>
            <select
              value={filterRole}
              onChange={(e) => setFilterRole(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600"
            >
              <option value="all">Todos</option>
              <option value="super_admin">Super Admin</option>
              <option value="admin">Admin</option>
              <option value="user">Usuário</option>
            </select>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Usuário</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Organização</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Papel</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">CRM</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {filteredUsers.map((user) => (
              <tr key={user.id} className="hover:bg-gray-50">
                <td className="px-6 py-4">
                  <div>
                    <p className="text-sm font-medium text-gray-900">{user.full_name}</p>
                    <p className="text-sm text-gray-500">{user.email}</p>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    <Building2 className="w-4 h-4 text-gray-400" />
                    <span className="text-sm text-gray-900">{user.organization_name || '-'}</span>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <span className={`inline-flex items-center gap-1 px-2 py-1 text-xs rounded-full ${
                    user.role === 'super_admin' ? 'bg-red-100 text-red-700' :
                    user.role === 'admin' ? 'bg-purple-100 text-purple-700' : 
                    'bg-blue-100 text-blue-700'
                  }`}>
                    {user.role === 'super_admin' ? <Shield className="w-3 h-3" /> : 
                     user.role === 'admin' ? <Shield className="w-3 h-3" /> : 
                     <UserIcon className="w-3 h-3" />}
                    {user.role === 'super_admin' ? 'Super Admin' : user.role === 'admin' ? 'Admin' : 'Usuário'}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    user.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                  }`}>
                    {user.is_active ? 'Ativo' : 'Inativo'}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <span className="text-sm text-gray-900">{user.crm || '-'}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {filteredUsers.length === 0 && (
          <div className="text-center py-12">
            <Users className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">Nenhum usuário encontrado</p>
          </div>
        )}
      </div>

      {/* MODAL CRIAR */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold">Novo Usuário</h2>
              <button onClick={() => setShowModal(false)} className="p-2 hover:bg-gray-100 rounded">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Nome Completo *</label>
                  <input
                    type="text"
                    value={formData.full_name}
                    onChange={(e) => setFormData({...formData, full_name: e.target.value})}
                    required
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600"
                  />
                </div>

                <div className="col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Email *</label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    required
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600"
                  />
                </div>

                <div className="col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Senha * (mínimo 6 caracteres)</label>
                  <input
                    type="password"
                    value={formData.password}
                    onChange={(e) => setFormData({...formData, password: e.target.value})}
                    required
                    minLength={6}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600"
                  />
                </div>

                <div className="col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Organização *</label>
                  {currentUser?.role === 'super_admin' ? (
                    <select
                      value={formData.organization_id}
                      onChange={(e) => setFormData({...formData, organization_id: e.target.value})}
                      required
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600"
                    >
                      <option value="">Selecione uma organização</option>
                      {organizations.map(org => (
                        <option key={org.id} value={org.id}>{org.name}</option>
                      ))}
                    </select>
                  ) : (
                    <input
                      type="text"
                      value={organizations.find(o => o.id === currentUser?.organization_id)?.name || ''}
                      disabled
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-100"
                    />
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Papel *</label>
                  <select
                    value={formData.role}
                    onChange={(e) => setFormData({...formData, role: e.target.value})}
                    required
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600"
                  >
                    <option value="user">Usuário</option>
                    {currentUser?.role === 'super_admin' && (
                      <>
                        <option value="admin">Admin da Clínica</option>
                        <option value="super_admin">Super Administrador</option>
                      </>
                    )}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">CRM</label>
                  <input
                    type="text"
                    value={formData.crm}
                    onChange={(e) => setFormData({...formData, crm: e.target.value})}
                    placeholder="12345"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600"
                  />
                </div>

                <div className="col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Especialidade</label>
                  <input
                    type="text"
                    value={formData.specialty}
                    onChange={(e) => setFormData({...formData, specialty: e.target.value})}
                    placeholder="Cardiologia"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600"
                  />
                </div>
              </div>

              <div className="flex gap-2 pt-4">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="flex-1 flex items-center justify-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
                >
                  <Save className="w-4 h-4" />
                  Criar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL ESTATÍSTICAS */}
      {showStatsModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-3xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold">Estatísticas por Organização</h2>
              <button onClick={() => setShowStatsModal(false)} className="p-2 hover:bg-gray-100 rounded">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4">
              {statistics.map((stat) => (
                <div key={stat.organization_id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <h3 className="font-semibold text-lg">{stat.organization_name}</h3>
                      <p className="text-sm text-gray-500">
                        {stat.current_users} de {stat.max_users} usuários
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-2xl font-bold text-blue-600">{stat.usage_percentage}%</p>
                      <p className="text-sm text-gray-500">{stat.available_slots} vagas disponíveis</p>
                    </div>
                  </div>
                  
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        stat.usage_percentage >= 90 ? 'bg-red-600' :
                        stat.usage_percentage >= 70 ? 'bg-yellow-600' :
                        'bg-green-600'
                      }`}
                      style={{ width: `${stat.usage_percentage}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
