'use client';

import { useState } from 'react';
import { Download, FileCheck, AlertCircle, CheckCircle } from 'lucide-react';

interface XMLGeneratorProps {
  loteId: string;
  numeroLote: string;
  onSuccess?: () => void;
}

interface ValidationResult {
  valido: boolean;
  erros: string[];
  avisos: string[];
  total_guias: number;
  pode_gerar: boolean;
}

export default function XMLGenerator({ loteId, numeroLote, onSuccess }: XMLGeneratorProps) {
  const [loading, setLoading] = useState(false);
  const [validating, setValidating] = useState(false);
  const [validation, setValidation] = useState<ValidationResult | null>(null);
  const [showValidation, setShowValidation] = useState(false);

  const validarLote = async () => {
    setValidating(true);
    try {
      const response = await fetch('/api/v1/tiss-xml/validar/' + loteId);
      if (!response.ok) throw new Error('Erro ao validar lote');
      
      const data = await response.json();
      setValidation(data);
      setShowValidation(true);
    } catch (error) {
      console.error('Erro na validação:', error);
      alert('Erro ao validar lote');
    } finally {
      setValidating(false);
    }
  };

  const gerarXML = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/tiss-xml/download/' + loteId);
      
      if (!response.ok) {
        throw new Error('Erro ao gerar XML');
      }

      const contentDisposition = response.headers.get('Content-Disposition');
      const filename = contentDisposition
        ? contentDisposition.split('filename=')[1].replace(/"/g, '')
        : 'TISS_' + numeroLote + '.xml';

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      alert('XML gerado com sucesso!\nArquivo: ' + filename);
      if (onSuccess) onSuccess();
      
    } catch (error) {
      console.error('Erro ao gerar XML:', error);
      alert('Erro ao gerar XML. Verifique o console para mais detalhes.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <button
          onClick={validarLote}
          disabled={validating}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          <FileCheck className="w-4 h-4" />
          {validating ? 'Validando...' : 'Validar Lote'}
        </button>

        <button
          onClick={gerarXML}
          disabled={!!(loading || (validation && !validation.pode_gerar))}
          className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          <Download className="w-4 h-4" />
          {loading ? 'Gerando XML...' : 'Gerar e Baixar XML'}
        </button>
      </div>

      {showValidation && validation && (
        <div className={'p-4 rounded-lg border-2 ' + (validation.valido ? 'bg-green-50 border-green-300' : 'bg-red-50 border-red-300')}>
          <div className="flex items-center gap-2 mb-3">
            {validation.valido ? (
              <>
                <CheckCircle className="w-5 h-5 text-green-600" />
                <h3 className="font-semibold text-green-800">Lote Válido para Geração</h3>
              </>
            ) : (
              <>
                <AlertCircle className="w-5 h-5 text-red-600" />
                <h3 className="font-semibold text-red-800">Lote com Problemas</h3>
              </>
            )}
          </div>

          <div className="space-y-2 text-sm">
            <p className="text-gray-700">
              <strong>Total de Guias:</strong> {validation.total_guias}
            </p>

            {validation.erros.length > 0 && (
              <div>
                <p className="font-semibold text-red-700 mb-1">Erros:</p>
                <ul className="list-disc list-inside space-y-1 text-red-600">
                  {validation.erros.map((erro, idx) => (
                    <li key={idx}>{erro}</li>
                  ))}
                </ul>
              </div>
            )}

            {validation.avisos.length > 0 && (
              <div>
                <p className="font-semibold text-yellow-700 mb-1">Avisos:</p>
                <ul className="list-disc list-inside space-y-1 text-yellow-600">
                  {validation.avisos.map((aviso, idx) => (
                    <li key={idx}>{aviso}</li>
                  ))}
                </ul>
              </div>
            )}

            {validation.valido && (
              <p className="text-green-700 font-medium mt-2">
                ✅ Lote pronto para geração de XML!
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}