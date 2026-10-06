"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { casesApi, fetchApi } from "@/services/api";
import { Loader2, AlertCircle, ArrowRight, CheckCircle2, Circle, RotateCcw } from "lucide-react";
import { FingerprintCard } from "./FingerprintCard";
import { EvidenceLedger } from "./EvidenceLedger";
import { InterventionLab } from "./InterventionLab";
import { HistoryView } from "./HistoryView";
import { PredictView } from "./PredictView";
import { ExecuteView } from "./ExecuteView";
import { VerifyView } from "./VerifyView";
import { OutcomeView } from "./OutcomeView";
import { MemoryView } from "./MemoryView";
import { AnimatePresence, motion } from "framer-motion";

import { BeautifulImpactSummary } from "./BeautifulImpactSummary";

const STAGES = [
  { id: 'UNDERSTAND', label: 'Understand', short: 'What is happening?' },
  { id: 'INVESTIGATE', label: 'Investigate', short: 'What is connected?' },
  { id: 'HISTORY', label: 'History', short: 'What happened before?' },
  { id: 'PREDICT', label: 'Predict', short: 'What if we do nothing?' },
  { id: 'SIMULATE', label: 'Simulate', short: 'What can we do?' },
  { id: 'EXECUTE', label: 'Execute', short: 'How do we execute?' },
  { id: 'VERIFY', label: 'Verify', short: 'Did we do it?' },
  { id: 'OUTCOME', label: 'Outcome', short: 'Did it work?' },
  { id: 'MEMORY', label: 'Memory', short: 'What did we learn?' },
];

export function CaseWorkspace({ caseId }: { caseId: string }) {
  const queryClient = useQueryClient();
  const [currentStageIdx, setCurrentStageIdx] = useState(0);

  const { data: completeData, isLoading: isLoadingCase, error: caseError } = useQuery({
    queryKey: ['case-complete', caseId],
    queryFn: () => casesApi.getCaseComplete(caseId),
  });

  const caseData = completeData?.case;

  const resetMutation = useMutation({
    mutationFn: async () => {
      await fetchApi(`/cases/${caseData?.case_id || caseId}/reset-demo`, { method: "POST" });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['case-complete', caseId] });
      setCurrentStageIdx(0);
    }
  });

  const createPlanMutation = useMutation({
    mutationFn: async (interventionId: string) => {
      return await casesApi.createResolutionPlan(caseId, interventionId);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['case-complete', caseId] });
      // Move to Execute Stage
      const executeIdx = STAGES.findIndex(s => s.id === 'EXECUTE');
      if (executeIdx !== -1) setCurrentStageIdx(executeIdx);
    }
  });

  const handleReset = () => {
    resetMutation.mutate();
  };

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

  const currentStage = STAGES[currentStageIdx];
  const isPast = (idx: number) => idx < currentStageIdx;
  const isCurrent = (idx: number) => idx === currentStageIdx;

  const handleNext = () => {
    if (currentStageIdx < STAGES.length - 1) {
      setCurrentStageIdx(prev => prev + 1);
    }
  };

  return (
    <div className="flex-1 flex h-[calc(100vh-64px)] bg-[#0a0f1c]">
      {/* Workflow Rail */}
      <div className="w-64 border-r border-slate-800 bg-[#0f172a] p-6 flex flex-col shrink-0 overflow-y-auto">
        <h2 className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-6 pb-2 border-b border-slate-800">Case Workflow</h2>
        <div className="flex-1 flex flex-col gap-4">
          {STAGES.map((stage, idx) => (
            <button
              key={stage.id}
              onClick={() => setCurrentStageIdx(idx)}
              className={`flex items-start gap-3 text-left transition-all ${
                isCurrent(idx) ? 'opacity-100' : isPast(idx) ? 'opacity-60 hover:opacity-100' : 'opacity-40 hover:opacity-100'
              }`}
            >
              <div className="mt-0.5 shrink-0">
                {isPast(idx) ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                ) : isCurrent(idx) ? (
                  <div className="w-4 h-4 rounded-full bg-blue-500/20 border-2 border-blue-500 flex items-center justify-center">
                    <div className="w-1.5 h-1.5 rounded-full bg-blue-500" />
                  </div>
                ) : (
                  <Circle className="w-4 h-4 text-slate-600" />
                )}
              </div>
              <div>
                <div className={`text-sm font-bold ${isCurrent(idx) ? 'text-blue-400' : 'text-slate-300'}`}>
                  {stage.label}
                </div>
                {isCurrent(idx) && (
                  <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} className="text-xs text-slate-500 mt-1">
                    {stage.short}
                  </motion.div>
                )}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden relative">
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
          <div className="text-right">
             <div className="text-sm font-medium text-slate-400">Step {currentStageIdx + 1} of {STAGES.length}</div>
             <div className="text-lg font-bold text-slate-100">{currentStage.label}</div>
          </div>
        </div>

        <div className="flex-1 flex overflow-hidden">
          {/* Main Workspace */}
          <div className="flex-1 overflow-y-auto p-8 relative flex flex-col">
            <AnimatePresence mode="wait">
              <motion.div
                key={currentStage.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.2 }}
                className="flex-1 max-w-5xl mx-auto w-full flex flex-col gap-6"
              >
                {/* STAGE CONTENT */}
                {currentStage.id === 'UNDERSTAND' && (
                  <div className="grid grid-cols-2 gap-8 h-full">
                     <div className="flex flex-col gap-6">
                        <div className="bg-slate-900/50 p-6 rounded-xl border border-slate-800">
                           <h2 className="text-sm font-bold uppercase tracking-wider text-slate-300 mb-4">What is happening?</h2>
                           <BeautifulImpactSummary summary={caseData.impact_summary || ""} />
                        </div>
                        <div className="bg-slate-900/50 p-6 rounded-xl border border-slate-800">
                           <h2 className="text-sm font-bold uppercase tracking-wider text-slate-300 mb-4">Related Signals</h2>
                           <div className="flex flex-wrap gap-2">
                             {caseData.failure_chain?.map((c: any, i: number) => (
                               <span key={i} className="px-3 py-1 bg-slate-800 border border-slate-700 rounded-full text-sm text-slate-300">
                                 {typeof c === 'object' ? c.node : c}
                               </span>
                             ))}
                           </div>
                        </div>
                     </div>
                     <div className="bg-[#0f172a] rounded-xl border border-slate-800 overflow-hidden shadow-xl">
                       <FingerprintCard caseData={caseData} hypotheses={completeData?.failure_hypothesis} />
                     </div>
                  </div>
                )}

                {currentStage.id === 'INVESTIGATE' && (
                  <div className="flex flex-col gap-8 h-full">
                     <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6 shadow-sm">
                        <h2 className="text-sm font-bold uppercase tracking-wider text-slate-300 mb-6">Failure Chain</h2>
                        {/* Visual Failure Chain */}
                        <div className="flex items-center justify-center py-8">
                          {caseData.failure_chain ? (
                            <div className="flex items-center overflow-x-auto pb-4 custom-scrollbar">
                              {caseData.failure_chain.map((node: any, idx: number) => (
                                <div key={idx} className="flex items-center shrink-0">
                                  <div className="bg-slate-800 border border-slate-700 rounded-lg p-4 text-center w-40 shadow-lg hover:border-blue-500/50 cursor-pointer transition-colors">
                                    <div className="font-mono text-slate-200 text-xs font-semibold">{typeof node === 'string' ? node : (node && typeof node === 'object' ? String(node.node || node.name || 'Unknown') : 'Unknown')}</div>
                                    <div className="text-[9px] uppercase tracking-wider text-slate-500 mt-2">{node.type}</div>
                                  </div>
                                  {idx < caseData.failure_chain!.length - 1 && (
                                    <div className="px-3">
                                      <ArrowRight className="text-slate-600 w-5 h-5" />
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
                     <div className="flex-1 min-h-[400px]">
                        <EvidenceLedger evidence={completeData?.evidence || []} />
                     </div>
                  </div>
                )}

                {currentStage.id === 'HISTORY' && (
                  <HistoryView history={completeData?.history} recurrenceCount={caseData?.recurrence_count || 0} />
                )}

                {currentStage.id === 'PREDICT' && (
                  <PredictView caseId={caseData.case_id} history={completeData?.history} />
                )}

                {(currentStage.id === 'SIMULATE') && (
                  <div className="flex-1 min-h-[500px]">
                     <InterventionLab 
                       caseId={caseData.case_id}
                       interventions={completeData?.interventions || []} 
                       constraints={completeData?.constraints}
                       decision={completeData?.decision}
                       onApprove={(interventionId) => createPlanMutation.mutate(interventionId)}
                     />
                  </div>
                )}

                {currentStage.id === 'EXECUTE' && (
                  <ExecuteView roadmap={completeData?.roadmap} tasks={completeData?.tasks || []} workOrder={completeData?.work_order} />
                )}

                {currentStage.id === 'VERIFY' && (
                  <VerifyView 
                    verification={completeData?.verification} 
                    fieldEvidence={completeData?.field_evidence || []} 
                    workOrder={completeData?.work_order}
                    caseId={caseId}
                    onVerified={() => queryClient.invalidateQueries({ queryKey: ['case-complete', caseId] })}
                  />
                )}
                
                {currentStage.id === 'OUTCOME' && (
                  <OutcomeView 
                    outcome={completeData?.outcome} 
                    caseId={caseId}
                    workOrder={completeData?.work_order}
                    onLogged={() => queryClient.invalidateQueries({ queryKey: ['case-complete', caseId] })}
                  />
                )}

                {currentStage.id === 'MEMORY' && (
                  <MemoryView memory={completeData?.memory} />
                )}
              </motion.div>
            </AnimatePresence>

            {/* Bottom action bar */}
            <div className="mt-8 pt-4 border-t border-slate-800 flex justify-between shrink-0">
               <button 
                 onClick={handleReset}
                 disabled={resetMutation.isPending}
                 className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-sm font-semibold transition-colors border border-slate-700"
               >
                 <RotateCcw className={`w-4 h-4 ${resetMutation.isPending ? 'animate-spin' : ''}`} />
                 Reset Demo State
               </button>

               <button 
                 onClick={handleNext}
                 disabled={currentStageIdx === STAGES.length - 1}
                 className="flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg font-semibold transition-colors shadow-lg shadow-blue-900/20"
               >
                 {currentStageIdx === 0 ? "Start Investigation" : 
                  currentStageIdx === 3 ? "Explore Solutions" :
                  currentStageIdx === 5 ? "Verify Field Work" :
                  currentStageIdx === 6 ? "Record Outcome" :
                  currentStageIdx === 7 ? "Save to Infrastructure Memory" :
                  "Continue to " + (STAGES[currentStageIdx + 1]?.label || "")}
                 <ArrowRight className="w-4 h-4" />
               </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
