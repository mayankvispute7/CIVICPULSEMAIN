"use client";

import { useQuery } from "@tanstack/react-query";
import { casesApi } from "@/services/api";
import { 
  Loader2, 
  History, 
  Clock, 
  AlertTriangle, 
  Repeat, 
  Wrench, 
  CheckCircle2, 
  MessageSquare,
  TrendingDown,
  Calendar
} from "lucide-react";

export function HistoryTimeline({ caseId }: { caseId: string }) {
  const { data: historyData, isLoading, error } = useQuery({
    queryKey: ['case-history', caseId],
    queryFn: () => casesApi.getHistory(caseId),
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-16">
        <div className="text-center">
          <Loader2 className="mx-auto h-8 w-8 text-blue-500 animate-spin" />
          <p className="mt-3 text-xs uppercase tracking-wider font-semibold text-slate-400">Loading historical timeline...</p>
        </div>
      </div>
    );
  }

  if (error || !historyData) {
    return (
      <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6 text-center text-slate-400">
        <AlertTriangle className="mx-auto h-8 w-8 text-amber-500 mb-2" />
        <p className="text-sm font-medium text-slate-200">Failed to load history</p>
        <p className="text-xs text-slate-500 mt-1">{(error as Error)?.message || "No history records available."}</p>
      </div>
    );
  }

  const { historical_incidents = [], previous_complaints = [], recurrence_intervals = [] } = historyData;

  // Compute average recurrence interval if available
  const avgRecurrence = recurrence_intervals.length > 0
    ? Math.round(recurrence_intervals.reduce((a, b) => a + b, 0) / recurrence_intervals.length)
    : null;

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Metrics Banner */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="bg-slate-900/70 border border-slate-800 p-4 rounded-xl">
          <div className="flex items-center gap-2 text-slate-400 text-xs font-semibold uppercase tracking-wider mb-1">
            <History className="w-3.5 h-3.5 text-blue-400" />
            Past Incidents
          </div>
          <div className="text-2xl font-bold text-slate-100">{historyData.total_past_incidents || historical_incidents.length}</div>
        </div>

        <div className="bg-slate-900/70 border border-slate-800 p-4 rounded-xl">
          <div className="flex items-center gap-2 text-slate-400 text-xs font-semibold uppercase tracking-wider mb-1">
            <Wrench className="w-3.5 h-3.5 text-emerald-400" />
            Interventions Done
          </div>
          <div className="text-2xl font-bold text-emerald-400">{historyData.total_previous_interventions || 0}</div>
        </div>

        <div className="bg-slate-900/70 border border-slate-800 p-4 rounded-xl">
          <div className="flex items-center gap-2 text-slate-400 text-xs font-semibold uppercase tracking-wider mb-1">
            <Repeat className="w-3.5 h-3.5 text-amber-400" />
            Avg Recurrence
          </div>
          <div className="text-2xl font-bold text-slate-100">
            {avgRecurrence ? `${avgRecurrence}d` : "N/A"}
          </div>
        </div>

        <div className="bg-slate-900/70 border border-slate-800 p-4 rounded-xl">
          <div className="flex items-center gap-2 text-slate-400 text-xs font-semibold uppercase tracking-wider mb-1">
            <MessageSquare className="w-3.5 h-3.5 text-purple-400" />
            Corridor Complaints
          </div>
          <div className="text-2xl font-bold text-purple-400">{previous_complaints.length}</div>
        </div>
      </div>

      {/* Historical Incidents Timeline */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 shadow-sm">
        <div className="flex items-center justify-between mb-6 border-b border-slate-800 pb-4">
          <div>
            <h2 className="text-base font-bold text-slate-100 flex items-center gap-2">
              <History className="w-5 h-5 text-blue-400" />
              Chronological Incident History
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Historical failure patterns, emergency interventions applied, and recurrence intervals.
            </p>
          </div>
          <span className="text-[10px] font-bold px-2 py-1 rounded bg-blue-900/40 text-blue-300 border border-blue-800">
            SYNTHETIC DEMO AUDIT
          </span>
        </div>

        {historical_incidents.length === 0 ? (
          <div className="p-8 text-center text-slate-500 border border-dashed border-slate-800 rounded-lg">
            No past incidents documented for this location.
          </div>
        ) : (
          <div className="relative pl-6 space-y-6 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-800">
            {historical_incidents.map((incident, idx) => {
              const dateStr = incident.occurred_at
                ? new Date(incident.occurred_at).toLocaleDateString("en-US", {
                    year: "numeric",
                    month: "short",
                    day: "numeric",
                  })
                : "Unknown Date";

              return (
                <div key={incident.incident_id || idx} className="relative group">
                  {/* Timeline dot */}
                  <div className="absolute -left-[27px] top-1.5 w-3 h-3 rounded-full bg-blue-500 border-2 border-[#0a0f1c] ring-2 ring-blue-500/20 group-hover:scale-125 transition-transform" />

                  <div className="bg-slate-800/50 hover:bg-slate-800/80 border border-slate-700/60 rounded-xl p-4 transition-colors">
                    <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-slate-100">{incident.title}</span>
                        {incident.severity && (
                          <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded uppercase tracking-wider ${
                            incident.severity === 'HIGH' || incident.severity === 'CRITICAL'
                              ? 'bg-red-900/40 text-red-300 border border-red-800'
                              : 'bg-amber-900/40 text-amber-300 border border-amber-800'
                          }`}>
                            {incident.severity}
                          </span>
                        )}
                        <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-700/60 text-slate-300 uppercase">
                          {incident.data_truth}
                        </span>
                      </div>
                      <div className="flex items-center gap-1.5 text-xs text-slate-400 font-mono">
                        <Calendar className="w-3.5 h-3.5 text-slate-500" />
                        {dateStr}
                      </div>
                    </div>

                    {incident.description && (
                      <p className="text-xs text-slate-300 mb-3">{incident.description}</p>
                    )}

                    {/* Intervention details */}
                    {(incident.intervention_taken || incident.intervention_outcome) && (
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-3 pt-3 border-t border-slate-700/50 text-xs">
                        {incident.intervention_taken && (
                          <div className="bg-slate-900/60 p-2.5 rounded-lg border border-slate-700/40">
                            <span className="text-[10px] uppercase font-bold text-slate-400 block mb-0.5">
                              Intervention Taken
                            </span>
                            <span className="text-slate-200">{incident.intervention_taken}</span>
                          </div>
                        )}

                        {incident.intervention_outcome && (
                          <div className="bg-slate-900/60 p-2.5 rounded-lg border border-slate-700/40">
                            <span className="text-[10px] uppercase font-bold text-slate-400 block mb-0.5 flex items-center justify-between">
                              <span>Observed Outcome</span>
                              {incident.recurrence_after_days && (
                                <span className="text-amber-400 font-mono text-[10px] lowercase">
                                  recurred in {incident.recurrence_after_days}d
                                </span>
                              )}
                            </span>
                            <span className="text-slate-300">{incident.intervention_outcome}</span>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Associated Citizen Complaints */}
      {previous_complaints.length > 0 && (
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-3">
            <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
              <MessageSquare className="w-4 h-4 text-purple-400" />
              Citizen Reports Triggering Current Situation ({previous_complaints.length})
            </h3>
            <span className="text-xs text-slate-400 font-mono">DBSCAN Clustered</span>
          </div>

          <div className="space-y-2">
            {previous_complaints.map((c) => (
              <div 
                key={c.complaint_id}
                className="bg-slate-800/40 border border-slate-700/50 rounded-lg p-3 hover:bg-slate-800/70 transition-colors"
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h4 className="text-xs font-semibold text-slate-200">{c.title}</h4>
                    <p className="text-xs text-slate-400 mt-1">{c.description}</p>
                    {c.address && (
                      <p className="text-[11px] text-slate-500 mt-1 font-mono">📍 {c.address}</p>
                    )}
                  </div>
                  <div className="shrink-0 text-right">
                    <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded uppercase tracking-wider ${
                      c.severity === 'HIGH' || c.severity === 'CRITICAL'
                        ? 'bg-red-900/40 text-red-300 border border-red-800'
                        : 'bg-slate-700 text-slate-300'
                    }`}>
                      {c.severity}
                    </span>
                    <div className="text-[10px] text-slate-500 font-mono mt-1">
                      {c.reported_at ? new Date(c.reported_at).toLocaleDateString() : ""}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
