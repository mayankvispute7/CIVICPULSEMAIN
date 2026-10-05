"use client";

import { useQuery } from "@tanstack/react-query";
import { casesApi } from "@/services/api";
import { 
  Loader2, 
  ShieldCheck, 
  Database, 
  Camera, 
  CloudRain, 
  AlertTriangle, 
  FileText,
  Layers,
  Activity,
  Info
} from "lucide-react";

export function EvidenceLedger({ caseId }: { caseId: string }) {
  const { data: evidence, isLoading, error } = useQuery({
    queryKey: ['case-evidence', caseId],
    queryFn: () => casesApi.getEvidence(caseId),
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-16">
        <div className="text-center">
          <Loader2 className="mx-auto h-8 w-8 text-blue-500 animate-spin" />
          <p className="mt-3 text-xs uppercase tracking-wider font-semibold text-slate-400">Loading evidence audit trail...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6 text-center text-slate-400">
        <AlertTriangle className="mx-auto h-8 w-8 text-amber-500 mb-2" />
        <p className="text-sm font-medium text-slate-200">Failed to load evidence ledger</p>
        <p className="text-xs text-slate-500 mt-1">{(error as Error)?.message}</p>
      </div>
    );
  }

  const getIcon = (type: string) => {
    const t = type.toUpperCase();
    if (t.includes('SATELLITE') || t.includes('EO')) return <Database className="w-4 h-4" />;
    if (t.includes('PHOTO') || t.includes('IMAGE')) return <Camera className="w-4 h-4" />;
    if (t.includes('RAIN') || t.includes('WEATHER')) return <CloudRain className="w-4 h-4" />;
    if (t.includes('TERRAIN') || t.includes('ELEVATION')) return <Layers className="w-4 h-4" />;
    if (t.includes('DRAIN') || t.includes('FLOW')) return <Activity className="w-4 h-4" />;
    return <FileText className="w-4 h-4" />;
  };

  const getTruthBadge = (truth: string) => {
    switch (truth) {
      case "EVIDENCE":
        return "bg-emerald-900/40 text-emerald-300 border-emerald-800";
      case "MODEL_ESTIMATION":
        return "bg-blue-900/40 text-blue-300 border-blue-800";
      case "SYNTHETIC_DATA":
        return "bg-purple-900/40 text-purple-300 border-purple-800";
      default:
        return "bg-slate-800 text-slate-300 border-slate-700";
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 shadow-sm">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-slate-100 flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-emerald-400" />
              Evidence Ledger & Provenance
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Multi-source intelligence verifying failure mechanisms with data truth declarations.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono font-bold px-2.5 py-1 rounded bg-slate-800 text-slate-300 border border-slate-700">
              {evidence?.length || 0} Records
            </span>
            <div className="flex items-center gap-1 text-xs font-semibold text-emerald-400 bg-emerald-950/50 px-2.5 py-1 rounded border border-emerald-800/50">
              <ShieldCheck className="w-3.5 h-3.5" />
              Audit Trail Active
            </div>
          </div>
        </div>
      </div>

      {/* Evidence items */}
      <div className="space-y-4">
        {evidence?.map((item) => (
          <div 
            key={item.evidence_id} 
            className="border border-slate-800 rounded-xl p-5 bg-slate-900/60 hover:bg-slate-900/90 transition-all shadow-sm"
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex items-start gap-3">
                <div className="bg-blue-950/60 text-blue-400 p-2.5 rounded-lg border border-blue-800/40 shrink-0 mt-0.5">
                  {getIcon(item.type)}
                </div>
                <div>
                  <div className="flex flex-wrap items-center gap-2 mb-1.5">
                    <span className="text-xs font-bold text-slate-300 uppercase tracking-wider">{item.type}</span>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded border uppercase tracking-wider ${getTruthBadge(item.data_truth)}`}>
                      {item.data_truth}
                    </span>
                    {item.source && (
                      <span className="text-[11px] text-slate-400 font-mono">
                        Source: {item.source}
                      </span>
                    )}
                  </div>
                  <h4 className="font-semibold text-slate-100 text-sm">{item.title}</h4>
                  {item.description && (
                    <p className="text-xs text-slate-300 mt-1.5 leading-relaxed">{item.description}</p>
                  )}
                </div>
              </div>

              <div className="text-right shrink-0">
                <div className="text-base font-bold text-slate-100 font-mono">{(item.confidence * 100).toFixed(0)}%</div>
                <div className="text-[10px] text-slate-400 uppercase tracking-wider">Confidence</div>
              </div>
            </div>

            {/* Extracted Metrics / Values if available */}
            {item.value && typeof item.value === 'object' && Object.keys(item.value).length > 0 && (
              <div className="mt-4 pt-3 border-t border-slate-800/80 grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs font-mono">
                {Object.entries(item.value).map(([k, v]) => {
                  if (typeof v === 'object' && v !== null) return null;
                  return (
                    <div key={k} className="bg-slate-950/60 px-3 py-2 rounded border border-slate-800">
                      <span className="text-[10px] text-slate-500 uppercase block tracking-wider mb-0.5 truncate">
                        {k.replace(/_/g, ' ')}
                      </span>
                      <span className="text-slate-200 font-semibold truncate block">
                        {String(v)}
                      </span>
                    </div>
                  );
                })}
              </div>
            )}

            {/* Assumptions & Limitations */}
            {((item.limitations && item.limitations.length > 0) || (item.assumptions && item.assumptions.length > 0)) && (
              <div className="mt-4 pt-3 border-t border-slate-800/80 grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                {item.assumptions && item.assumptions.length > 0 && (
                  <div className="bg-slate-950/40 p-3 rounded-lg border border-slate-800/60">
                    <div className="flex items-center gap-1.5 text-xs font-semibold text-blue-400 mb-1.5">
                      <Info className="w-3.5 h-3.5" />
                      Assumptions
                    </div>
                    <ul className="text-slate-400 list-disc pl-4 space-y-1 text-[11px]">
                      {item.assumptions.map((asm, i) => (
                        <li key={i}>{typeof asm === 'string' ? asm : JSON.stringify(asm)}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {item.limitations && item.limitations.length > 0 && (
                  <div className="bg-slate-950/40 p-3 rounded-lg border border-slate-800/60">
                    <div className="flex items-center gap-1.5 text-xs font-semibold text-amber-400 mb-1.5">
                      <AlertTriangle className="w-3.5 h-3.5" />
                      Limitations
                    </div>
                    <ul className="text-slate-400 list-disc pl-4 space-y-1 text-[11px]">
                      {item.limitations.map((lim, i) => (
                        <li key={i}>{typeof lim === 'string' ? lim : JSON.stringify(lim)}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}

        {(!evidence || evidence.length === 0) && (
          <div className="text-center p-12 text-slate-500 border border-dashed border-slate-800 rounded-xl bg-slate-900/30">
            <Info className="mx-auto h-8 w-8 text-slate-600 mb-2" />
            <p className="text-sm font-medium text-slate-400">No evidence records found for this case.</p>
            <p className="text-xs text-slate-500 mt-1">Verify cluster intelligence or run analysis to generate evidence.</p>
          </div>
        )}
      </div>
    </div>
  );
}
