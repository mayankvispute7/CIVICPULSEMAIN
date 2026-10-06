import { fetchApi } from './client';
import { 
  FailureCaseListResponse, 
  FailureCaseResponse, 
  EvidenceResponse,
  HistoryResponse,
  InterventionListResponse,
  DecisionAnalysisResponse,
  PredictionResponse,
  ResolutionPlanResponse,
  CaseCompleteResponse
} from '@/types/api';

export const casesApi = {
  getCases: async (skip = 0, limit = 50): Promise<FailureCaseListResponse> => {
    return fetchApi<FailureCaseListResponse>(`/cases?skip=${skip}&limit=${limit}`);
  },

  getCase: async (id: string): Promise<FailureCaseResponse> => {
    return fetchApi<FailureCaseResponse>(`/cases/${id}`);
  },

  getCaseComplete: async (id: string): Promise<CaseCompleteResponse> => {
    return fetchApi<CaseCompleteResponse>(`/cases/${id}/complete`);
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

  updateConstraints: async (id: string, constraints: any): Promise<any> => {
    return fetchApi<any>(`/cases/${id}/constraints`, { 
      method: 'POST',
      body: JSON.stringify(constraints)
    });
  },

  getPredictions: async (id: string): Promise<PredictionResponse[]> => {
    return fetchApi<PredictionResponse[]>(`/cases/${id}/predictions`);
  },
  
  getResolutionPlan: async (id: string): Promise<ResolutionPlanResponse> => {
    return fetchApi<ResolutionPlanResponse>(`/cases/${id}/plan`);
  },

  getCostOfInaction: async (id: string): Promise<any> => {
    return fetchApi<any>(`/cases/${id}/cost-of-inaction`);
  },

  getCounterfactual: async (id: string): Promise<any> => {
    return fetchApi<any>(`/cases/${id}/counterfactual`);
  },

  getCasePrediction: async (id: string): Promise<any> => {
    return fetchApi<any>(`/cases/${id}/prediction`);
  },

  simulateIntervention: async (id: string, request: any): Promise<any> => {
    return fetchApi<any>(`/cases/${id}/simulate`, {
      method: 'POST',
      body: JSON.stringify(request)
    });
  },

  getSimulationRuns: async (id: string): Promise<any[]> => {
    return fetchApi<any[]>(`/cases/${id}/simulation/runs`);
  },

  updateSimulationConstraints: async (id: string, request: any): Promise<any> => {
    return fetchApi<any>(`/cases/${id}/simulation/constraints`, {
      method: 'POST',
      body: JSON.stringify(request)
    });
  },

  createResolutionPlan: async (id: string, interventionId: string): Promise<any> => {
    return fetchApi<any>(`/cases/${id}/plan/${interventionId}`, {
      method: 'POST'
    });
  }
};
