'use client';

import { useState, useEffect } from 'react';
import { Building2, Users, UserCog, Shield, Activity, TrendingUp } from 'lucide-react';

interface DashboardStats {
  organizations: {
    total: number;
    active: number;
    inactive: number;
    new_last_6_months: number;
  };
  users: {
    total: number;
    active: number;
    inactive: number;
    recently_active_24h: number;
    by_role: {
      super_admins: number;
      admins: number;
      users: number;
    };
  };
  top_organizations: Array<{
    name: string;
    users: number;
  }>;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [userRole, setUserRole] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const token = localStorage.getItem('access_token');
      
      // Verificar role do usuário
      const meResponse = await fetch('http://localhost:8888/api/v1/auth/me', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (meResponse.ok) {
        const userData = await meResponse.json();
        setUserRole(userData.role);
        
        // Se for super admin, carregar dashboard específico
        if (userData.role === 'super_admin') {
          const statsResponse = await fetch('http://localhost:8888/api/v1/admin/dashboard', {
            headers: { 'Authorization': `Bearer ${token}` }
          });
          
          if (statsResponse.ok) {
            const data = await statsResponse.json();
            setStats(data);
          }
        }
      }
    } catch (error) {
      console.error('Erro ao carregar dashboard:', error);
    } finally {
      setIsLoading(false);
    }
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

  // Dashboard para Super Admin
  if (userRole === 'super_admin' && stats) {
    return (
      <div className="p-6 bg-gray-50 min-h-screen">
        <div className="max-w-7xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900">Dashboard do Sistema</h1>
            <p className="text-gray-500 mt-1">Visão geral da plataforma Sanaris Pro</p>
          </div>

          {/* Cards principais */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {/* Organizações */}
            <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg p-6 text-white shadow-lg">
              <div className="flex items-center justify-between mb-4">
                <Building2 className="w-8 h-8" />
                <span className="text-sm bg-white/20 px-2 py-1 rounded">
                  {stats.organizations.active} ativas
                </span>
              </div>
              <h3 className="text-sm font-medium mb-2 opacity-90">Total de Organizações</h3>
              <p className="text-4xl font-bold">{stats.organizations.total}</p>
              <p className="text-sm mt-2 opacity-80">
                +{stats.organizations.new_last_6_months} nos últimos 6 meses
              </p>
            </div>

            {/* Total Usuários */}
            <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg p-6 text-white shadow-lg">
              <div className="flex items-center justify-between mb-4">
                <Users className="w-8 h-8" />
                <span className="text-sm bg-white/20 px-2 py-1 rounded">
                  {stats.users.active} ativos
                </span>
              </div>
              <h3 className="text-sm font-medium mb-2 opacity-90">Total de Usuários</h3>
              <p className="text-4xl font-bold">{stats.users.total}</p>
              <p className="text-sm mt-2 opacity-80">
                {stats.users.inactive} inativos
              </p>
            </div>

            {/* Usuários Online */}
            <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg p-6 text-white shadow-lg">
              <div className="flex items-center justify-between mb-4">
                <Activity className="w-8 h-8" />
                <span className="text-sm bg-white/20 px-2 py-1 rounded animate-pulse">
                  Online
                </span>
              </div>
              <h3 className="text-sm font-medium mb-2 opacity-90">Ativos (24h)</h3>
              <p className="text-4xl font-bold">{stats.users.recently_active_24h}</p>
              <p className="text-sm mt-2 opacity-80">
                {Math.round((stats.users.recently_active_24h / stats.users.total) * 100)}% do total
              </p>
            </div>

            {/* Crescimento */}
            <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-lg p-6 text-white shadow-lg">
              <div className="flex items-center justify-between mb-4">
                <TrendingUp className="w-8 h-8" />
                <span className="text-sm bg-white/20 px-2 py-1 rounded">
                  6 meses
                </span>
              </div>
              <h3 className="text-sm font-medium mb-2 opacity-90">Crescimento</h3>
              <p className="text-4xl font-bold">
                {stats.organizations.new_last_6_months}
              </p>
              <p className="text-sm mt-2 opacity-80">Novas organizações</p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Usuários por Hierarquia */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-6 flex items-center gap-2">
                <UserCog className="w-5 h-5 text-blue-600" />
                Usuários por Nível de Hierarquia
              </h3>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-red-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-red-500 rounded-full flex items-center justify-center">
                      <Shield className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <p className="font-semibold text-gray-900">Super Admins</p>
                      <p className="text-sm text-gray-500">Gestão do Sistema</p>
                    </div>
                  </div>
                  <span className="text-2xl font-bold text-red-600">
                    {stats.users.by_role.super_admins}
                  </span>
                </div>

                <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center">
                      <UserCog className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <p className="font-semibold text-gray-900">Administradores</p>
                      <p className="text-sm text-gray-500">Gestão de Clínicas</p>
                    </div>
                  </div>
                  <span className="text-2xl font-bold text-blue-600">
                    {stats.users.by_role.admins}
                  </span>
                </div>

                <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center">
                      <Users className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <p className="font-semibold text-gray-900">Usuários Comuns</p>
                      <p className="text-sm text-gray-500">Operacional</p>
                    </div>
                  </div>
                  <span className="text-2xl font-bold text-green-600">
                    {stats.users.by_role.users}
                  </span>
                </div>
              </div>
            </div>

            {/* Top Organizações */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-6 flex items-center gap-2">
                <Building2 className="w-5 h-5 text-blue-600" />
                Top 5 Organizações
              </h3>
              
              <div className="space-y-3">
                {stats.top_organizations.map((org, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                        <span className="text-blue-600 font-semibold text-sm">
                          {index + 1}
                        </span>
                      </div>
                      <p className="font-medium text-gray-900">{org.name}</p>
                    </div>
                    <span className="text-sm font-semibold text-gray-600">
                      {org.users} {org.users === 1 ? 'usuário' : 'usuários'}
                    </span>
                  </div>
                ))}
                
                {stats.top_organizations.length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    <Building2 className="w-12 h-12 mx-auto mb-2 text-gray-300" />
                    <p>Nenhuma organização cadastrada</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Dashboard padrão para admin/user (manter o antigo)
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-6">Dashboard Analítico</h1>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-blue-500 rounded-lg p-6 text-white">
              <h3 className="text-sm font-medium mb-2">Total de Pacientes</h3>
              <p className="text-3xl font-bold">6</p>
              <p className="text-sm mt-2">+6 no período</p>
            </div>
            
            <div className="bg-green-500 rounded-lg p-6 text-white">
              <h3 className="text-sm font-medium mb-2">Consultas Previstas</h3>
              <p className="text-3xl font-bold">0</p>
              <p className="text-sm mt-2">0 realizadas</p>
            </div>
            
            <div className="bg-purple-500 rounded-lg p-6 text-white">
              <h3 className="text-sm font-medium mb-2">Taxa de Realização</h3>
              <p className="text-3xl font-bold">0%</p>
            </div>
            
            <div className="bg-orange-500 rounded-lg p-6 text-white">
              <h3 className="text-sm font-medium mb-2">Total Prontuários</h3>
              <p className="text-3xl font-bold">1</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
