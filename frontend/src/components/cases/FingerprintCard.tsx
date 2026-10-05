import { FailureCaseResponse } from "@/types/api";
import { AlertTriangle, MapPin, BarChart3, Activity } from "lucide-react";

export function FingerprintCard({ caseData }: { caseData: FailureCaseResponse }) {
  return (
    <div className="p-6">
      <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-6 border-b border-slate-800 pb-2">Failure Fingerprint</h3>
      
      <div className="space-y-6">
        <div>
          <div className="flex items-center gap-2 mb-2 text-slate-300">
            <BarChart3 className="w-4 h-4 text-blue-400" />
            <span className="text-sm font-semibold tracking-wide">Magnitude</span>
          </div>
          <div className="grid grid-cols-2 gap-2">
            <div className="bg-slate-800/50 p-3 rounded border border-slate-700/50 hover:bg-slate-800 transition-colors">
              <div className="text-2xl font-light text-slate-100">{caseData.recurrence_count || '--'}</div>
              <div className="text-[9px] uppercase tracking-wider text-slate-500 mt-1">Historical Incidents</div>
            </div>
            <div className="bg-slate-800/50 p-3 rounded border border-slate-700/50 hover:bg-slate-800 transition-colors">
              <div className="text-2xl font-light text-emerald-400">{(caseData.confidence * 100).toFixed(0)}%</div>
              <div className="text-[9px] uppercase tracking-wider text-slate-500 mt-1">Confidence</div>
            </div>
          </div>
        </div>

        <div>
          <div className="flex items-center gap-2 mb-3 text-slate-300">
            <AlertTriangle className="w-4 h-4 text-orange-400" />
            <span className="text-sm font-semibold tracking-wide">Probable Characteristics</span>
          </div>
          <ul className="space-y-2">
            {caseData.fingerprint ? (
              Object.entries(caseData.fingerprint).map(([key, val]) => (
                <li key={key} className="text-sm flex items-start gap-3 p-2 bg-slate-800/30 rounded border border-slate-800 hover:border-slate-700 transition-colors">
                  <div className="w-1.5 h-1.5 rounded-full bg-orange-500 mt-1.5 shrink-0 shadow-[0_0_8px_rgba(249,115,22,0.8)]" />
                  <span className="text-slate-300">
                    <strong className="text-slate-100 uppercase text-[10px] tracking-wider mr-2">{key.replace(/_/g, ' ')}:</strong> 
                    <span className="font-mono text-xs">{typeof val === 'string' ? val : JSON.stringify(val)}</span>
                  </span>
                </li>
              ))
            ) : (
              <li className="text-xs text-slate-500 italic p-2">No structured fingerprint available</li>
            )}
          </ul>
        </div>

        <div>
          <div className="flex items-center gap-2 mb-2 text-slate-300 border-t border-slate-800 pt-6">
            <Activity className="w-4 h-4 text-purple-400" />
            <span className="text-sm font-semibold tracking-wide">Impact Summary</span>
          </div>
          <div className="text-sm text-slate-400 bg-slate-900/50 p-4 rounded border border-slate-800 leading-relaxed italic">
            "{caseData.impact_summary || 'No impact summary generated.'}"
          </div>
        </div>
      </div>
    </div>
  );
}
