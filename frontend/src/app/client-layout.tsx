'use client';

import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import Link from 'next/link';
import { 
  LayoutDashboard, Users, Calendar, FileText, FileEdit, 
  Shield, DollarSign, Receipt, BarChart, Settings, 
  MessageSquare, Building2, UserCog, LogOut, Menu, X
} from 'lucide-react';

interface SidebarItem {
  id: string;
  name: string;
  icon: any;
  href: string;
}

const ALL_MODULES: SidebarItem[] = [
  { id: 'dashboard', name: 'Dashboard', icon: LayoutDashboard, href: '/' },
  { id: 'pacientes', name: 'Pacientes', icon: Users, href: '/pacientes' },
  { id: 'agenda', name: 'Agenda', icon: Calendar, href: '/agenda' },
  { id: 'prontuarios', name: 'Prontuários', icon: FileText, href: '/prontuarios' },
  { id: 'prescricoes', name: 'Prescrições', icon: FileEdit, href: '/prescricoes' },
  { id: 'cfm', name: 'CFM', icon: Shield, href: '/cfm' },
  { id: 'financeiro', name: 'Financeiro', icon: DollarSign, href: '/financeiro' },
  { id: 'faturamento_tiss', name: 'Faturamento TISS', icon: Receipt, href: '/faturamento' },
  { id: 'relatorios', name: 'Relatórios', icon: BarChart, href: '/relatorios' },
  { id: 'configuracoes', name: 'Configurações', icon: Settings, href: '/configuracoes' },
  { id: 'chat', name: 'Chat', icon: MessageSquare, href: '/chat' },
];

const SUPER_ADMIN_MODULES: SidebarItem[] = [
  { id: 'organizacoes', name: 'Organizações', icon: Building2, href: '/organizacoes' },
  { id: 'usuarios', name: 'Usuários', icon: UserCog, href: '/usuarios' },
];

export default function ClientLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [user, setUser] = useState<any>(null);
  const [allowedModules, setAllowedModules] = useState<string[]>([]);
  const [sidebarItems, setSidebarItems] = useState<SidebarItem[]>([]);
  const [isOpen, setIsOpen] = useState(true);
  const [isLoading, setIsLoading] = useState(true);

  // Páginas públicas - não verificar auth
  const isPublicRoute = pathname === '/login' || pathname === '/register';

  useEffect(() => {
    // NUNCA executar checkAuth em páginas públicas
    if (isPublicRoute) {
      setIsLoading(false);
      setUser(null);
      return;
    }

    // Só verificar auth se não for rota pública
    checkAuth();
  }, [pathname, isPublicRoute]);

  const checkAuth = async () => {
    // Double check - garantir que não é rota pública
    if (isPublicRoute) {
      setIsLoading(false);
      return;
    }

    const token = localStorage.getItem('access_token');
    if (!token) {
      router.push('/login');
      setIsLoading(false);
      return;
    }

    try {
      // Buscar dados do usuário
      const response = await fetch('http://localhost:8888/api/v1/auth/me', {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!response.ok) {
        localStorage.removeItem('access_token');
        router.push('/login');
        setIsLoading(false);
        return;
      }

      const userData = await response.json();
      setUser(userData);

      // Buscar módulos permitidos
      const modulesResponse = await fetch('http://localhost:8888/api/v1/permissions/my-modules', {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (modulesResponse.ok) {
        const modulesData = await modulesResponse.json();
        setAllowedModules(modulesData.modules || []);
        
        // Filtrar sidebar baseado no role
        if (modulesData.role === 'super_admin') {
          setSidebarItems(SUPER_ADMIN_MODULES);
        } else {
          // Admin e User veem apenas módulos permitidos
          const filteredModules = ALL_MODULES.filter(module => 
            modulesData.modules.includes(module.id)
          );
          setSidebarItems(filteredModules);
        }
      }
    } catch (error) {
      console.error('Erro ao verificar autenticação:', error);
      localStorage.removeItem('access_token');
      router.push('/login');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    setUser(null);
    router.push('/login');
  };

  // Se for rota pública, renderizar apenas children
  if (isPublicRoute) {
    return <>{children}</>;
  }

  // Enquanto carrega
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

  // Se não tiver usuário, não renderizar (redirecionará para login)
  if (!user) {
    return null;
  }

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      {/* Sidebar */}
      <aside className={`${isOpen ? 'w-64' : 'w-20'} bg-white border-r border-gray-200 transition-all duration-300`}>
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200">
            {isOpen && <h1 className="text-xl font-bold text-blue-600">Sanaris Pro</h1>}
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="p-2 hover:bg-gray-100 rounded-lg"
            >
              {isOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 overflow-y-auto p-4">
            <div className="space-y-1">
              {sidebarItems.map((item) => {
                const Icon = item.icon;
                const isActive = pathname === item.href;
                
                return (
                  <Link
                    key={item.id}
                    href={item.href}
                    className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                      isActive
                        ? 'bg-blue-50 text-blue-600'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    {isOpen && <span className="font-medium">{item.name}</span>}
                  </Link>
                );
              })}
            </div>

            {/* Seção Admin (apenas para admin) */}
            {user.role === 'admin' && (
              <>
                <div className="mt-6 mb-2">
                  {isOpen && (
                    <p className="px-3 text-xs font-semibold text-gray-400 uppercase">
                      Administração
                    </p>
                  )}
                </div>
                <div className="space-y-1">
                  <Link
                    href="/usuarios"
                    className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                      pathname === '/usuarios'
                        ? 'bg-blue-50 text-blue-600'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    <UserCog className="w-5 h-5" />
                    {isOpen && <span className="font-medium">Usuários</span>}
                  </Link>
                  <Link
                    href="/permissoes"
                    className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                      pathname === '/permissoes'
                        ? 'bg-blue-50 text-blue-600'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    <Shield className="w-5 h-5" />
                    {isOpen && <span className="font-medium">Permissões</span>}
                  </Link>
                </div>
              </>
            )}
          </nav>

          {/* User Info */}
          <div className="border-t border-gray-200 p-4">
            <div className="flex items-center gap-3 mb-3">
              <div className={`w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white font-semibold ${!isOpen && 'mx-auto'}`}>
                {user.full_name?.charAt(0).toUpperCase()}
              </div>
              {isOpen && (
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {user.full_name}
                  </p>
                  <p className="text-xs text-gray-500">
                    {user.role === 'super_admin' ? 'Super Admin' : 
                     user.role === 'admin' ? 'Administrador' : 'Usuário'}
                  </p>
                </div>
              )}
            </div>
            <button
              onClick={handleLogout}
              className={`flex items-center gap-2 w-full px-3 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors ${!isOpen && 'justify-center'}`}
            >
              <LogOut className="w-5 h-5" />
              {isOpen && <span className="font-medium">Sair</span>}
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        {children}
      </main>
    </div>
  );
}
