'use client';

import { useState } from 'react';
import { ExternalLink, RefreshCw, ArrowLeft } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function CFMPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const [key, setKey] = useState(0);

  const handleReload = () => {
    setIsLoading(true);
    setKey(prev => prev + 1);
  };

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div className="flex items-center gap-4">
            <button onClick={() => router.push('/')} className="flex items-center gap-2 text-gray-600 hover:text-gray-900">
              <ArrowLeft className="w-5 h-5" />
              <span>Voltar</span>
            </button>
            <div className="h-6 w-px bg-gray-300" />
            <h1 className="text-xl font-bold text-gray-900">Portal CFM</h1>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={handleReload} className="flex items-center gap-2 px-3 py-2 text-sm text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition" title="Recarregar">
              <RefreshCw className="w-4 h-4" />
              Recarregar
            </button>
            <a href="https://portal.cfm.org.br" target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 px-3 py-2 text-sm text-blue-700 bg-blue-100 rounded-lg hover:bg-blue-200 transition">
              <ExternalLink className="w-4 h-4" />
              Abrir em Nova Aba
            </a>
          </div>
        </div>
      </div>
      {isLoading && (
        <div className="absolute inset-0 bg-white bg-opacity-90 flex items-center justify-center z-10">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Carregando Portal CFM...</p>
          </div>
        </div>
      )}
      <div className="flex-1 relative">
        <iframe key={key} src="https://portal.cfm.org.br" className="w-full h-full border-0" title="Portal CFM" onLoad={() => setIsLoading(false)} sandbox="allow-same-origin allow-scripts allow-popups allow-forms" />
      </div>
      <div className="bg-gray-100 border-t border-gray-200 px-4 py-2">
        <div className="max-w-7xl mx-auto flex items-center justify-between text-xs text-gray-600">
          <div><span className="font-semibold">Portal CFM</span> - Conselho Federal de Medicina</div>
          <div>Integrado ao Sanaris Pro</div>
        </div>
      </div>
    </div>
  );
}
