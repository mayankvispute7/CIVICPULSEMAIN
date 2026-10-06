import { motion } from "framer-motion";
import { Users, Map, AlertTriangle, AlertOctagon } from "lucide-react";

export function BeautifulImpactSummary({ summary }: { summary: string }) {
  if (!summary) return <div className="text-slate-500 italic">No summary available.</div>;

  // Regex parsing based on the Python f-string format
  const complaintsMatch = summary.match(/(\d+)\s+complaints/i);
  const areaMatch = summary.match(/over\s+([\d.]+)\s*m/i);
  
  const categoriesStr = summary.match(/Categories:\s+(.*?)\./i)?.[1];
  const categories = categoriesStr ? categoriesStr.split(',').map(s => s.trim()) : [];
  
  const severityStr = summary.match(/Severity distribution:\s+(\{.*?\})/i)?.[1];
  let severities: Record<string, number> | null = null;
  
  try {
    if (severityStr) {
      // Replace python single quotes with double quotes to make it valid JSON
      const jsonStr = severityStr.replace(/'/g, '"');
      severities = JSON.parse(jsonStr);
    }
  } catch (e) {
    console.warn("Failed to parse severity distribution:", e);
  }

  // If regex fails to match standard format, fallback to standard text
  if (!complaintsMatch || !areaMatch) {
    return <p className="text-slate-300 leading-relaxed text-lg">{summary}</p>;
  }

  const complaintCount = parseInt(complaintsMatch[1], 10);
  const areaValue = parseFloat(areaMatch[1]);

  return (
    <div className="space-y-6">
      {/* Top Stats */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-slate-800/40 p-4 rounded-xl border border-slate-700/50 flex items-center gap-4">
          <div className="p-3 bg-red-500/10 rounded-lg shrink-0">
            <Users className="w-6 h-6 text-red-400" />
          </div>
          <div>
            <div className="text-2xl font-black text-slate-100">{complaintCount}</div>
            <div className="text-xs uppercase tracking-wider text-slate-400 font-semibold">Total Complaints</div>
          </div>
        </div>

        <div className="bg-slate-800/40 p-4 rounded-xl border border-slate-700/50 flex items-center gap-4">
          <div className="p-3 bg-blue-500/10 rounded-lg shrink-0">
            <Map className="w-6 h-6 text-blue-400" />
          </div>
          <div>
            <div className="text-2xl font-black text-slate-100">{areaValue.toLocaleString()}m</div>
            <div className="text-xs uppercase tracking-wider text-slate-400 font-semibold">Affected Area</div>
          </div>
        </div>
      </div>

      {/* Severity Distribution */}
      {severities && (
        <div>
          <h3 className="text-xs uppercase tracking-wider text-slate-500 mb-3 font-semibold">Severity Breakdown</h3>
          <div className="grid grid-cols-4 gap-2">
            {[
              { label: 'Critical', key: 'CRITICAL', color: 'text-red-400', bg: 'bg-red-500/10', border: 'border-red-500/20' },
              { label: 'High', key: 'HIGH', color: 'text-orange-400', bg: 'bg-orange-500/10', border: 'border-orange-500/20' },
              { label: 'Medium', key: 'MEDIUM', color: 'text-yellow-400', bg: 'bg-yellow-500/10', border: 'border-yellow-500/20' },
              { label: 'Low', key: 'LOW', color: 'text-emerald-400', bg: 'bg-emerald-500/10', border: 'border-emerald-500/20' }
            ].map((level) => {
              const count = severities?.[level.key] || 0;
              return (
                <div key={level.key} className={`${level.bg} ${level.border} border p-3 rounded-lg text-center flex flex-col justify-center`}>
                  <div className={`text-xl font-bold ${level.color}`}>{count}</div>
                  <div className={`text-[9px] uppercase tracking-wider font-bold ${level.color} opacity-80 mt-1`}>{level.label}</div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Categories */}
      {categories.length > 0 && (
        <div>
          <h3 className="text-xs uppercase tracking-wider text-slate-500 mb-3 font-semibold flex items-center gap-2">
            <AlertTriangle className="w-3 h-3" /> Reported Issues
          </h3>
          <div className="flex flex-wrap gap-2 max-h-[120px] overflow-y-auto custom-scrollbar pr-2">
            {categories.map((cat, idx) => (
              <span key={idx} className="px-2.5 py-1.5 bg-slate-800/80 border border-slate-700/80 rounded-md text-xs text-slate-300 font-medium">
                {cat.replace(/_/g, ' ')}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
