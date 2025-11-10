'use client';

import { usePathname, useRouter } from 'next/navigation';
import Link from 'next/link';
import { useState, useEffect } from 'react';
import { Home, Calendar, FileText, MessageSquare, DollarSign, Users as UsersIcon, Settings, LogOut, Building2, Menu, X, Users, Shield } from 'lucide-react';

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    const userStr = localStorage.getItem('user');
    if (userStr && userStr !== 'undefined') {
      try {
        const userData = JSON.parse(userStr);
        setUser(userData);
      } catch (error) {
        console.error('Erro ao parsear user:', error);
      }
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    router.push('/login');
  };

  const isAdmin = user?.role === 'super_admin' || user?.role === 'admin';
  const isSuperAdmin = user?.role === 'super_admin';

  if (!user) return null;

  return (
    <>
      <button
        onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
        className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-white rounded-lg shadow-lg"
      >
        {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
      </button>

      {isMobileMenuOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-40"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}

      <aside
        className={`
          fixed top-0 left-0 h-screen w-64 bg-white border-r border-gray-200 flex flex-col
          transition-transform duration-300 z-40
          ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        `}
      >
        <div className="p-6 border-b border-gray-200">
          <h1 className="text-2xl font-bold text-gray-900">Sanaris Pro</h1>
        </div>

        <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
          <Link
            href="/"
            className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
              pathname === '/' ? 'bg-blue-50 text-blue-600' : 'text-gray-700 hover:bg-gray-100'
            }`}
            onClick={() => setIsMobileMenuOpen(false)}
          >
            <Home className="w-5 h-5" />
            <span>Dashboard</span>
          </Link>

          <Link
            href="/pacientes"
            className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
              pathname === '/pacientes' ? 'bg-blue-50 text-blue-600' : 'text-gray-700 hover:bg-gray-100'
            }`}
            onClick={() => setIsMobileMenuOpen(false)}
          >
            <UsersIcon className="w-5 h-5" />
            <span>Pacientes</span>
          </Link>

          <Link
            href="/agenda"
            className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
              pathname === '/agenda' ? 'bg-blue-50 text-blue-600' : 'text-gray-700 hover:bg-gray-100'
            }`}
            onClick={() => setIsMobileMenuOpen(false)}
          >
            <Calendar className="w-5 h-5" />
            <span>Agenda</span>
          </Link>

          <Link
            href="/prontuarios"
            className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
              pathname === '/prontuarios' ? 'bg-blue-50 text-blue-600' : 'text-gray-700 hover:bg-gray-100'
            }`}
            onClick={() => setIsMobileMenuOpen(false)}
          >
            <FileText className="w-5 h-5" />
            <span>Prontuários</span>
          </Link>

          <Link
            href="/prescricoes"
            className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
              pathname === '/prescricoes' ? 'bg-blue-50 text-blue-600' : 'text-gray-700 hover:bg-gray-100'
            }`}
            onClick={() => setIsMobileMenuOpen(false)}
          >
            <FileText className="w-5 h-5" />
            <span>Prescrições</span>
          </Link>

          <Link
            href="/cfm"
            className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
              pathname === '/cfm' ? 'bg-blue-50 text-blue-600' : 'text-gray-700 hover:bg-gray-100'
            }`}
            onClick={() => setIsMobileMenuOpen(false)}
          >
            <Shield className="w-5 h-5" />
            <span>CFM</span>
          </Link>

          <Link
            href="/financeiro"
            className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
              pathname === '/financeiro' ? 'bg-blue-50 text-blue-600' : 'text-gray-700 hover:bg-gray-100'
            }`}
            onClick={() => setIsMobileMenuOpen(false)}
          >
            <DollarSign className="w-5 h-5" />
            <span>Financeiro</span>
          </Link>

          <Link
            href="/faturamento-tiss"
            className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
              pathname === '/faturamento-tiss' ? 'bg-blue-50 text-blue-600' : 'text-gray-700 hover:bg-gray-100'
            }`}
            onClick={() => setIsMobileMenuOpen(false)}
          >
            <FileText className="w-5 h-5" />
            <span>Faturamento TISS</span>
          </Link>

          <Link
            href="/relatorios"
            className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
              pathname === '/relatorios' ? 'bg-blue-50 text-blue-600' : 'text-gray-700 hover:bg-gray-100'
            }`}
            onClick={() => setIsMobileMenuOpen(false)}
          >
            <FileText className="w-5 h-5" />
            <span>Relatórios</span>
          </Link>

          <Link
            href="/configuracoes"
            className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
              pathname === '/configuracoes' ? 'bg-blue-50 text-blue-600' : 'text-gray-700 hover:bg-gray-100'
            }`}
            onClick={() => setIsMobileMenuOpen(false)}
          >
            <Settings className="w-5 h-5" />
            <span>Configurações</span>
          </Link>

          <Link
            href="/chat"
            className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
              pathname === '/chat' ? 'bg-blue-50 text-blue-600' : 'text-gray-700 hover:bg-gray-100'
            }`}
            onClick={() => setIsMobileMenuOpen(false)}
          >
            <MessageSquare className="w-5 h-5" />
            <span>Chat</span>
          </Link>

          {isAdmin && (
            <>
              <div className="pt-4 mt-4 border-t border-gray-200">
                <p className="px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
                  Administração
                </p>
              </div>

              {isSuperAdmin && (
                <Link
                  href="/organizacoes"
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                    pathname === '/organizacoes' ? 'bg-blue-50 text-blue-600' : 'text-gray-700 hover:bg-gray-100'
                  }`}
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  <Building2 className="w-5 h-5" />
                  <span>Organizações</span>
                </Link>
              )}

              <Link
                href="/usuarios"
                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                  pathname === '/usuarios' ? 'bg-blue-50 text-blue-600' : 'text-gray-700 hover:bg-gray-100'
                }`}
                onClick={() => setIsMobileMenuOpen(false)}
              >
                <Users className="w-5 h-5" />
                <span>Usuários</span>
              </Link>
            </>
          )}
        </nav>

        <div className="p-4 border-t border-gray-200">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
              <span className="text-gray-600 font-semibold">
                {user?.full_name?.charAt(0).toUpperCase() || 'U'}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">
                {user?.full_name || 'Usuário'}
              </p>
              <p className="text-xs text-gray-500 capitalize">
                {user?.role === 'super_admin' ? 'Super Admin' : user?.role === 'admin' ? 'Admin' : 'Usuário'}
              </p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="w-full flex items-center justify-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors"
          >
            <LogOut className="w-4 h-4" />
            <span>Sair</span>
          </button>
        </div>
      </aside>
    </>
  );
}
