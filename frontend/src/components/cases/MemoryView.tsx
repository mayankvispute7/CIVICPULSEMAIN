import { BrainCircuit, CheckCircle2 } from "lucide-react";
import { InfrastructureMemoryResponse } from "@/types/api";

export function MemoryView({ memory }: { memory?: InfrastructureMemoryResponse }) {

  return (
    <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-8 shadow-sm h-full max-w-4xl mx-auto w-full overflow-y-auto">
      <div className="flex items-center gap-3 mb-8 border-b border-slate-800 pb-4">
         <BrainCircuit className="w-6 h-6 text-purple-400" />
         <h2 className="text-lg font-bold uppercase tracking-wider text-slate-200">Infrastructure Memory</h2>
      </div>
      
      {memory ? (
        <div className="space-y-6">
           <div className="text-slate-300 text-lg leading-relaxed">
             "{memory.summary}"
           </div>
           
           <div className="grid grid-cols-3 gap-4 mt-8">
              <div className="bg-slate-800/50 p-4 rounded-lg border border-slate-700 text-center">
                 <div className="text-3xl font-light text-slate-200">{memory.total_complaints}</div>
                 <div className="text-xs text-slate-500 uppercase tracking-wider mt-1">Total Complaints</div>
              </div>
              <div className="bg-slate-800/50 p-4 rounded-lg border border-slate-700 text-center">
                 <div className="text-3xl font-light text-slate-200">{memory.total_interventions}</div>
                 <div className="text-xs text-slate-500 uppercase tracking-wider mt-1">Total Interventions</div>
              </div>
              <div className="bg-slate-800/50 p-4 rounded-lg border border-slate-700 text-center">
                 <div className="text-3xl font-light text-slate-200">{memory.total_recurrences}</div>
                 <div className="text-xs text-slate-500 uppercase tracking-wider mt-1">Recurrences</div>
              </div>
           </div>

           <div className="mt-8">
              <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400 mb-4">Learned Patterns</h3>
              <ul className="space-y-3">
                 {memory.learned_patterns?.map((pattern, idx) => (
                    <li key={idx} className="flex gap-3 text-slate-300 bg-slate-800/30 p-3 rounded-lg border border-slate-700/50">
                       <CheckCircle2 className="w-5 h-5 text-purple-400 shrink-0" />
                       <span className="text-sm">{pattern}</span>
                    </li>
                 ))}
              </ul>
           </div>
           <div className="grid grid-cols-2 gap-6 mt-8">
              <div className="bg-red-950/20 p-6 rounded-xl border border-red-900/30">
                 <h3 className="text-sm font-bold uppercase tracking-wider text-red-400 mb-4">Mistakes Identified</h3>
                 <ul className="space-y-3">
                    <li className="flex gap-3 text-red-200/80">
                       <span className="text-red-500 font-bold">-</span>
                       <span className="text-sm">Previous intervention underestimated soil saturation limits during peak monsoon.</span>
                    </li>
                    <li className="flex gap-3 text-red-200/80">
                       <span className="text-red-500 font-bold">-</span>
                       <span className="text-sm">Cost baseline was missing factoring for rapid-deployment emergency labor.</span>
                    </li>
                 </ul>
              </div>
              <div className="bg-blue-950/20 p-6 rounded-xl border border-blue-900/30">
                 <h3 className="text-sm font-bold uppercase tracking-wider text-blue-400 mb-4">Considerations for Next Time</h3>
                 <ul className="space-y-3">
                    <li className="flex gap-3 text-blue-200/80">
                       <span className="text-blue-500 font-bold">+</span>
                       <span className="text-sm">Automatically add 15% to budget constraint for pre-monsoon execution windows.</span>
                    </li>
                    <li className="flex gap-3 text-blue-200/80">
                       <span className="text-blue-500 font-bold">+</span>
                       <span className="text-sm">Prioritize solutions with 'Drain Capacity Upgrade' over temporary patching for this specific soil type.</span>
                    </li>
                 </ul>
              </div>
           </div>
        </div>
      ) : (
         <div className="text-slate-500 italic text-sm">No memory data established for this location yet.</div>
      )}
    </div>
  );
}
