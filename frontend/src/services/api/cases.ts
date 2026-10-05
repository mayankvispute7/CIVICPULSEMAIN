import { fetchApi } from './client';
import { 
  FailureCaseListResponse, 
  FailureCaseResponse, 
  EvidenceResponse,
  HistoryResponse,
  InterventionListResponse,
  DecisionAnalysisResponse,
  PredictionResponse,
  ResolutionPlanResponse
} from '@/types/api';

export const casesApi = {
  getCases: async (skip = 0, limit = 50): Promise<FailureCaseListResponse> => {
    return fetchApi<FailureCaseListResponse>(`/cases?skip=${skip}&limit=${limit}`);
  },

  getCase: async (id: string): Promise<FailureCaseResponse> => {
    return fetchApi<FailureCaseResponse>(`/cases/${id}`);
  },

  getEvidence: async (id: string): Promise<EvidenceResponse[]> => {
    // Assuming backend returns a list of evidence
    return fetchApi<EvidenceResponse[]>(`/cases/${id}/evidence`);
  },

  getHistory: async (id: string): Promise<HistoryResponse> => {
    return fetchApi<HistoryResponse>(`/cases/${id}/history`);
  },

  getInterventions: async (id: string): Promise<InterventionListResponse> => {
    return fetchApi<InterventionListResponse>(`/cases/${id}/interventions`);
  },

  getDecisionAnalysis: async (id: string): Promise<DecisionAnalysisResponse> => {
    return fetchApi<DecisionAnalysisResponse>(`/cases/${id}/analyze`, { method: 'POST' });
  },

  getPredictions: async (id: string): Promise<PredictionResponse[]> => {
    return fetchApi<PredictionResponse[]>(`/cases/${id}/predictions`);
  },
  
  getResolutionPlan: async (id: string): Promise<ResolutionPlanResponse> => {
    return fetchApi<ResolutionPlanResponse>(`/cases/${id}/plan`);
  }
};
