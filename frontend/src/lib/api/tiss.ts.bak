import { api } from '../api';

export const tissOperadorasAPI = {
  list: (params?: any) => api.get('/tiss/operadoras/', { params }),
  get: (id: string) => api.get(`/tiss/operadoras/${id}`),
  create: (data: any) => api.post('/tiss/operadoras/', data),
  update: (id: string, data: any) => api.put(`/tiss/operadoras/${id}`, data),
  delete: (id: string) => api.delete(`/tiss/operadoras/${id}`),
};

export const tissLotesAPI = {
  list: (params?: any) => api.get('/tiss/lotes/', { params }),
  get: (id: string) => api.get(`/tiss/lotes/${id}`),
  create: (data: any) => api.post('/tiss/lotes/', data),
  update: (id: string, data: any) => api.put(`/tiss/lotes/${id}`, data),
  delete: (id: string) => api.delete(`/tiss/lotes/${id}`),
  fechar: (id: string) => api.post(`/tiss/lotes/${id}/fechar`),
};

export const tissGuiasAPI = {
  list: (params?: any) => api.get('/tiss/guias/', { params }),
  get: (id: string) => api.get(`/tiss/guias/${id}`),
  create: (data: any) => api.post('/tiss/guias/', data),
  update: (id: string, data: any) => api.put(`/tiss/guias/${id}`, data),
  delete: (id: string) => api.delete(`/tiss/guias/${id}`),
  calcularValor: (id: string) => api.post(`/tiss/guias/${id}/calcular-valor`),
};

export const tissProcedimentosAPI = {
  listByGuia: (guiaId: string) => api.get(`/tiss/procedimentos/guia/${guiaId}`),
  get: (id: string) => api.get(`/tiss/procedimentos/${id}`),
  create: (data: any) => api.post('/tiss/procedimentos/', data),
  update: (id: string, data: any) => api.put(`/tiss/procedimentos/${id}`, data),
  delete: (id: string) => api.delete(`/tiss/procedimentos/${id}`),
};

export const tissTabelasAPI = {
  list: (params?: any) => api.get('/tiss/tabelas/', { params }),
  get: (id: string) => api.get(`/tiss/tabelas/${id}`),
  buscarPorCodigo: (codigo: string, tipo?: string) => 
    api.get(`/tiss/tabelas/buscar/${codigo}`, { params: { tipo_tabela: tipo } }),
  create: (data: any) => api.post('/tiss/tabelas/', data),
  update: (id: string, data: any) => api.put(`/tiss/tabelas/${id}`, data),
  delete: (id: string) => api.delete(`/tiss/tabelas/${id}`),
  importarTuss: () => api.post('/tiss/tabelas/importar-tuss'),
};
// ============================================

// ============================================
// PRESTADORES
// ============================================
export const prestadoresAPI = {
  list: (params?: { tipo_prestador?: string; ativo?: boolean }) => 
    api.get("/prestadores/", { params }),
  get: (id: string) => 
    api.get(`/prestadores/${id}`),
  create: (data: any) => 
    api.post("/prestadores/", data),
  update: (id: string, data: any) => 
    api.put(`/prestadores/${id}`, data),
  delete: (id: string) => 
    api.delete(`/prestadores/${id}`),
};
