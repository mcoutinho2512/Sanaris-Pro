import { 
  LayoutDashboard, UserCircle, Calendar, FileText, Pill, 
  Shield, DollarSign, FileBarChart, BarChart3, Settings, 
  MessageSquare, Stethoscope, Users, UserCheck,
  Building2, Package, FileSpreadsheet, ClipboardList, Table
} from 'lucide-react';

export interface MenuItem {
  id: string;
  name: string;
  icon: any;
  path?: string;
  children?: MenuItem[];
}

export const menuStructure: MenuItem[] = [
  { id: 'dashboard', name: 'Dashboard', icon: LayoutDashboard, path: '/dashboard' },
  { id: 'pacientes', name: 'Pacientes', icon: UserCircle, path: '/pacientes' },
  { id: 'agenda', name: 'Agenda', icon: Calendar, path: '/agenda' },
  { id: 'prontuarios', name: 'Prontuários', icon: FileText, path: '/prontuarios' },
  { id: 'prescricoes', name: 'Prescrições', icon: Pill, path: '/prescricoes' },
  { id: 'cfm', name: 'CFM', icon: Shield, path: '/cfm' },
  { id: 'financeiro', name: 'Financeiro', icon: DollarSign, path: '/financeiro' },
  { 
    id: 'faturamento_tiss', 
    name: 'Faturamento TISS', 
    icon: FileBarChart,
    children: [
      { id: 'tiss_dashboard', name: 'Dashboard', icon: LayoutDashboard, path: '/faturamento-tiss' },
      { id: 'operadoras', name: 'Operadoras', icon: Building2, path: '/faturamento-tiss/operadoras' },
      { id: 'lotes', name: 'Lotes', icon: Package, path: '/faturamento-tiss/lotes' },
      { id: 'guias', name: 'Guias', icon: FileSpreadsheet, path: '/faturamento-tiss/guias' },
      { id: 'procedimentos', name: 'Procedimentos', icon: ClipboardList, path: '/faturamento-tiss/procedimentos' },
      { id: 'tabelas', name: 'Tabelas', icon: Table, path: '/faturamento-tiss/tabelas' },
    ]
  },
  { id: 'prestadores', name: 'Prestadores', icon: UserCheck, path: '/prestadores' },
  { id: 'relatorios', name: 'Relatórios', icon: BarChart3, path: '/relatorios' },
  { id: 'configuracoes', name: 'Configurações', icon: Settings, path: '/configuracoes' },
  { id: 'chat', name: 'Chat', icon: MessageSquare, path: '/chat' },
  { id: 'meu-perfil', name: 'Meu Perfil', icon: Stethoscope, path: '/meu-perfil' }
];

export const superAdminMenu: MenuItem[] = [
  { id: 'dashboard', name: 'Dashboard', icon: LayoutDashboard, path: '/dashboard' },
  { id: 'organizacoes', name: 'Organizações', icon: Building2, path: '/organizacoes' },
  { id: 'usuarios', name: 'Usuários', icon: Users, path: '/usuarios' }
];
