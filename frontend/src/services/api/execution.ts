import { fetchApi } from './client';
import { 
  WorkOrderResponse, 
  TaskResponse, 
  FieldEvidenceResponse,
  VerificationResponse,
  ReplanEventResponse
} from '@/types/api';

export const executionApi = {
  getWorkOrders: async (skip = 0, limit = 50): Promise<WorkOrderResponse[]> => {
    return fetchApi<WorkOrderResponse[]>(`/execution/work-orders?skip=${skip}&limit=${limit}`);
  },

  getWorkOrder: async (id: string): Promise<WorkOrderResponse> => {
    return fetchApi<WorkOrderResponse>(`/execution/work-orders/${id}`);
  },

  getTasks: async (workOrderId: string): Promise<TaskResponse[]> => {
    return fetchApi<TaskResponse[]>(`/execution/work-orders/${workOrderId}/tasks`);
  },

  getFieldEvidence: async (workOrderId: string): Promise<FieldEvidenceResponse[]> => {
    return fetchApi<FieldEvidenceResponse[]>(`/execution/work-orders/${workOrderId}/evidence`);
  },

  getVerification: async (workOrderId: string): Promise<VerificationResponse> => {
    return fetchApi<VerificationResponse>(`/execution/work-orders/${workOrderId}/verification`);
  },
  
  getReplanEvents: async (workOrderId: string): Promise<ReplanEventResponse[]> => {
    return fetchApi<ReplanEventResponse[]>(`/execution/work-orders/${workOrderId}/replans`);
  }
};
