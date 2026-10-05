"use client";

import { useQuery } from "@tanstack/react-query";
import { clustersApi } from "@/services/api";

export function SituationHeader() {
  const { data } = useQuery({
    queryKey: ['clusters'],
    queryFn: () => clustersApi.getClusters(),
  });

  const total = data?.total || 0;
  
  // Calculate total complaints and high priority complaints from severity_distribution
  const totalComplaints = data?.clusters?.reduce((sum, c) => sum + c.complaint_count, 0) || 0;
  const highRisk = data?.clusters?.reduce((sum, c) => {
    const high = c.severity_distribution?.HIGH || 0;
    const critical = c.severity_distribution?.CRITICAL || 0;
    return sum + high + critical;
  }, 0) || 0;

  return (
    <div className="p-4 sm:p-6 border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 flex justify-between items-center z-10 shrink-0">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white tracking-tight uppercase">Baner Infrastructure Situation</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Real-time intelligence overlay on satellite map.</p>
      </div>
      <div className="flex gap-4">
        <div className="bg-gray-50 dark:bg-gray-800 px-4 py-2 rounded-lg border border-gray-200 dark:border-gray-700">
          <span className="text-xs uppercase font-semibold text-gray-500 block mb-1">Complaints</span>
          <span className="text-lg font-bold text-gray-900 dark:text-white">{!data ? '--' : totalComplaints}</span>
        </div>
        <div className="bg-gray-50 dark:bg-gray-800 px-4 py-2 rounded-lg border border-gray-200 dark:border-gray-700">
          <span className="text-xs uppercase font-semibold text-gray-500 block mb-1">Failure Clusters</span>
          <span className="text-lg font-bold text-gray-900 dark:text-white">{total === 0 && !data ? '--' : total}</span>
        </div>
        <div className="bg-gray-50 dark:bg-gray-800 px-4 py-2 rounded-lg border border-gray-200 dark:border-gray-700">
          <span className="text-xs uppercase font-semibold text-gray-500 block mb-1">High Priority</span>
          <span className="text-lg font-bold text-red-600 dark:text-red-400">{total === 0 && !data ? '--' : highRisk}</span>
        </div>
      </div>
    </div>
  );
}
