'use client';

import { useEffect, useState } from 'react';
import { Shield, Check, Save, ArrowLeft, Users } from 'lucide-react';
import { useRouter } from 'next/navigation';

interface Permission {
  id: string;
  name: string;
  description: string;
  module: string;
  action: string;
}

interface User {
  id: string;
  full_name: string;
  email: string;
  role: string;
}

export default function PermissoesPage() {
  const router = useRouter();
  const [users, setUsers] = useState<User[]>([]);
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [userPermissions, setUserPermissions] = useState<{[key: string]: string[]}>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [selectedUser, setSelectedUser] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');

      const usersRes = await fetch('http://localhost:8888/api/v1/users-management/', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const usersData = await usersRes.json();
      setUsers(Array.isArray(usersData) ? usersData : []);

      const permsRes = await fetch('http://localhost:8888/api/v1/permissions/');
      const permsData = await permsRes.json();
      setPermissions(Array.isArray(permsData) ? permsData : []);

      const userPermsMap: {[key: string]: string[]} = {};
      for (const user of (Array.isArray(usersData) ? usersData : [])) {
        try {
          const userPermsRes = await fetch(`http://localhost:8888/api/v1/permissions/user/${user.id}`);
          if (userPermsRes.ok) {
            const data = await userPermsRes.json();
            userPermsMap[user.id] = Array.isArray(data.permissions) ? data.permissions.map((p: Permission) => p.id) : [];
          }
        } catch (e) {
          console.error('Erro ao carregar permissões do usuário:', e);
        }
      }
      setUserPermissions(userPermsMap);
    } catch (error) {
      console.error('Erro:', error);
    } finally {
      setLoading(false);
    }
  };

  const togglePermission = (userId: string, permId: string) => {
    setUserPermissions(prev => {
      const current = prev[userId] || [];
      return {
        ...prev,
        [userId]: current.includes(permId) ? current.filter(id => id !== permId) : [...current, permId]
      };
    });
  };

  const savePermissions = async (userId: string) => {
    try {
      setSaving(true);
      const response = await fetch(`http://localhost:8888/api/v1/permissions/user/${userId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ permission_ids: userPermissions[userId] || [] })
      });
      if (response.ok) alert('Permissões salvas!');
    } catch (error) {
      alert('Erro ao salvar');
    } finally {
      setSaving(false);
    }
  };

  const groupByModule = () => {
    const grouped: {[key: string]: Permission[]} = {};
    permissions.forEach(p => {
      if (!grouped[p.module]) grouped[p.module] = [];
      grouped[p.module].push(p);
    });
    return grouped;
  };

  const moduleNames: {[key: string]: string} = {
    'patients': 'Pacientes', 'appointments': 'Agenda', 'medical_records': 'Prontuários',
    'prescriptions': 'Prescrições', 'chat': 'Chat', 'financial': 'Financeiro',
    'reports': 'Relatórios', 'tiss': 'TISS', 'cfm': 'CFM', 'admin': 'Administração'
  };

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const grouped = groupByModule();

  return (
    <div className="p-6">
      <button onClick={() => router.push('/')} className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4">
        <ArrowLeft className="w-5 h-5" />
        Voltar
      </button>

      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <Shield className="w-8 h-8 text-blue-600" />
          <h1 className="text-2xl font-bold">Gerenciar Permissões</h1>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center gap-2 mb-4">
            <Users className="w-5 h-5" />
            <h2 className="font-semibold">Usuários ({users.length})</h2>
          </div>
          {users.map(user => (
            <button
              key={user.id}
              onClick={() => setSelectedUser(user.id)}
              className={`w-full text-left p-3 rounded-lg mb-2 ${selectedUser === user.id ? 'bg-blue-100 border-2 border-blue-600' : 'bg-gray-50 hover:bg-gray-100'}`}
            >
              <div className="font-medium">{user.full_name}</div>
              <div className="text-sm text-gray-600">{user.email}</div>
              <div className="text-xs text-gray-500">{(userPermissions[user.id] || []).length} permissões</div>
            </button>
          ))}
        </div>

        <div className="lg:col-span-2">
          {selectedUser ? (
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex justify-between mb-6">
                <div>
                  <h2 className="text-xl font-bold">{users.find(u => u.id === selectedUser)?.full_name}</h2>
                  <p className="text-sm text-gray-600">{users.find(u => u.id === selectedUser)?.email}</p>
                </div>
                <button onClick={() => savePermissions(selectedUser)} disabled={saving} className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                  <Save className="w-4 h-4" />
                  {saving ? 'Salvando...' : 'Salvar'}
                </button>
              </div>

              {Object.entries(grouped).map(([module, perms]) => (
                <div key={module} className="border-b pb-4 mb-4">
                  <h3 className="font-semibold text-lg mb-3">{moduleNames[module] || module}</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {perms.map(perm => {
                      const checked = (userPermissions[selectedUser] || []).includes(perm.id);
                      return (
                        <label key={perm.id} className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-50 cursor-pointer">
                          <input type="checkbox" checked={checked} onChange={() => togglePermission(selectedUser, perm.id)} className="w-5 h-5" />
                          <div className="flex-1">
                            <div className="font-medium text-sm">{perm.description}</div>
                            <div className="text-xs text-gray-500">{perm.name}</div>
                          </div>
                          {checked && <Check className="w-5 h-5 text-green-600" />}
                        </label>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow p-12 text-center text-gray-500">
              <Shield className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <p>Selecione um usuário</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
