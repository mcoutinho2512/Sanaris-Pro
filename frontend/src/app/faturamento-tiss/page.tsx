"use client";

import { useRouter } from "next/navigation";
import { Building2, Package, FileText, Stethoscope, Database, ArrowRight } from "lucide-react";

export default function FaturamentoTISSPage() {
  const router = useRouter();

  const modules = [
    {
      title: "Operadoras",
      description: "Cadastro de operadoras de planos de saúde",
      icon: Building2,
      path: "/faturamento-tiss/operadoras",
      color: "bg-blue-500",
    },
    {
      title: "Lotes",
      description: "Gestão de lotes de faturamento",
      icon: Package,
      path: "/faturamento-tiss/lotes",
      color: "bg-green-500",
    },
    {
      title: "Guias",
      description: "Guias TISS (Consultas, SP/SADT)",
      icon: FileText,
      path: "/faturamento-tiss/guias",
      color: "bg-purple-500",
    },
    {
      title: "Procedimentos",
      description: "Procedimentos executados",
      icon: Stethoscope,
      path: "/faturamento-tiss/procedimentos",
      color: "bg-orange-500",
    },
    {
      title: "Tabelas",
      description: "Tabelas de referência (TUSS/CBHPM)",
      icon: Database,
      path: "/faturamento-tiss/tabelas",
      color: "bg-indigo-500",
    },
  ];

  return (
    <div className="p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Faturamento TISS</h1>
        <p className="text-gray-600">Sistema de faturamento para operadoras de planos de saúde</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {modules.map((module) => {
          const Icon = module.icon;
          return (
            <div
              key={module.path}
              onClick={() => router.push(module.path)}
              className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer border border-gray-200 overflow-hidden group"
            >
              <div className={module.color + " p-4"}>
                <Icon className="w-8 h-8 text-white" />
              </div>
              <div className="p-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-2 flex items-center justify-between">
                  {module.title}
                  <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-gray-600 transition-colors" />
                </h3>
                <p className="text-gray-600 text-sm">{module.description}</p>
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-2">ℹ️ Sobre o Faturamento TISS</h3>
        <p className="text-blue-800 text-sm">
          O padrão TISS (Troca de Informações na Saúde Suplementar) é o formato estabelecido pela ANS 
          para a comunicação entre prestadores de serviços de saúde e operadoras de planos de saúde.
        </p>
      </div>
    </div>
  );
}
