"use client";

import { useQuery } from "@tanstack/react-query";
import { complaintsApi } from "@/services/api";
import { BarChart3, AlertOctagon, TrendingUp, Filter } from "lucide-react";

export function CityMetrics() {
  const { data: complaintsData, isLoading } = useQuery({
    queryKey: ['complaints_summary'],
    queryFn: () => complaintsApi.getComplaints(1, 100), // Quick fetch to get totals
  });

  return (
    <div className="h-full flex flex-col bg-[#0f172a] text-slate-300 border-l border-slate-800">
      <div className="p-4 border-b border-slate-800 bg-slate-900/50">
        <h2 className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-1">City Overview</h2>
        <div className="text-2xl font-light text-slate-100">
          {isLoading ? "-" : complaintsData?.total || 0} <span className="text-sm text-slate-500">SIGNALS</span>
        </div>
      </div>
      
      <div className="flex-1 p-4 space-y-6 overflow-y-auto custom-scrollbar">
        
        {/* Metric Block */}
        <div>
          <div className="flex items-center text-xs font-bold uppercase tracking-wider text-slate-500 mb-3">
            <AlertOctagon className="w-4 h-4 mr-2 text-slate-400" />
            Vulnerability Index
          </div>
          <div className="bg-slate-800/40 rounded p-4 border border-slate-700/50">
            <div className="flex justify-between items-end mb-2">
              <span className="text-3xl font-light text-red-400">High</span>
              <span className="text-xs text-slate-400 mb-1 font-mono">Top 15%</span>
            </div>
            <div className="w-full bg-slate-900 h-1.5 rounded-full overflow-hidden">
              <div className="bg-gradient-to-r from-orange-500 to-red-500 h-full w-[85%]"></div>
            </div>
          </div>
        </div>

        {/* Metric Block */}
        <div>
          <div className="flex items-center text-xs font-bold uppercase tracking-wider text-slate-500 mb-3">
            <TrendingUp className="w-4 h-4 mr-2 text-slate-400" />
            Primary Categories
          </div>
          <div className="space-y-3">
            <div className="bg-slate-800/40 rounded p-3 border border-slate-700/50">
              <div className="flex justify-between text-sm mb-1">
                <span className="text-slate-200">Waterlogging</span>
                <span className="font-mono text-blue-400">68%</span>
              </div>
              <div className="w-full bg-slate-900 h-1 rounded-full overflow-hidden">
                <div className="bg-blue-500 h-full w-[68%]"></div>
              </div>
            </div>
            
            <div className="bg-slate-800/40 rounded p-3 border border-slate-700/50">
              <div className="flex justify-between text-sm mb-1">
                <span className="text-slate-200">Drainage</span>
                <span className="font-mono text-blue-400">22%</span>
              </div>
              <div className="w-full bg-slate-900 h-1 rounded-full overflow-hidden">
                <div className="bg-blue-600 h-full w-[22%]"></div>
              </div>
            </div>
          </div>
        </div>

        {/* Filters Placeholder */}
        <div className="pt-4 border-t border-slate-800">
          <div className="flex items-center text-xs font-bold uppercase tracking-wider text-slate-500 mb-3">
            <Filter className="w-4 h-4 mr-2 text-slate-400" />
            Quick Filters
          </div>
          <div className="flex flex-wrap gap-2">
            <span className="px-2 py-1 bg-slate-800 text-[10px] text-slate-300 rounded border border-slate-700 cursor-pointer hover:bg-slate-700">HIGH SEVERITY</span>
            <span className="px-2 py-1 bg-slate-800 text-[10px] text-slate-300 rounded border border-slate-700 cursor-pointer hover:bg-slate-700">LAST 24H</span>
            <span className="px-2 py-1 bg-slate-800 text-[10px] text-slate-300 rounded border border-slate-700 cursor-pointer hover:bg-slate-700">UNASSIGNED</span>
          </div>
        </div>

      </div>
    </div>
  );
}
