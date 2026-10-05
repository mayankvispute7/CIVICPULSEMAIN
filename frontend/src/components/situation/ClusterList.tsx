"use client";

import { useQuery } from "@tanstack/react-query";
import { clustersApi } from "@/services/api";
import { useRouter } from "next/navigation";
import { AlertTriangle, Clock, Activity, Target } from "lucide-react";

export function ClusterList() {
  const router = useRouter();
  const { data: clustersData, isLoading } = useQuery({
    queryKey: ['clusters'],
    queryFn: () => clustersApi.getClusters(),
  });

  return (
    <div className="h-full flex flex-col bg-[#0f172a] text-slate-300">
      <div className="p-4 border-b border-slate-800 bg-slate-900/50">
        <h2 className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-1">Active Situations</h2>
        <div className="text-2xl font-light text-slate-100">
          {isLoading ? "-" : clustersData?.total || 0} <span className="text-sm text-slate-500">CLUSTERS</span>
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto p-2 space-y-2 custom-scrollbar">
        {isLoading ? (
          <div className="p-4 text-center text-xs text-slate-500 animate-pulse">Scanning infrastructure...</div>
        ) : clustersData?.clusters?.length === 0 ? (
          <div className="p-4 text-center text-xs text-slate-500">No active clusters found.</div>
        ) : (
          clustersData?.clusters?.map((cluster) => (
            <div 
              key={cluster.cluster_id}
              onClick={() => router.push(`/cases/${cluster.cluster_id}`)}
              className="bg-slate-800/40 hover:bg-slate-800 p-3 rounded border border-slate-700/50 cursor-pointer transition-colors group"
            >
              <div className="flex justify-between items-start mb-2">
                <div className="text-[10px] font-mono text-blue-400">
                  {cluster.cluster_id.substring(0,8).toUpperCase()}
                </div>
                {cluster.confidence > 0.8 && (
                  <span className="flex h-2 w-2 relative mt-1">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500"></span>
                  </span>
                )}
              </div>
              
              <h3 className="text-sm font-semibold text-slate-100 mb-2 leading-tight group-hover:text-blue-300 transition-colors">
                {cluster.title}
              </h3>
              
              <div className="grid grid-cols-2 gap-2 text-xs border-t border-slate-700/50 pt-2 mt-2">
                <div>
                  <span className="text-slate-500 text-[9px] uppercase tracking-wider block">Complaints</span>
                  <span className="font-mono text-slate-200">{cluster.complaint_count}</span>
                </div>
                <div>
                  <span className="text-slate-500 text-[9px] uppercase tracking-wider block">Confidence</span>
                  <span className="font-mono text-emerald-400">{(cluster.confidence * 100).toFixed(0)}%</span>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
