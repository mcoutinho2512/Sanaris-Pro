"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Home,
  Users,
  Calendar,
  FileText,
  Pill,
  DollarSign,
  Receipt,
  Settings,
  BarChart3,
  Stethoscope,
} from "lucide-react";
import { cn } from "@/lib/utils";

const menuItems = [
  { href: "/", label: "Dashboard", icon: Home },
  { href: "/pacientes", label: "Pacientes", icon: Users },
  { href: "/agenda", label: "Agenda", icon: Calendar },
  { href: "/prontuarios", label: "Prontuários", icon: FileText },
  { href: "/prescricoes", label: "Prescrições", icon: Pill },
  { href: "/cfm", label: "CFM", icon: Stethoscope },
  { href: "/financeiro", label: "Financeiro", icon: DollarSign },
  { href: "/faturamento-tiss", label: "Faturamento TISS", icon: Receipt },
  { href: "/relatorios", label: "Relatórios", icon: BarChart3 },
  { href: "/configuracoes", label: "Configurações", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="flex h-screen w-64 flex-col border-r bg-background">
      {/* Logo */}
      <div className="flex h-16 items-center border-b px-6">
        <h1 className="text-2xl font-bold text-primary">Sanaris Pro</h1>
      </div>

      {/* Menu */}
      <nav className="flex-1 space-y-1 p-4">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
              )}
            >
              <Icon className="h-5 w-5" />
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="border-t p-4">
        <div className="flex items-center gap-3 rounded-lg px-3 py-2">
          <div className="h-8 w-8 rounded-full bg-primary/10" />
          <div className="flex-1">
            <p className="text-sm font-medium">Clínica Exemplo</p>
            <p className="text-xs text-muted-foreground">Admin</p>
          </div>
        </div>
      </div>
    </div>
  );
}
