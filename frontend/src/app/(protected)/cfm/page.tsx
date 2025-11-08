'use client';

export default function CFMPage() {
  return (
    <div className="h-screen flex flex-col p-2">
      <div className="bg-white rounded-lg shadow p-4 mb-2">
        <h2 className="text-lg font-bold text-gray-800 mb-2">🏥 Portal CFM</h2>
        <p className="text-sm text-gray-600">
          <strong>Nota:</strong> A Prescrição Eletrônica não permite incorporação. 
          Para acessá-la, use o botão abaixo:
        </p>
        <a 
          href="https://prescricaoeletronica.cfm.org.br/" 
          target="_blank"
          rel="noopener noreferrer"
          className="inline-block mt-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
        >
          🔗 Abrir Prescrição Eletrônica (Nova Aba)
        </a>
      </div>
      
      <iframe
        src="https://portal.cfm.org.br/"
        className="flex-1 w-full rounded-lg shadow-lg border-2 border-gray-200"
        title="Portal CFM"
        allow="fullscreen"
      />
    </div>
  );
}
