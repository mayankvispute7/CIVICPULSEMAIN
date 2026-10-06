import { useState } from "react";
import { TrendingDown, Loader2, CloudRain, CheckCircle2, AlertTriangle, CloudLightning } from "lucide-react";
import { OutcomeResponse, WorkOrderResponse } from "@/types/api";
import { useMutation } from "@tanstack/react-query";
import { outcomesApi } from "@/services/api";
import { motion, AnimatePresence } from "framer-motion";
import { format } from "date-fns";

export function OutcomeView({ 
  outcome, 
  caseId,
  workOrder,
  onLogged
}: { 
  outcome?: OutcomeResponse,
  caseId: string,
  workOrder?: WorkOrderResponse,
  onLogged?: () => void
}) {
  const [triggerEvent, setTriggerEvent] = useState("Monsoon 2026 Phase 1");
  
  const submitOutcomeMutation = useMutation({
    mutationFn: async () => {
      await outcomesApi.logOutcome({
        case_id: caseId,
        work_order_id: workOrder?.work_order_id,
        observed_at: new Date().toISOString(),
        status: "IMPROVED",
        trigger_event: triggerEvent,
        trigger_event_details: {
          rainfall_mm_per_hr: 45,
          duration_hours: 3
        },
        observed_conditions: {
          before_complaints: 12,
          after_complaints: 0,
          waterlogging_duration_mins: 15
        },
        complaints_during_event: 0,
        notes: "Post-intervention monitoring shows no severe waterlogging during peak monsoon burst."
      });
    },
    onSuccess: () => {
      if (onLogged) onLogged();
    }
  });

  const isSubmitting = submitOutcomeMutation.isPending;

  const handleSimulateObservation = () => {
    submitOutcomeMutation.mutate();
  };

  return (
    <div className="flex flex-col gap-6 h-full max-w-5xl mx-auto w-full">
      <div className="bg-slate-900/80 backdrop-blur-sm border border-slate-800 rounded-xl p-8 shadow-xl">
        
        <div className="flex justify-between items-start mb-8">
          <div>
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-400 mb-1">Impact Analysis</h2>
            <h3 className="text-2xl font-black text-slate-100">Did It Work?</h3>
            <p className="text-slate-500 mt-2">Correlating post-intervention real-world telemetry with the original predicted baseline.</p>
          </div>
          {outcome && (
            <div className="px-4 py-2 bg-emerald-900/30 text-emerald-400 border border-emerald-800 rounded-full font-bold uppercase tracking-wider text-xs flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4" /> Validated: {outcome.status}
            </div>
          )}
        </div>
        
        {outcome ? (
          <div className="space-y-8">
             <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="flex gap-4">
                <div className="flex-1 bg-slate-950/50 border border-slate-800 p-6 rounded-xl text-center relative overflow-hidden group">
                   <div className="absolute inset-0 bg-red-500/5 opacity-0 group-hover:opacity-100 transition-opacity" />
                   <div className="text-sm font-bold uppercase tracking-wider text-slate-500 mb-4">Historical Baseline</div>
                   <div className="text-5xl font-black text-slate-200 mb-2">{outcome.observed_conditions?.before_complaints || 0}</div>
                   <div className="text-xs text-slate-500">Peak Complaints</div>
                </div>
                
                <div className="flex-1 bg-slate-950/50 border border-blue-900/50 p-6 rounded-xl text-center relative overflow-hidden group shadow-[0_0_20px_rgba(59,130,246,0.1)]">
                   <div className="absolute top-0 left-0 w-full h-1 bg-blue-500" />
                   <div className="absolute inset-0 bg-blue-500/5 opacity-0 group-hover:opacity-100 transition-opacity" />
                   
                   <div className="text-sm font-bold uppercase tracking-wider text-blue-400 mb-4 flex justify-center items-center gap-2">
                     <CloudLightning className="w-4 h-4" /> {outcome.trigger_event}
                   </div>
                   
                   <div className="text-5xl font-black text-blue-400 flex items-center justify-center gap-4 mb-2">
                      {outcome.observed_conditions?.after_complaints || 0}
                      <TrendingDown className="w-8 h-8 text-blue-500" />
                   </div>
                   <div className="text-xs text-slate-400">Complaints Logged</div>
                </div>
             </motion.div>
             
             <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.1 }} className="bg-slate-950/30 p-6 rounded-xl border border-slate-800 flex items-start gap-6">
                <div className="p-4 bg-emerald-500/10 rounded-xl shrink-0">
                   <CloudRain className="w-8 h-8 text-emerald-500" />
                </div>
                <div className="flex-1">
                   <h4 className="text-lg font-bold text-slate-200 mb-2">Observation Notes</h4>
                   <p className="text-slate-400 text-sm leading-relaxed mb-4">{outcome.notes}</p>
                   
                   <div className="grid grid-cols-2 gap-4">
                     <div className="bg-slate-900 p-3 rounded-lg border border-slate-800">
                       <div className="text-xs text-slate-500 uppercase font-bold mb-1">Observed On</div>
                       <div className="text-sm text-slate-300 font-mono">{format(new Date(outcome.observed_at), 'MMM d, yyyy - HH:mm')}</div>
                     </div>
                     <div className="bg-slate-900 p-3 rounded-lg border border-slate-800">
                       <div className="text-xs text-slate-500 uppercase font-bold mb-1">Data Truth Level</div>
                       <div className="text-sm text-blue-400 font-mono">{outcome.data_truth}</div>
                     </div>
                   </div>
                </div>
             </motion.div>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-20 text-center border-2 border-dashed border-slate-800 rounded-xl bg-slate-900/30">
            {isSubmitting ? (
              <>
                <Loader2 className="w-12 h-12 animate-spin text-blue-500 mb-4" />
                <h3 className="text-xl font-bold text-slate-300 mb-2">Compiling Telemetry...</h3>
                <p className="text-slate-500 text-sm max-w-sm">Correlating recent rainfall events with incoming complaints and IoT sensor data.</p>
              </>
            ) : (
              <>
                <CloudRain className="w-12 h-12 text-slate-600 mb-4" />
                <h3 className="text-xl font-bold text-slate-300 mb-2">Waiting for Trigger Event</h3>
                <p className="text-slate-500 text-sm max-w-md mb-6">
                  The true test of the intervention happens during the next significant weather event.
                </p>
                
                <div className="w-full max-w-xs mb-8">
                  <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 text-left">Select Simulation Trigger</label>
                  <select 
                    value={triggerEvent}
                    onChange={(e) => setTriggerEvent(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-sm text-slate-200 outline-none focus:border-blue-500"
                  >
                    <option value="Monsoon 2026 Phase 1">Monsoon 2026 - Phase 1</option>
                    <option value="Cyclone Warning (Red Alert)">Cyclone Warning (Red Alert)</option>
                    <option value="Unseasonal Heavy Downpour">Unseasonal Heavy Downpour</option>
                  </select>
                </div>
                <button 
                  onClick={handleSimulateObservation}
                  disabled={isSubmitting}
                  className="px-6 py-3 bg-blue-600 hover:bg-blue-500 disabled:bg-blue-800 text-white font-bold rounded-lg transition-colors flex items-center justify-center gap-2 shadow-lg shadow-blue-900/20"
                >
                  {isSubmitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4 fill-white" />}
                  {isSubmitting ? "Compiling Telemetry..." : "Fast-Forward & Log Observation"}
                </button>
                {submitOutcomeMutation.isError && (
                  <div className="mt-4 p-3 bg-red-950/30 border border-red-900/50 rounded-lg flex items-center justify-center gap-2 text-red-400 text-sm">
                    <AlertTriangle className="w-4 h-4 text-red-500" /> Observation failed to log. Please try again.
                  </div>
                )}
              </>
            )}
          </div>
        )}

        {/* Complaint Lifecycle visualization */}
        {outcome && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="mt-8 pt-8 border-t border-slate-800">
             <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400 mb-6 flex items-center gap-2">
               Incident Lifecycle Trace
             </h3>
             <div className="relative flex justify-between items-center px-4">
                <div className="absolute left-8 right-8 top-4 h-0.5 bg-slate-800 z-0"></div>
                <div className="absolute left-8 right-[20%] top-4 h-0.5 bg-blue-500 z-0"></div>
                
                {[
                  { title: "Ingested", detail: "Multi-modal clustering", done: true },
                  { title: "Investigated", detail: "Failure fingerprint mapped", done: true },
                  { title: "Planned", detail: "Constraint-based simulation", done: true },
                  { title: "Executed", detail: "Verified by field telemetry", done: true },
                  { title: "Validated", detail: "Real-world outcome proven", done: true }
                ].map((step, idx) => (
                  <div key={idx} className="relative z-10 flex flex-col items-center group w-24">
                     <div className={`w-8 h-8 rounded-full border-4 flex items-center justify-center bg-slate-900 transition-colors ${step.done ? 'border-blue-500 text-blue-500' : 'border-slate-700 text-slate-600'}`}>
                        {step.done ? <CheckCircle2 className="w-4 h-4" /> : <div className="w-2 h-2 rounded-full bg-slate-700"></div>}
                     </div>
                     <div className="mt-3 text-center">
                        <div className={`text-xs font-bold uppercase tracking-wider ${step.done ? 'text-slate-300' : 'text-slate-500'}`}>{step.title}</div>
                        <div className="text-[9px] text-slate-500 mt-1 opacity-0 group-hover:opacity-100 transition-opacity absolute w-32 -left-4">{step.detail}</div>
                     </div>
                  </div>
                ))}
             </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}

// Inline icon component since it wasn't imported from lucide-react above
const Play = ({ className }: { className?: string }) => (
  <svg className={className} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="5 3 19 12 5 21 5 3"/></svg>
);
