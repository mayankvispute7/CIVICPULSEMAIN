import { fetchApi } from './client';
import { ClusterListResponse, ClusterResponse, ClusteringResultResponse } from '@/types/api';

export const clustersApi = {
  getClusters: async (skip = 0, limit = 50): Promise<ClusterListResponse> => {
    return fetchApi<ClusterListResponse>(`/complaints/clusters/all`);
  },

  getCluster: async (id: string): Promise<ClusterResponse> => {
    return fetchApi<ClusterResponse>(`/complaints/clusters/${id}`);
  },

  runClustering: async (): Promise<ClusteringResultResponse> => {
    return fetchApi<ClusteringResultResponse>('/complaints/cluster', {
      method: 'POST',
    });
  }
};
