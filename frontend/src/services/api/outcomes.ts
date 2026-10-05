import { fetchApi } from './client';
import { 
  OutcomeResponse, 
  PredictionRealityResponse, 
  LearningRecordResponse, 
  InfrastructureMemoryResponse 
} from '@/types/api';

export const outcomesApi = {
  getOutcomesForCase: async (caseId: string): Promise<OutcomeResponse[]> => {
    return fetchApi<OutcomeResponse[]>(`/outcomes/cases/${caseId}`);
  },

  getComparisons: async (caseId: string): Promise<PredictionRealityResponse[]> => {
    return fetchApi<PredictionRealityResponse[]>(`/outcomes/cases/${caseId}/comparisons`);
  },

  getLearnings: async (caseId: string): Promise<LearningRecordResponse[]> => {
    return fetchApi<LearningRecordResponse[]>(`/outcomes/cases/${caseId}/learnings`);
  },

  getMemory: async (siteId: string): Promise<InfrastructureMemoryResponse> => {
    return fetchApi<InfrastructureMemoryResponse>(`/outcomes/sites/${siteId}/memory`);
  }
};
