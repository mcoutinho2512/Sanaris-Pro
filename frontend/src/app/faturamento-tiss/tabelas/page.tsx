"use client";

import { Database } from "lucide-react";

export default function TabelasPage() {
  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Tabelas de Referência</h1>
          <p className="text-gray-600">TUSS e CBHPM</p>
        </div>
      </div>

      <div className="text-center py-12 bg-gray-50 rounded-lg">
        <Database className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-600">Módulo em desenvolvimento</p>
      </div>
    </div>
  );
}
