'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { User, Stethoscope, Building2, Phone, Mail, MapPin, Palette, Save, Upload, X } from 'lucide-react';

interface DoctorProfile {
  id?: string;
  crm: string;
  crm_state: string;
  specialty: string;
  clinic_name: string;
  logo_url: string | null;
  primary_color: string;
  secondary_color: string;
  phone: string;
  email: string;
  address: string;
  footer_text: string;
}

export default function MeuPerfilPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [hasProfile, setHasProfile] = useState(false);
  const [logoFile, setLogoFile] = useState<File | null>(null);
  const [logoPreview, setLogoPreview] = useState<string | null>(null);

  const [formData, setFormData] = useState<DoctorProfile>({
    crm: '',
    crm_state: '',
    specialty: '',
    clinic_name: '',
    logo_url: null,
    primary_color: '#2563eb',
    secondary_color: '#1e40af',
    phone: '',
    email: '',
    address: '',
    footer_text: ''
  });

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/v1/doctor-profile/me', {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setFormData(data);
        setHasProfile(true);
        if (data.logo_url) {
          setLogoPreview(`${data.logo_url}`);
        }
      } else if (response.status === 404) {
        setHasProfile(false);
      }
    } catch (error) {
      console.error('Erro ao carregar perfil:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (!file.type.startsWith('image/')) {
        alert('Por favor, selecione uma imagem');
        return;
      }
      setLogoFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setLogoPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const uploadLogo = async () => {
    if (!logoFile) return null;

    const formDataUpload = new FormData();
    formDataUpload.append('file', logoFile);

    const token = localStorage.getItem('token');
    const response = await fetch('/api/v1/doctor-profile/upload-logo', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
      body: formDataUpload
    });

    if (response.ok) {
      const data = await response.json();
      return data.logo_url;
    }
    return null;
  };

  const handleSave = async () => {
    if (!formData.crm || !formData.crm_state) {
      alert('CRM e Estado são obrigatórios!');
      return;
    }

    setSaving(true);
    try {
      // Upload logo primeiro se houver
      if (logoFile) {
        const logoUrl = await uploadLogo();
        if (logoUrl) {
          formData.logo_url = logoUrl;
        }
      }

      const token = localStorage.getItem('token');
      const url = '/api/v1/doctor-profile/';
      const method = hasProfile ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        alert('Perfil salvo com sucesso!');
        setHasProfile(true);
        setLogoFile(null);
        loadProfile();
      } else {
        const error = await response.json();
        alert(error.detail || 'Erro ao salvar perfil');
      }
    } catch (error) {
      console.error('Erro:', error);
      alert('Erro ao salvar perfil');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center gap-3">
            <div className="bg-blue-100 p-3 rounded-lg">
              <Stethoscope className="w-8 h-8 text-blue-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Meu Perfil Médico</h1>
              <p className="text-gray-600">Configure sua identidade visual para documentos</p>
            </div>
          </div>
        </div>

        {/* Formulário */}
        <div className="bg-white rounded-lg shadow-sm p-6 space-y-6">
          
          {/* Dados Profissionais */}
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <User className="w-5 h-5" />
              Dados Profissionais
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  CRM *
                </label>
                <input
                  type="text"
                  value={formData.crm}
                  onChange={(e) => setFormData({...formData, crm: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="Ex: 52-951048"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Estado *
                </label>
                <input
                  type="text"
                  maxLength={2}
                  value={formData.crm_state}
                  onChange={(e) => setFormData({...formData, crm_state: e.target.value.toUpperCase()})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="RJ"
                />
              </div>
            </div>
            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Especialidade
              </label>
              <input
                type="text"
                value={formData.specialty}
                onChange={(e) => setFormData({...formData, specialty: e.target.value})}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="Ex: Cardiologia, Clínica Geral, etc."
              />
            </div>
          </div>

          {/* Dados do Consultório */}
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Building2 className="w-5 h-5" />
              Dados do Consultório
            </h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nome do Consultório/Clínica
                </label>
                <input
                  type="text"
                  value={formData.clinic_name}
                  onChange={(e) => setFormData({...formData, clinic_name: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="Ex: Vogue Square"
                />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <Phone className="w-4 h-4 inline mr-1" />
                    Telefone
                  </label>
                  <input
                    type="text"
                    value={formData.phone}
                    onChange={(e) => setFormData({...formData, phone: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="(21) 98108-6700"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <Mail className="w-4 h-4 inline mr-1" />
                    Email
                  </label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="contato@clinica.com"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <MapPin className="w-4 h-4 inline mr-1" />
                  Endereço Completo
                </label>
                <textarea
                  value={formData.address}
                  onChange={(e) => setFormData({...formData, address: e.target.value})}
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="Avenida das Américas, 8585, Barra da Tijuca, Rio de Janeiro - RJ"
                />
              </div>
            </div>
          </div>

          {/* Logo */}
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Upload className="w-5 h-5" />
              Logo do Consultório
            </h2>
            <div className="flex items-center gap-6">
              {logoPreview ? (
                <div className="relative">
                  <img src={logoPreview} alt="Logo" className="w-32 h-32 object-contain border-2 border-gray-200 rounded-lg" />
                  <button
                    onClick={() => {
                      setLogoPreview(null);
                      setLogoFile(null);
                      setFormData({...formData, logo_url: null});
                    }}
                    className="absolute -top-2 -right-2 bg-red-500 text-white p-1 rounded-full hover:bg-red-600"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ) : (
                <div className="w-32 h-32 border-2 border-dashed border-gray-300 rounded-lg flex items-center justify-center">
                  <Upload className="w-8 h-8 text-gray-400" />
                </div>
              )}
              <div>
                <input
                  type="file"
                  id="logo-upload"
                  accept="image/*"
                  onChange={handleLogoChange}
                  className="hidden"
                />
                <label
                  htmlFor="logo-upload"
                  className="cursor-pointer bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 inline-block"
                >
                  Escolher Logo
                </label>
                <p className="text-sm text-gray-500 mt-2">
                  PNG, JPG ou SVG (max 2MB)
                </p>
              </div>
            </div>
          </div>

          {/* Cores */}
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Palette className="w-5 h-5" />
              Cores Personalizadas
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Cor Primária
                </label>
                <div className="flex items-center gap-3">
                  <input
                    type="color"
                    value={formData.primary_color}
                    onChange={(e) => setFormData({...formData, primary_color: e.target.value})}
                    className="w-16 h-10 rounded cursor-pointer"
                  />
                  <input
                    type="text"
                    value={formData.primary_color}
                    onChange={(e) => setFormData({...formData, primary_color: e.target.value})}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Cor Secundária
                </label>
                <div className="flex items-center gap-3">
                  <input
                    type="color"
                    value={formData.secondary_color}
                    onChange={(e) => setFormData({...formData, secondary_color: e.target.value})}
                    className="w-16 h-10 rounded cursor-pointer"
                  />
                  <input
                    type="text"
                    value={formData.secondary_color}
                    onChange={(e) => setFormData({...formData, secondary_color: e.target.value})}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
            </div>
            
            {/* Preview das cores */}
            <div className="mt-4 p-4 rounded-lg border-2 border-gray-200">
              <p className="text-sm text-gray-600 mb-2">Preview:</p>
              <div className="flex gap-4">
                <div 
                  className="flex-1 h-20 rounded-lg flex items-center justify-center text-white font-semibold"
                  style={{ backgroundColor: formData.primary_color }}
                >
                  Cor Primária
                </div>
                <div 
                  className="flex-1 h-20 rounded-lg flex items-center justify-center text-white font-semibold"
                  style={{ backgroundColor: formData.secondary_color }}
                >
                  Cor Secundária
                </div>
              </div>
            </div>
          </div>

          {/* Rodapé Personalizado */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Rodapé dos Documentos (Opcional)
            </label>
            <textarea
              value={formData.footer_text}
              onChange={(e) => setFormData({...formData, footer_text: e.target.value})}
              rows={3}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="Texto que aparecerá no rodapé das prescrições e pedidos de exame"
            />
          </div>

          {/* Botões */}
          <div className="flex gap-4 pt-6 border-t">
            <button
              onClick={handleSave}
              disabled={saving}
              className="flex-1 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 flex items-center justify-center gap-2 font-semibold"
            >
              {saving ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
                  Salvando...
                </>
              ) : (
                <>
                  <Save className="w-5 h-5" />
                  Salvar Perfil
                </>
              )}
            </button>
            <button
              onClick={() => router.push('/dashboard')}
              className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Cancelar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
