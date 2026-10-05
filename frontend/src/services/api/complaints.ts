import { fetchApi } from './client';
import { ComplaintListResponse, ComplaintResponse, ImportSummary } from '@/types/api';

export const complaintsApi = {
  uploadCsv: async (file: File): Promise<ImportSummary> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('data_truth', 'SYNTHETIC_DATA');
    
    // We cannot use fetchApi wrapper for FormData directly because it forces Content-Type: application/json
    // Let's use standard fetch here.
    const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const response = await fetch(`${BASE_URL}/ingest/csv`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || errorData.message || 'Failed to upload CSV');
    }
    
    return response.json();
  },

  getComplaints: async (page = 1, pageSize = 50): Promise<ComplaintListResponse> => {
    return fetchApi<ComplaintListResponse>(`/complaints?page=${page}&page_size=${pageSize}`);
  },

  getComplaint: async (id: string): Promise<ComplaintResponse> => {
    return fetchApi<ComplaintResponse>(`/complaints/${id}`);
  }
};
