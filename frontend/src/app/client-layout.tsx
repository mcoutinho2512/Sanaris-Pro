'use client';

import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import Link from 'next/link';
import { 
  Building2, Users, LayoutDashboard, LogOut, 
  Menu, X, Settings, Lock, ChevronDown,
  UserCircle, Calendar, FileText, Pill, 
  Shield, DollarSign, FileBarChart, BarChart3, MessageSquare, UserCheck,
  Stethoscope
} from 'lucide-react';

interface Module {
  id: string;
  name: string;
  icon: any;
  path: string;
}

export default function ClientLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [userRole, setUserRole] = useState<string>('');
  const [userName, setUserName] = useState<string>('');
  const [allowedModules, setAllowedModules] = useState<string[]>([]);
  const [showProfileMenu, setShowProfileMenu] = useState(false);

  // PÁGINAS PÚBLICAS (sem sidebar)
  const publicPages = ['/login', '/forgot-password', '/reset-password'];
  const isPublicPage = publicPages.some(page => pathname?.startsWith(page));

  useEffect(() => {
    console.log('🔍 CLIENT-LAYOUT: useEffect executado, pathname:', pathname);
    const fetchUserData = async () => {
      try {
        const token = localStorage.getItem('token');
        console.log('🔑 CLIENT-LAYOUT: Token encontrado?', !!token);
        if (token) {
          console.log('📋 CLIENT-LAYOUT: Token lido:', token.substring(0, 50) + '...');
        }
        if (token) {
          console.log('📋 CLIENT-LAYOUT: Token lido:', token.substring(0, 50) + '...');
        }
        if (!token) {
          console.log('❌ CLIENT-LAYOUT: Sem token, redirecionando para /login');
          router.push('/login');
          return;
        }
        console.log('✅ CLIENT-LAYOUT: Token OK, buscando dados do usuário...');

        const meResponse = await fetch('http://localhost:8888/api/v1/auth/me', {
          headers: { 'Authorization': `Bearer ${token}` }
        });

        if (meResponse.ok) {
          const userData = await meResponse.json();
          console.log('👤 CLIENT-LAYOUT: Dados do usuário:', userData);
          setUserRole(userData.role);
          setUserName(userData.full_name);
        } else {
          console.error('❌ CLIENT-LAYOUT: Erro no /auth/me:', meResponse.status);
        }

        const modulesResponse = await fetch('http://localhost:8888/api/v1/permissions/my-modules', {
          headers: { 'Authorization': `Bearer ${token}` }
        });

        if (modulesResponse.ok) {
          const modulesData = await modulesResponse.json();
          setAllowedModules(Array.isArray(modulesData) ? modulesData : []);
        }
      } catch (error) {
        console.error('Erro ao carregar dados:', error);
      }
    };

    if (!isPublicPage) {
      fetchUserData();
    }
  }, [pathname, router, isPublicPage]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    router.push('/login');
  };

  // Se for página pública, renderizar sem layout
  if (isPublicPage) {
    return <>{children}</>;
  }

  const superAdminModules: Module[] = [
    { id: 'organizations', name: 'Organizações', icon: Building2, path: '/organizacoes' }
  ];

  const adminModules: Module[] = [
    { id: 'users', name: 'Usuários', icon: Users, path: '/usuarios' }
  ];

  const allModules: Module[] = [
    { id: 'dashboard', name: 'Dashboard', icon: LayoutDashboard, path: '/dashboard' },
    { id: 'pacientes', name: 'Pacientes', icon: UserCircle, path: '/pacientes' },
    { id: 'agenda', name: 'Agenda', icon: Calendar, path: '/agenda' },
    { id: 'prontuarios', name: 'Prontuários', icon: FileText, path: '/prontuarios' },
    { id: 'prescricoes', name: 'Prescrições', icon: Pill, path: '/prescricoes' },
    { id: 'cfm', name: 'CFM', icon: Shield, path: '/cfm' },
    { id: 'financeiro', name: 'Financeiro', icon: DollarSign, path: '/financeiro' },
    { id: 'faturamento_tiss', name: 'Faturamento TISS', icon: FileBarChart, path: '/faturamento-tiss' },
    { id: 'prestadores', name: 'Prestadores', icon: UserCheck, path: '/prestadores' },
    { id: 'relatorios', name: 'Relatórios', icon: BarChart3, path: '/relatorios' },
    { id: 'configuracoes', name: 'Configurações', icon: Settings, path: '/configuracoes' },
    { id: 'chat', name: 'Chat', icon: MessageSquare, UserCheck, path: '/chat' },
    { id: 'meu-perfil', name: 'Meu Perfil', icon: Stethoscope, path: '/meu-perfil' }
  ];

  const visibleModules = userRole === 'super_admin' 
    ? superAdminModules  // Super admin vê APENAS gestão do sistema
    : userRole === 'admin'
    ? [...allModules, ...adminModules]  // Admin vê tudo da clínica + gestão de usuários
    : allModules.filter(m => 
        m.id !== 'financeiro' &&  // Usuário básico NUNCA vê financeiro
        m.id !== 'faturamento_tiss' &&
        allowedModules.includes(m.id)  // Apenas módulos permitidos
      );

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className={`${isSidebarOpen ? 'w-64' : 'w-20'} bg-white shadow-lg transition-all duration-300 flex flex-col`}>
        {/* Header */}
        <div className="p-4 border-b flex items-center justify-between">
          {isSidebarOpen && (
            <Link href="/" className="text-xl font-bold text-blue-600">
              Sanaris Pro
            </Link>
          )}
          <button
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="p-2 hover:bg-gray-100 rounded-lg"
          >
            {isSidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>

        {/* Menu Items */}
        <nav className="flex-1 p-4 space-y-2">
          {visibleModules.map((module) => {
            const Icon = module.icon;
            const isActive = pathname === module.path;
            
            return (
              <Link
                key={module.id}
                href={module.path}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                  isActive 
                    ? 'bg-blue-50 text-blue-600' 
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                <Icon className="w-5 h-5 flex-shrink-0" />
                {isSidebarOpen && <span className="font-medium">{module.name}</span>}
              </Link>
            );
          })}
        </nav>

        {/* User Profile with Dropdown */}
        <div className="border-t p-4 relative">
          <button
            onClick={() => setShowProfileMenu(!showProfileMenu)}
            className="w-full flex items-center gap-3 p-3 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white font-semibold flex-shrink-0">
              {userName.charAt(0).toUpperCase()}
            </div>
            {isSidebarOpen && (
              <>
                <div className="flex-1 text-left">
                  <p className="text-sm font-medium text-gray-900">{userName}</p>
                  <p className="text-xs text-gray-500">
                    {userRole === 'super_admin' ? 'Super Admin' : 
                     userRole === 'admin' ? 'Admin' : 'Usuário'}
                  </p>
                </div>
                <ChevronDown className={`w-4 h-4 text-gray-500 transition-transform ${showProfileMenu ? 'rotate-180' : ''}`} />
              </>
            )}
          </button>

          {/* Dropdown Menu */}
          {showProfileMenu && isSidebarOpen && (
            <div className="absolute bottom-full left-4 right-4 mb-2 bg-white border border-gray-200 rounded-lg shadow-lg overflow-hidden">
              <Link
                href="/configuracoes"
                onClick={() => setShowProfileMenu(false)}
                className="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 transition-colors"
              >
                <Lock className="w-4 h-4 text-gray-600" />
                <span className="text-sm text-gray-700">Alterar Senha</span>
              </Link>
              <button
                onClick={handleLogout}
                className="w-full flex items-center gap-3 px-4 py-3 hover:bg-red-50 transition-colors border-t"
              >
                <LogOut className="w-4 h-4 text-red-600" />
                <span className="text-sm text-red-600">Sair</span>
              </button>
            </div>
          )}
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        {children}
      </main>
    </div>
  );
}
