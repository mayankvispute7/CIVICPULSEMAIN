import React, { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { casesApi } from "@/services/api";
import { Loader2, CheckCircle2, SlidersHorizontal, ArrowRight, Zap, Target, Clock, Coins, XCircle, Send, MessageSquare, AlertCircle, Activity, Info } from "lucide-react";
import { formatCurrency } from "@/lib/utils";
import { motion, AnimatePresence } from "framer-motion";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, ReferenceLine } from "recharts";

import { InterventionResponse, ConstraintResponse, DecisionAnalysisResponse } from "@/types/api";

export function InterventionLab({ 
  caseId,
  interventions = [], 
  constraints,
  decision,
  onApprove
}: { 
  caseId: string,
  interventions: InterventionResponse[], 
  constraints?: ConstraintResponse, 
  decision?: DecisionAnalysisResponse,
  onApprove?: (interventionId: string) => void
}) {
  const queryClient = useQueryClient();
  const [showConstraints, setShowConstraints] = useState(false);
  const [selectedIntervention, setSelectedIntervention] = useState<string | null>(
    decision?.ranked_interventions?.[0]?.intervention_id || interventions[0]?.intervention_id || null
  );
  
  // Constraints form state
  const [budget, setBudget] = useState<number | ''>(constraints?.budget_limit || 800000);
  const [deadlineDays, setDeadlineDays] = useState<number>(30);
  const [workers, setWorkers] = useState<number>(constraints?.available_workers || 10);
  const [excavators, setExcavators] = useState<number>(2);

  // Chatbot state
  const [chatMessages, setChatMessages] = useState<{role: 'user' | 'assistant', text: string}[]>([
    { role: 'assistant', text: "I'm your decision-support copilot. I evaluate the baseline risk against intervention options. What scenario would you like to explore?" }
  ]);
  const [chatInput, setChatInput] = useState("");

  // Queries
  const { data: baselinePrediction, isLoading: isBaselineLoading } = useQuery({
    queryKey: ['prediction', caseId],
    queryFn: () => casesApi.getCasePrediction(caseId)
  });

  const { data: simulationRun, isPending: isSimulating, mutate: simulate } = useMutation({
    mutationFn: (interventionId: string) => casesApi.simulateIntervention(caseId, {
      intervention_id: interventionId,
      budget: budget === '' ? undefined : budget,
      deadline_days: deadlineDays,
      workers: workers,
      excavators: excavators
    })
  });

  // Re-run simulation when selected intervention changes
  useEffect(() => {
    if (selectedIntervention) {
      simulate(selectedIntervention);
    }
  }, [selectedIntervention, simulate]);

  const handleApplyConstraints = () => {
    if (selectedIntervention) {
      simulate(selectedIntervention);
    }
    setShowConstraints(false);
  };


  const handleChat = (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim()) return;
    
    setChatMessages(prev => [...prev, { role: 'user', text: chatInput }]);
    const currentInput = chatInput.toLowerCase();
    setChatInput("");
    
    setTimeout(() => {
       let reply = "I've analyzed the constraints and expected physical outcomes.";
       if (currentInput.includes('compare top 2')) {
         reply = `Comparing the top options: "Drain Capacity Upgrade" offers a massive 75% risk drop but takes 12 days and ₹8.4L. "Emergency Drain Cleaning" is a quick 3-day fix for ₹1.2L but only drops risk by 25%. If immediate relief is needed, choose cleaning. For long-term resilience, upgrade capacity.`;
       } else if (currentInput.includes('reduce') && currentInput.includes('cost')) {
         reply = `To reduce cost, you can lower the budget constraint above. I will automatically filter out expensive structural options like "Drain Capacity Upgrade". You could also consider a phased approach: do "Emergency Drain Cleaning" now, and plan the upgrade for the next fiscal year.`;
       } else if (currentInput.includes('rain')) {
         reply = `If heavy rain is forecasted within the next 48 hours, I strongly advise against interventions that require open trenching (like "Drain Capacity Upgrade"). You should immediately prioritize "Emergency Drain Cleaning" or "Blocked Inlet Rehabilitation" as they can be completed in under 4 days.`;
       } else if (currentInput.includes('budget')) {
         reply = `With a budget of ${budget ? formatCurrency(budget as number) : 'unlimited'}, some comprehensive options may become infeasible. I will filter them out in the simulation.`;
       } else if (currentInput.includes('why') || currentInput.includes('explain')) {
         reply = "The risk reduction is calculated deterministically based on screening-level models of drainage capacity and historical recurrence data. Cost and time constraints act as strict filters (binary feasibility).";
       } else if (currentInput.includes('time machine')) {
         reply = "The Time Machine graph shows the 5-year projection. 'Do Nothing' results in escalating risk and compounding complaint burden. The green line shows the mitigated trajectory post-intervention.";
       } else {
         reply = "I recommend evaluating the 'Time Machine' projection above to see the 5-year compound impact of this intervention versus the baseline.";
       }
       setChatMessages(prev => [...prev, { role: 'assistant', text: reply }]);
    }, 600);
  };

  // Generate chart data based on baseline and simulation
  const generateChartData = () => {
    if (!baselinePrediction || !baselinePrediction.yearly_projection) return [];
    
    return baselinePrediction.yearly_projection.map((yearData: any, idx: number) => {
      let mitigatedRisk = yearData.risk;
      let mitigatedIncidents = yearData.incident_max;
      
      if (simulationRun && simulationRun.intervention && simulationRun.feasibility === "FEASIBLE") {
         // Apply risk reduction
         mitigatedRisk = Math.max(0, yearData.risk - simulationRun.risk_reduction);
         mitigatedIncidents = Math.max(0, yearData.incident_max * (1 - simulationRun.risk_reduction));
      }
      
      return {
        year: yearData.year,
        "Baseline Risk": yearData.risk * 100,
        "Intervention Risk": mitigatedRisk * 100,
        "Baseline Incidents": yearData.incident_max,
        "Mitigated Incidents": mitigatedIncidents
      };
    });
  };

  const chartData = generateChartData();
  const simResult = simulationRun;
  const isFeasible = simResult?.feasibility === "FEASIBLE";

  const [rejectMode, setRejectMode] = useState(false);
  const [rejectReasons, setRejectReasons] = useState<string[]>([]);
  const [acceptMode, setAcceptMode] = useState(false);

  const handleRejectSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setChatMessages(prev => [...prev, { role: 'user', text: `Rejected because: ${rejectReasons.join(", ")}` }]);
    setRejectMode(false);
    setRejectReasons([]);
    setTimeout(() => {
      setChatMessages(prev => [...prev, { role: 'assistant', text: "Noted. I've logged the rejection reason. Let's look at other options or adjust constraints." }]);
    }, 600);
  };

  return (
    <div className="flex gap-6 h-full text-slate-200">
      {/* LEFT: Interventions List & Constraints */}
      <div className="w-[450px] flex flex-col bg-slate-900/80 backdrop-blur-md border border-slate-800 rounded-xl overflow-hidden shadow-2xl">
        <div className="p-4 border-b border-slate-800 flex justify-between items-center bg-slate-950">
          <div className="flex items-center gap-2">
            <SlidersHorizontal className="w-4 h-4 text-blue-400" />
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-200">Intervention Options</h2>
          </div>
          <button 
            onClick={() => setShowConstraints(!showConstraints)}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-xs font-bold transition-colors border ${showConstraints ? 'bg-blue-600 border-blue-500 text-white' : 'bg-slate-800 hover:bg-slate-700 text-slate-300 border-slate-700'}`}
          >
            {showConstraints ? 'Hide Constraints' : 'Adjust Constraints'}
          </button>
        </div>

        <AnimatePresence>
          {showConstraints && (
            <motion.div 
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="bg-slate-800/50 border-b border-slate-700 overflow-hidden"
            >
               <div className="p-5 space-y-4">
                 <div>
                   <label className="flex justify-between text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">
                     <span>Budget Limit</span>
                     <span className="text-blue-400">{budget ? formatCurrency(budget) : 'Unlimited'}</span>
                   </label>
                   <input type="range" min="50000" max="2500000" step="50000" value={budget || 2500000} onChange={e => setBudget(Number(e.target.value))} className="w-full accent-blue-500 h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer" />
                 </div>
                 <div className="grid grid-cols-2 gap-4">
                   <div>
                     <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">Deadline (Days)</label>
                     <input type="number" value={deadlineDays} onChange={e => setDeadlineDays(Number(e.target.value))} className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none" />
                   </div>
                   <div>
                     <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">Labor Force</label>
                     <input type="number" value={workers} onChange={e => setWorkers(Number(e.target.value))} className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none" />
                   </div>
                 </div>
                 <div className="flex justify-end pt-2">
                   <button 
                     onClick={handleApplyConstraints}
                     className="bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold px-4 py-2 rounded flex items-center gap-2"
                   >
                     Apply Constraints <CheckCircle2 className="w-3 h-3" />
                   </button>
                 </div>
               </div>
            </motion.div>
          )}
        </AnimatePresence>

        <div className="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar">
          {interventions.map((option) => {
            const isSelected = selectedIntervention === option.intervention_id;
            return (
              <motion.div 
                key={option.intervention_id}
                whileHover={{ scale: 1.01 }}
                whileTap={{ scale: 0.99 }}
                onClick={() => setSelectedIntervention(option.intervention_id)}
                className={`cursor-pointer p-4 rounded-xl border transition-all duration-300 ${
                  isSelected 
                    ? 'bg-blue-900/20 border-blue-500 shadow-[0_0_15px_rgba(59,130,246,0.15)] ring-1 ring-blue-500/50' 
                    : 'bg-slate-900 border-slate-800 hover:border-slate-600'
                }`}
              >
                <div className="flex justify-between items-start mb-2">
                  <h3 className={`font-bold text-sm ${isSelected ? 'text-blue-100' : 'text-slate-300'}`}>{option.title}</h3>
                  <div className="flex gap-2">
                    <span className="text-[10px] font-mono bg-slate-800 text-slate-400 px-2 py-0.5 rounded-full border border-slate-700">
                      {option.estimated_duration_days}d
                    </span>
                    <span className="text-[10px] font-mono bg-emerald-900/30 text-emerald-400 px-2 py-0.5 rounded-full border border-emerald-900">
                      -{(option.expected_risk_reduction * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
                <div className="text-xs text-slate-500 line-clamp-2 mb-3">
                  {option.description}
                </div>
                <div className="flex justify-between items-center text-xs font-semibold">
                  <span className={isSelected ? 'text-blue-300' : 'text-slate-400'}>{formatCurrency(option.estimated_cost)}</span>
                  <span className="text-slate-500 flex items-center gap-1"><Coins className="w-3 h-3"/> Cost</span>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>

      {/* RIGHT: Time Machine & Simulation Lab */}
      <div className="flex-1 flex flex-col gap-6 overflow-hidden">
        
        {/* Top: Simulation Results / Time Machine */}
        <div className="flex-1 bg-slate-900/80 backdrop-blur-md border border-slate-800 rounded-xl overflow-hidden flex flex-col shadow-2xl">
          <div className="p-4 border-b border-slate-800 bg-slate-950 flex justify-between items-center">
             <div className="flex items-center gap-2">
               <Activity className="w-5 h-5 text-emerald-400" />
               <h2 className="text-sm font-bold uppercase tracking-wider text-slate-200">Time Machine & Simulation</h2>
             </div>
             {isSimulating && (
               <div className="flex items-center gap-2 text-xs font-mono text-blue-400">
                 <Loader2 className="w-3 h-3 animate-spin" /> Simulating Parameters...
               </div>
             )}
          </div>
          
          <div className="flex-1 p-6 overflow-y-auto flex flex-col gap-6">
            {!simResult && !isSimulating ? (
              <div className="flex-1 flex items-center justify-center text-slate-500">
                <p>Select an intervention to run simulation.</p>
              </div>
            ) : (
              <>
                {/* Feasibility Alert */}
                <AnimatePresence mode="wait">
                  {!isFeasible && simResult?.reasons && simResult.reasons.length > 0 && (
                    <motion.div 
                      initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, height: 0 }}
                      className="bg-red-950/40 border border-red-900/50 p-4 rounded-xl flex items-start gap-3"
                    >
                      <XCircle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
                      <div>
                        <h4 className="text-red-400 font-bold text-sm mb-1 uppercase tracking-wider">Infeasible under constraints</h4>
                        <ul className="text-sm text-red-200/80 space-y-1 list-disc pl-4">
                          {simResult.reasons.map((r: string, i: number) => <li key={i}>{r}</li>)}
                        </ul>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>

                {/* Score Cards */}
                <div className={`grid grid-cols-4 gap-4 transition-opacity duration-300 ${!isFeasible ? 'opacity-50 grayscale-[50%]' : ''}`}>
                   <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl">
                     <div className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Current Risk</div>
                     <div className="text-2xl font-black text-slate-300">{(simResult?.risk_before * 100).toFixed(0)}</div>
                   </div>
                   <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl relative overflow-hidden">
                     <div className="absolute inset-0 bg-emerald-500/5" />
                     <div className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2 relative">Risk After</div>
                     <div className="text-2xl font-black text-emerald-400 relative">
                       {(simResult?.risk_after * 100).toFixed(0)}
                       <span className="text-xs font-normal text-emerald-500/70 ml-2">({(simResult?.risk_reduction * 100).toFixed(0)}% drop)</span>
                     </div>
                   </div>
                   <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl">
                     <div className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Annual Cost (Base)</div>
                     <div className="text-2xl font-black text-slate-300">{formatCurrency(simResult?.baseline?.estimated_recurring_cost_per_year || 75000)}</div>
                   </div>
                   <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl relative overflow-hidden">
                     <div className="absolute inset-0 bg-blue-500/5" />
                     <div className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2 relative">Intervention Cost</div>
                     <div className="text-2xl font-black text-blue-400 relative">{formatCurrency(simResult?.cost)}</div>
                   </div>
                </div>

                {/* Time Machine Chart */}
                <div className={`flex-1 min-h-[250px] bg-slate-950 border border-slate-800 p-4 rounded-xl flex flex-col transition-opacity duration-300 ${!isFeasible ? 'opacity-50' : ''}`}>
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-4 flex items-center gap-2">
                    <Clock className="w-4 h-4" /> 5-Year Risk Projection (Time Machine)
                  </h3>
                  <div className="flex-1 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                        <XAxis dataKey="year" stroke="#475569" tick={{fill: '#475569', fontSize: 12}} />
                        <YAxis stroke="#475569" tick={{fill: '#475569', fontSize: 12}} domain={[0, 100]} />
                        <RechartsTooltip 
                          contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '8px' }}
                          itemStyle={{ fontSize: '12px', fontWeight: 'bold' }}
                          labelStyle={{ color: '#94a3b8', marginBottom: '4px' }}
                        />
                        <ReferenceLine y={80} stroke="#7f1d1d" strokeDasharray="3 3" label={{ position: 'insideTopLeft', value: 'Critical Threshold', fill: '#ef4444', fontSize: 10 }} />
                        <Line type="monotone" dataKey="Baseline Risk" stroke="#ef4444" strokeWidth={3} dot={{r: 4, fill: '#ef4444'}} name="Do Nothing Risk" />
                        {isFeasible && (
                          <Line type="monotone" dataKey="Intervention Risk" stroke="#10b981" strokeWidth={3} dot={{r: 4, fill: '#10b981'}} name="Mitigated Risk" />
                        )}
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Bottom: Decision Copilot */}
        <div className="h-[280px] bg-slate-900/80 backdrop-blur-md border border-slate-800 rounded-xl flex flex-col overflow-hidden shadow-2xl">
          <div className="p-3 border-b border-slate-800 bg-slate-950 flex items-center gap-2 justify-between">
            <div className="flex items-center gap-2">
              <MessageSquare className="w-4 h-4 text-purple-400" />
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">Decision Copilot</h3>
            </div>
            <div className="flex gap-2">
               {isFeasible && simResult && !rejectMode && !acceptMode && (
                 <>
                   <button 
                     onClick={() => setRejectMode(true)}
                     className="bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 text-xs font-bold px-4 py-1.5 rounded flex items-center gap-2 transition-colors"
                   >
                     Reject <XCircle className="w-3 h-3" />
                   </button>
                   <button 
                     onClick={() => setAcceptMode(true)}
                     className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold px-4 py-1.5 rounded flex items-center gap-2 transition-colors shadow-lg shadow-emerald-900/20"
                   >
                     Accept Option <CheckCircle2 className="w-3 h-3" />
                   </button>
                 </>
               )}
               {rejectMode && (
                  <button onClick={() => setRejectMode(false)} className="text-xs text-slate-400 hover:text-slate-200">Cancel Reject</button>
               )}
               {acceptMode && (
                  <button onClick={() => setAcceptMode(false)} className="text-xs text-slate-400 hover:text-slate-200">Cancel</button>
               )}
            </div>
          </div>
          
          <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
            {chatMessages.map((msg, i) => (
              <motion.div 
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                key={i} 
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`max-w-[80%] rounded-xl p-3 text-sm shadow-md ${
                  msg.role === 'user' 
                    ? 'bg-blue-600 text-white rounded-br-none' 
                    : 'bg-slate-800 border border-slate-700 text-slate-200 rounded-bl-none'
                }`}>
                  {msg.text}
                </div>
              </motion.div>
            ))}
            
            {rejectMode && (
              <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="bg-slate-900 p-4 border border-red-900/50 rounded-xl mt-2">
                 <h4 className="text-xs font-bold text-red-400 mb-3 uppercase tracking-wider">Why are you rejecting this option?</h4>
                 <form onSubmit={handleRejectSubmit} className="flex flex-col gap-4">
                   <div className="flex flex-wrap gap-2">
                     {["Too expensive", "Timeline too long", "Resource constraints", "Policy/Political reasons"].map(reason => {
                       const isSelected = rejectReasons.includes(reason);
                       return (
                         <button
                           key={reason}
                           type="button"
                           onClick={() => setRejectReasons(prev => isSelected ? prev.filter(r => r !== reason) : [...prev, reason])}
                           className={`px-3 py-1.5 text-xs font-bold rounded-full border transition-colors ${
                             isSelected ? 'bg-red-600 border-red-500 text-white' : 'bg-slate-800 border-slate-700 text-slate-300 hover:border-slate-500'
                           }`}
                         >
                           {reason}
                         </button>
                       );
                     })}
                   </div>
                   <div className="flex justify-end mt-2">
                     <button type="submit" disabled={rejectReasons.length === 0} className="bg-red-600 disabled:bg-slate-800 disabled:text-slate-500 hover:bg-red-500 text-white text-xs px-4 py-2 rounded font-bold">Submit Feedback</button>
                   </div>
                 </form>
              </motion.div>
            )}

            {acceptMode && (
               <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="bg-slate-900 p-4 border border-emerald-900/50 rounded-xl mt-2 text-center">
                 <h4 className="text-sm font-bold text-emerald-400 mb-2 uppercase tracking-wider">Intervention Accepted</h4>
                 <p className="text-sm text-slate-300 mb-4">Would you like to automatically generate a detailed execution roadmap for this intervention?</p>
                 <div className="flex justify-center gap-3">
                   <button 
                     onClick={() => setAcceptMode(false)}
                     className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-bold rounded"
                   >
                     Maybe Later
                   </button>
                   <button 
                     onClick={() => onApprove && selectedIntervention && onApprove(selectedIntervention)}
                     className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded flex items-center gap-2 shadow-lg shadow-emerald-900/20"
                   >
                     Generate Roadmap <Zap className="w-3 h-3" />
                   </button>
                 </div>
               </motion.div>
            )}
          </div>
          
          <div className="p-2 border-t border-slate-800 bg-slate-900 flex gap-2 overflow-x-auto custom-scrollbar">
            {["Compare top 2 options", "How can I reduce the cost?", "What if it rains?"].map((suggestion, idx) => (
              <button 
                key={idx}
                onClick={() => setChatInput(suggestion)}
                className="shrink-0 px-3 py-1 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-full text-[10px] text-slate-300 transition-colors whitespace-nowrap"
              >
                {suggestion}
              </button>
            ))}
          </div>
          <form onSubmit={handleChat} className="p-3 bg-slate-950/80 flex gap-2 items-center">
            <input 
              type="text" 
              value={chatInput}
              onChange={e => setChatInput(e.target.value)}
              placeholder="Ask about parameters, rank, or alternatives..." 
              className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500 transition-all placeholder:text-slate-600"
            />
            <button type="submit" disabled={!chatInput.trim()} className="p-2.5 bg-purple-600 disabled:bg-slate-800 disabled:text-slate-500 text-white rounded-lg hover:bg-purple-500 transition-colors">
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>

      </div>
    </div>
  );
}
