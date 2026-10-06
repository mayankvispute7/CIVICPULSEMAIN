import { useState } from "react";
import { Loader2, Image as ImageIcon, ShieldCheck, Upload, AlertTriangle, CheckCircle2 } from "lucide-react";
import { format } from "date-fns";
import { VerificationResponse, FieldEvidenceResponse, WorkOrderResponse } from "@/types/api";
import { useMutation } from "@tanstack/react-query";
import { executionApi } from "@/services/api";
import { motion, AnimatePresence } from "framer-motion";

export function VerifyView({ 
  verification, 
  fieldEvidence = [],
  workOrder,
  caseId,
  onVerified
}: { 
  verification?: VerificationResponse, 
  fieldEvidence?: FieldEvidenceResponse[],
  workOrder?: WorkOrderResponse,
  caseId: string,
  onVerified?: () => void
}) {
  const [isSubmitting, setIsSubmitting] = useState(false);

  const submitEvidenceMutation = useMutation({
    mutationFn: async () => {
      if (!workOrder) throw new Error("No work order to submit evidence against");
      
      // Step 1: Submit mock field evidence
      await executionApi.submitFieldEvidence({
        work_order_id: workOrder.work_order_id,
        evidence_type: "POST_EXECUTION_IMAGE",
        captured_at: new Date().toISOString(),
        latitude: workOrder.location_lat || 18.5204,
        longitude: workOrder.location_lon || 73.8567,
        image_url: "https://images.unsplash.com/photo-1541888062-87000676451a?auto=format&fit=crop&q=80&w=600",
        metadata_info: {
          device: "Field Officer App v2.1",
          user: "officer_kothrud_01"
        }
      });
      
      // Step 2: Trigger automated verification
      return await executionApi.runVerification(workOrder.work_order_id);
    },
    onSuccess: () => {
      if (onVerified) onVerified();
      setIsSubmitting(false);
    },
    onError: () => {
      setIsSubmitting(false);
    }
  });

  const [isCapturing, setIsCapturing] = useState(false);
  
  const handleStartCapture = () => {
    setIsCapturing(true);
  };

  const handleVerify = () => {
    setIsSubmitting(true);
    submitEvidenceMutation.mutate();
  };

  return (
    <div className="flex flex-col gap-6 h-full max-w-5xl mx-auto w-full">
      <div className="bg-slate-900/80 backdrop-blur-sm border border-slate-800 rounded-xl p-8 shadow-xl">
        
        <div className="flex justify-between items-start mb-8">
          <div>
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-400 mb-1">Field Verification</h2>
            <h3 className="text-2xl font-black text-slate-100">Ensure Execution Integrity</h3>
            <p className="text-slate-500 mt-2">Automated consistency checks against field evidence and telemetry.</p>
          </div>
          {verification && (
            <div className="px-4 py-2 bg-emerald-900/30 text-emerald-400 border border-emerald-800 rounded-full font-bold uppercase tracking-wider text-xs flex items-center gap-2">
              <ShieldCheck className="w-4 h-4" /> Verified {verification.overall_consistency}
            </div>
          )}
        </div>
        
        {verification ? (
          <div className="space-y-8">
             <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="flex items-center gap-4 bg-emerald-950/40 border border-emerald-900/50 p-6 rounded-xl">
               <ShieldCheck className="w-10 h-10 text-emerald-500 shrink-0" />
               <div className="flex-1">
                 <div className="text-xl font-bold text-emerald-400 mb-1">Verification Completed</div>
                 <div className="text-sm text-emerald-200/70">
                   Automated systems confirmed execution matches plan. No manual review required.
                 </div>
               </div>
               <div className="text-right border-l border-emerald-900/50 pl-6">
                 <div className="text-xs uppercase font-bold text-emerald-500 mb-1">Confidence Score</div>
                 <div className="text-3xl font-black text-emerald-400">{(verification.confidence * 100).toFixed(0)}%</div>
               </div>
             </motion.div>
             
             <div>
               <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400 border-b border-slate-800 pb-2 mb-4 flex items-center gap-2">
                 <ImageIcon className="w-4 h-4" /> Submitted Field Evidence
               </h3>
               <div className="grid grid-cols-2 gap-6">
                  {fieldEvidence?.map((ev, i) => (
                    <motion.div 
                      initial={{ opacity: 0, scale: 0.95 }} 
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: i * 0.1 }}
                      key={ev.evidence_id} 
                      className="bg-slate-800/40 border border-slate-700/50 rounded-xl overflow-hidden flex flex-col shadow-lg"
                    >
                      <div className="h-48 bg-slate-900 flex items-center justify-center relative overflow-hidden group">
                        {ev.image_url ? (
                           <>
                             <img src={ev.image_url} alt="Field Evidence" className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105" />
                             <div className="absolute inset-0 bg-gradient-to-t from-slate-900 via-transparent to-transparent opacity-80" />
                           </>
                        ) : (
                           <ImageIcon className="w-8 h-8 text-slate-700" />
                        )}
                        <div className="absolute bottom-3 left-3 flex items-center gap-2">
                          <span className="px-2 py-1 bg-emerald-500 text-white rounded text-[10px] font-bold uppercase shadow-sm">
                            {ev.overall_consistency}
                          </span>
                        </div>
                      </div>
                      <div className="p-4 flex-1 flex flex-col justify-between">
                        <div>
                          <div className="text-sm font-bold text-slate-300 mb-1">Visual Match: {ev.visual_change}</div>
                          <div className="text-xs text-slate-500 mb-4">{format(new Date(ev.captured_at), 'PPP p')}</div>
                        </div>
                        <div className="space-y-2">
                          {ev.manipulation_indicators?.map((ind: string, idx: number) => (
                            <div key={idx} className="flex items-center gap-2 text-xs text-slate-400">
                              <CheckCircle2 className="w-3 h-3 text-emerald-500" /> {ind}
                            </div>
                          ))}
                        </div>
                      </div>
                    </motion.div>
                  ))}
               </div>
             </div>
          </div>
        ) : isCapturing ? (
          <motion.div initial={{opacity:0, scale:0.95}} animate={{opacity:1, scale:1}} className="max-w-md mx-auto">
             <div className="bg-slate-900 border border-slate-700 p-6 rounded-xl relative overflow-hidden">
                <div className="text-sm font-bold text-slate-300 mb-4 uppercase tracking-wider text-center">Field Officer App Simulator</div>
                <div className="aspect-video bg-black rounded-lg mb-4 relative flex items-center justify-center border border-slate-700 overflow-hidden">
                   <img src="https://images.unsplash.com/photo-1541888062-87000676451a?auto=format&fit=crop&q=80&w=600" alt="Camera viewfinder" className="w-full h-full object-cover opacity-80" />
                   <div className="absolute inset-0 border-2 border-white/20"></div>
                   <div className="absolute w-8 h-8 border-t-2 border-l-2 border-emerald-500 top-4 left-4"></div>
                   <div className="absolute w-8 h-8 border-t-2 border-r-2 border-emerald-500 top-4 right-4"></div>
                   <div className="absolute w-8 h-8 border-b-2 border-l-2 border-emerald-500 bottom-4 left-4"></div>
                   <div className="absolute w-8 h-8 border-b-2 border-r-2 border-emerald-500 bottom-4 right-4"></div>
                   
                   <div className="absolute bottom-2 right-2 bg-black/60 px-2 py-1 rounded text-[10px] text-emerald-400 font-mono">
                     {workOrder?.location_lat?.toFixed(4) || '18.5204'}, {workOrder?.location_lon?.toFixed(4) || '73.8567'}
                   </div>
                </div>
                
                <div className="space-y-3 mb-6">
                  <div className="flex items-center gap-2 text-xs text-slate-400 bg-slate-950 p-2 rounded">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500" /> GPS Location locked
                  </div>
                  <div className="flex items-center gap-2 text-xs text-slate-400 bg-slate-950 p-2 rounded">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500" /> Time-stamp verified
                  </div>
                </div>

                <button 
                  onClick={handleVerify}
                  disabled={isSubmitting}
                  className="w-full py-3 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-lg transition-colors flex items-center justify-center gap-2"
                >
                  {isSubmitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
                  {isSubmitting ? "Uploading Evidence..." : "Submit Field Report"}
                </button>
             </div>
          </motion.div>
        ) : (
          <div className="flex flex-col items-center justify-center py-20 text-center border-2 border-dashed border-slate-800 rounded-xl bg-slate-900/30">
             <Upload className="w-12 h-12 text-slate-600 mb-4" />
             <h3 className="text-xl font-bold text-slate-300 mb-2">Awaiting Field Submission</h3>
             <p className="text-slate-500 text-sm max-w-md mb-8">
               The on-ground team needs to submit post-execution photo evidence through the Field Officer app to proceed.
             </p>
             <button 
               onClick={handleStartCapture}
               disabled={!workOrder}
               className="px-6 py-3 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-800 disabled:text-slate-600 text-white font-bold rounded-lg transition-colors flex items-center gap-2 shadow-lg shadow-blue-900/20"
             >
               {workOrder ? 'Simulate Field Submission' : 'No Work Order Active'}
             </button>
          </div>
        )}
      </div>
    </div>
  );
}
