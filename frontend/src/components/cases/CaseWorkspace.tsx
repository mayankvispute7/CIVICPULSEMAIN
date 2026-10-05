"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { casesApi } from "@/services/api";
import { Loader2, AlertCircle, Map as MapIcon, Link as LinkIcon, History, FileText, ArrowRight } from "lucide-react";
import { FingerprintCard } from "./FingerprintCard";
import { EvidenceLedger } from "./EvidenceLedger";
import { InterventionLab } from "./InterventionLab";

export function CaseWorkspace({ caseId }: { caseId: string }) {
  const [activeTab, setActiveTab] = useState<'CHAIN' | 'EVIDENCE' | 'HISTORY' | 'OPTIONS'>('CHAIN');

  const { data: caseData, isLoading: isLoadingCase, error: caseError } = useQuery({
    queryKey: ['case', caseId],
    queryFn: () => casesApi.getCase(caseId),
  });

  if (isLoadingCase) {
    return (
      <div className="flex-1 flex items-center justify-center bg-[#0a0f1c] p-8 h-full">
        <div className="text-center">
          <Loader2 className="mx-auto h-8 w-8 text-blue-500 animate-spin" />
          <h3 className="mt-4 text-sm font-bold tracking-widest text-gray-200 uppercase">Loading Case Intelligence...</h3>
        </div>
      </div>
    );
  }

  if (caseError || !caseData) {
    return (
      <div className="flex-1 p-8 bg-[#0a0f1c] h-full">
        <div className="bg-red-900/20 p-4 rounded-lg border border-red-800 flex gap-3">
          <AlertCircle className="h-5 w-5 text-red-400 mt-0.5" />
          <div>
            <h3 className="text-sm font-medium text-red-300">Failed to load case</h3>
            <p className="text-sm text-red-400 mt-1">{(caseError as Error)?.message || "Unknown error"}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col h-[calc(100vh-64px)] bg-[#0a0f1c]">
      <div className="border-b border-slate-800 bg-slate-900/50 px-6 py-4 flex items-center justify-between shrink-0">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-bold uppercase tracking-wider text-blue-400">{caseData.case_id}</span>
            <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-slate-800 text-slate-400 border border-slate-700">
              {caseData.status}
            </span>
            <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-slate-800 text-slate-400 border border-slate-700 ml-2">
              {caseData.data_truth}
            </span>
          </div>
          <h1 className="text-2xl font-bold text-slate-100 tracking-tight">{caseData.title}</h1>
        </div>
        
        <div className="flex bg-slate-800/50 rounded-lg p-1 border border-slate-700/50">
          {[
            { id: 'CHAIN', label: 'Failure Chain', icon: LinkIcon },
            { id: 'EVIDENCE', label: 'Evidence', icon: FileText },
            { id: 'HISTORY', label: 'History', icon: History },
            { id: 'OPTIONS', label: 'Intervention Lab', icon: ArrowRight }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${
                activeTab === tab.id 
                  ? 'bg-blue-900/40 text-blue-400 shadow-sm border border-blue-800/50' 
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700/50 border border-transparent'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel: Fingerprint */}
        <div className="w-80 border-r border-slate-800 bg-[#0f172a] overflow-y-auto shrink-0 z-10 shadow-xl">
          <FingerprintCard caseData={caseData} />
        </div>

        {/* Center/Right Panel based on Tab */}
        <div className="flex-1 overflow-y-auto p-6 bg-[#0a0f1c]">
          {activeTab === 'CHAIN' && (
             <div className="h-full flex flex-col gap-6 max-w-4xl mx-auto">
               <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6 shadow-sm">
                 <h2 className="text-sm font-bold uppercase tracking-wider text-slate-300 mb-6">Evidence-Supported Hypothesis</h2>
                 
                 {/* Visual Failure Chain */}
                 <div className="flex items-center justify-center py-16">
                   {caseData.failure_chain ? (
                     <div className="flex items-center overflow-x-auto pb-4 custom-scrollbar">
                       {caseData.failure_chain.map((node: any, idx: number) => (
                         <div key={idx} className="flex items-center shrink-0">
                           <div className="bg-slate-800 border border-slate-700 rounded-lg p-4 text-center w-48 shadow-lg hover:border-blue-500/50 transition-colors">
                             <div className="font-mono text-slate-200 text-xs">{typeof node === 'string' ? node : (node && typeof node === 'object' ? String(node.node || node.name || 'Unknown') : 'Unknown')}</div>
                           </div>
                           {idx < caseData.failure_chain!.length - 1 && (
                             <div className="px-4">
                               <ArrowRight className="text-slate-600 w-6 h-6" />
                             </div>
                           )}
                         </div>
                       ))}
                     </div>
                   ) : (
                     <div className="text-slate-500 italic text-sm">No structured failure chain available.</div>
                   )}
                 </div>
               </div>
             </div>
          )}

          {activeTab === 'EVIDENCE' && (
            <EvidenceLedger caseId={caseId} />
          )}

          {activeTab === 'OPTIONS' && (
            <InterventionLab caseId={caseId} />
          )}
          
          {activeTab === 'HISTORY' && (
            <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6 shadow-sm h-full max-w-4xl mx-auto">
               <h2 className="text-sm font-bold uppercase tracking-wider text-slate-300 mb-4">Historical Context</h2>
               <p className="text-slate-500 text-sm">History timeline implementation...</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
