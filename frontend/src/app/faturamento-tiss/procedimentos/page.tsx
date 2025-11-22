"use client";

import { Stethoscope } from "lucide-react";

export default function ProcedimentosPage() {
  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Procedimentos</h1>
          <p className="text-gray-600">Gestão de procedimentos executados</p>
        </div>
      </div>

      <div className="text-center py-12 bg-gray-50 rounded-lg">
        <Stethoscope className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-600">Módulo em desenvolvimento</p>
      </div>
    </div>
  );
}
