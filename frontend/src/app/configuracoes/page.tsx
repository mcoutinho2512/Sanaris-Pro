'use client';

import { useState, useEffect } from 'react';
import { Lock, Eye, EyeOff, ArrowLeft, Save, Shield, User } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function ConfiguracoesPage() {
  const router = useRouter();
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [showOldPassword, setShowOldPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'senha' | 'perfil'>('senha');
  
  const [formData, setFormData] = useState({
    old_password: '',
    new_password: '',
    confirm_password: ''
  });

  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    loadCurrentUser();
  }, []);

  const loadCurrentUser = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8888/api/v1/auth/me', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setCurrentUser(data);
      }
    } catch (error) {
      console.error('Erro ao carregar usuário:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (formData.new_password.length < 6) {
      setError('A nova senha deve ter pelo menos 6 caracteres');
      return;
    }

    if (formData.new_password !== formData.confirm_password) {
      setError('As senhas não coincidem');
      return;
    }

    if (formData.old_password === formData.new_password) {
      setError('A nova senha deve ser diferente da senha atual');
      return;
    }

    setIsLoading(true);

    try {
      const token = localStorage.getItem('token');
      
      const formBody = new URLSearchParams();
      formBody.append('old_password', formData.old_password);
      formBody.append('new_password', formData.new_password);

      const response = await fetch('http://localhost:8888/api/v1/auth/change-password', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: formBody
      });

      if (response.ok) {
        setSuccess('Senha alterada com sucesso!');
        setFormData({
          old_password: '',
          new_password: '',
          confirm_password: ''
        });
        
        setTimeout(() => {
          router.push('/');
        }, 2000);
      } else {
        const data = await response.json();
        setError(data.detail || 'Erro ao alterar senha');
      }
    } catch (error) {
      console.error('Erro:', error);
      setError('Erro ao conectar com o servidor');
    } finally {
      setIsLoading(false);
    }
  };

  const isAdmin = currentUser && currentUser.role === 'admin';

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="mb-6">
          <button
            onClick={() => router.push('/')}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="w-4 h-4" />
            Voltar ao Dashboard
          </button>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <User className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Configurações</h1>
              <p className="text-gray-500">Gerencie suas preferências e segurança</p>
            </div>
          </div>

          {/* Opções para Admin */}
          {isAdmin && (
            <div className="mb-6 p-4 bg-blue-50 border-2 border-blue-200 rounded-lg">
              <h3 className="font-semibold text-blue-900 mb-3">Configurações de Administrador</h3>
              <button
                onClick={() => router.push('/configuracoes/permissoes')}
                className="w-full flex items-center justify-between p-4 bg-white border-2 border-blue-200 rounded-lg hover:bg-blue-50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <Shield className="w-5 h-5 text-blue-600" />
                  <div className="text-left">
                    <p className="font-semibold text-gray-900">Gerenciar Permissões</p>
                    <p className="text-sm text-gray-500">Controle o acesso dos usuários aos módulos do sistema</p>
                  </div>
                </div>
                <ArrowLeft className="w-5 h-5 text-gray-400 rotate-180" />
              </button>
            </div>
          )}

          {/* Trocar Senha */}
          <div className="border-t pt-6">
            <div className="flex items-center gap-2 mb-4">
              <Lock className="w-5 h-5 text-gray-600" />
              <h2 className="text-xl font-semibold text-gray-900">Alterar Senha</h2>
            </div>

            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-800 text-sm">
                {error}
              </div>
            )}

            {success && (
              <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg text-green-800 text-sm">
                {success}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Senha Atual *
                </label>
                <div className="relative">
                  <input
                    type={showOldPassword ? 'text' : 'password'}
                    value={formData.old_password}
                    onChange={(e) => setFormData({...formData, old_password: e.target.value})}
                    required
                    className="w-full px-4 py-2 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <button
                    type="button"
                    onClick={() => setShowOldPassword(!showOldPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showOldPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nova Senha * (mínimo 6 caracteres)
                </label>
                <div className="relative">
                  <input
                    type={showNewPassword ? 'text' : 'password'}
                    value={formData.new_password}
                    onChange={(e) => setFormData({...formData, new_password: e.target.value})}
                    required
                    minLength={6}
                    className="w-full px-4 py-2 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <button
                    type="button"
                    onClick={() => setShowNewPassword(!showNewPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showNewPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Confirmar Nova Senha *
                </label>
                <div className="relative">
                  <input
                    type={showConfirmPassword ? 'text' : 'password'}
                    value={formData.confirm_password}
                    onChange={(e) => setFormData({...formData, confirm_password: e.target.value})}
                    required
                    minLength={6}
                    className="w-full px-4 py-2 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => router.push('/')}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={isLoading}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  <Save className="w-4 h-4" />
                  {isLoading ? 'Salvando...' : 'Alterar Senha'}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
