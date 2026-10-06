import { format } from "date-fns";
import { HistoryResponse } from "@/types/api";

export function HistoryView({ history, recurrenceCount }: { history?: HistoryResponse, recurrenceCount: number }) {

  return (
    <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-8 shadow-sm h-full max-w-3xl mx-auto w-full overflow-y-auto">
      <h2 className="text-sm font-bold uppercase tracking-wider text-slate-300 mb-8">What Happened Before?</h2>
      <div className="space-y-6">
        <div className="bg-slate-800/50 p-4 rounded-lg border border-slate-700/50">
          <div className="text-sm text-slate-400 mb-1">Total Previous Incidents</div>
          <div className="text-3xl font-light text-slate-200">{recurrenceCount || history?.historical_incidents?.length || 0}</div>
        </div>
        
        {history?.historical_incidents?.length ? (
          <div className="relative border-l-2 border-slate-700 ml-4 pl-6 py-2 space-y-8">
            {history.historical_incidents.map((inc, i) => (
              <div key={inc.incident_id} className="relative">
                <div className="absolute -left-[31px] top-1 w-4 h-4 bg-slate-800 border-2 border-slate-600 rounded-full" />
                <div className="text-xs text-slate-500 mb-1 font-mono">{format(new Date(inc.occurred_at), 'yyyy-MM-dd')}</div>
                <div className="text-sm font-bold text-slate-300 mb-1">{inc.title}</div>
                {inc.intervention_taken && (
                  <div className="text-xs text-blue-400 font-medium mb-1">Intervention: {inc.intervention_taken}</div>
                )}
                {inc.intervention_outcome && (
                  <div className="text-xs text-slate-400 mb-2">Outcome: {inc.intervention_outcome}</div>
                )}
                <div className="inline-block px-2 py-0.5 bg-slate-800 text-[10px] uppercase font-bold text-slate-500 rounded border border-slate-700">
                  {inc.data_truth.replace('_', ' ')}
                </div>
              </div>
            ))}
          </div>
        ) : (
           <div className="text-slate-500 italic text-sm">No historical incidents recorded.</div>
        )}
      </div>
    </div>
  );
}
