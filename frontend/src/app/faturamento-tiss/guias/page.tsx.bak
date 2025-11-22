"use client";

import { useState, useEffect } from "react";
import { tissGuiasAPI, tissLotesAPI, tissOperadorasAPI } from "@/lib/api/tiss";
import { Plus, Edit, Trash2, FileText, Calculator } from "lucide-react";
import { toast } from "react-hot-toast";

interface Guia {
  id: string;
  numero_guia_prestador: string;
  tipo_guia: string;
  nome_beneficiario: string;
  data_atendimento: string;
  valor_total_informado: number;
  status: string;
}

export default function GuiasPage() {
  const [guias, setGuias] = useState<Guia[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadGuias();
  }, []);

  const loadGuias = async () => {
    try {
      const response = await tissGuiasAPI.list();
      setGuias(response.data);
    } catch (error) {
      toast.error("Erro ao carregar guias");
    } finally {
      setLoading(false);
    }
  };

  const getTipoGuiaLabel = (tipo: string) => {
    const labels: any = {
      consulta: "Consulta",
      sp_sadt: "SP/SADT",
      internacao: "Internação",
      urgencia: "Urgência/Emergência",
    };
    return labels[tipo] || tipo;
  };

  const getStatusColor = (status: string) => {
    const colors: any = {
      pendente: "bg-yellow-100 text-yellow-800",
      processada: "bg-green-100 text-green-800",
      glosada: "bg-red-100 text-red-800",
      paga: "bg-emerald-100 text-emerald-800",
    };
    return colors[status] || "bg-gray-100 text-gray-800";
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Guias TISS</h1>
          <p className="text-gray-600">Gestão de guias de atendimento</p>
        </div>
        <button
          onClick={() => toast("Funcionalidade em desenvolvimento")}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-blue-700"
        >
          <Plus className="w-5 h-5" />
          Nova Guia
        </button>
      </div>

      {loading ? (
        <div className="text-center py-12">Carregando...</div>
      ) : guias.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 mb-2">Nenhuma guia cadastrada</p>
          <p className="text-sm text-gray-500 mb-4">
            As guias TISS requerem um cadastro completo de paciente.<br/>
            Cadastre pacientes primeiro para poder criar guias.
          </p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Número Guia
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Tipo
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Beneficiário
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Data
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Valor
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {guias.map((guia) => (
                <tr key={guia.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {guia.numero_guia_prestador}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {getTipoGuiaLabel(guia.tipo_guia)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {guia.nome_beneficiario}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(guia.data_atendimento).toLocaleDateString("pt-BR")}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {new Intl.NumberFormat("pt-BR", {
                      style: "currency",
                      currency: "BRL",
                    }).format(guia.valor_total_informado)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(
                        guia.status
                      )}`}
                    >
                      {guia.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="mt-8 bg-amber-50 border border-amber-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-amber-900 mb-2">⚠️ Funcionalidade Avançada</h3>
        <p className="text-amber-800 text-sm mb-2">
          As Guias TISS são documentos complexos que requerem:
        </p>
        <ul className="text-amber-800 text-sm list-disc list-inside space-y-1">
          <li>Cadastro completo de pacientes</li>
          <li>Dados do prestador (clínica/médico)</li>
          <li>CID-10, autorização prévia</li>
          <li>Integração com módulo de Procedimentos</li>
        </ul>
        <p className="text-amber-800 text-sm mt-3">
          📋 <strong>Recomendação:</strong> Implemente o cadastro completo de pacientes e prestadores antes de usar este módulo.
        </p>
      </div>
    </div>
  );
}
