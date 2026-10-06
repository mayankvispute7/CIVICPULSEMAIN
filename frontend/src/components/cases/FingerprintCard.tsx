import { FailureCaseResponse, HypothesisResponse } from "@/types/api";
import { AlertTriangle, BarChart3, Activity, Lightbulb, CheckCircle2 } from "lucide-react";
import { motion } from "framer-motion";

const NestedValue = ({ val }: { val: any }) => {
  if (typeof val !== 'object' || val === null) {
    return <span className="font-mono text-slate-200">{String(val)}</span>;
  }
  
  return (
    <div className="flex flex-wrap gap-2 mt-2">
      {Object.entries(val).map(([k, v]) => {
        if (k === 'data_truth' || k === 'data truth') return null; // hide metadata noise if possible, or render it differently
        return (
          <div key={k} className="bg-slate-800/80 px-2 py-1 rounded text-[10px] border border-slate-700/50 flex gap-1 items-center">
            <span className="text-slate-400 uppercase tracking-wider">{k.replace(/_/g, ' ')}:</span>
            <span className="text-emerald-400 font-mono font-bold">{String(v)}</span>
          </div>
        );
      })}
    </div>
  );
};

export function FingerprintCard({ caseData, hypotheses = [] }: { caseData: FailureCaseResponse, hypotheses?: HypothesisResponse[] }) {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.1 } }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 10 },
    visible: { opacity: 1, y: 0 }
  };
  
  // Filter out redundant or overly verbose keys from the fingerprint
  const excludedKeys = ['summary', 'case id', 'case_id', 'impact_summary'];

  return (
    <div className="p-6">
      <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-6 border-b border-slate-800 pb-2 flex items-center gap-2">
        <Activity className="w-4 h-4 text-blue-400" />
        Failure Fingerprint
      </h3>
      
      <motion.div className="space-y-6" variants={containerVariants} initial="hidden" animate="visible">
        <motion.div variants={itemVariants}>
          <div className="flex items-center gap-2 mb-2 text-slate-300">
            <BarChart3 className="w-4 h-4 text-blue-400" />
            <span className="text-sm font-semibold tracking-wide">Magnitude</span>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-slate-800/30 p-4 rounded-xl border border-slate-700/50 hover:bg-slate-800/50 transition-colors">
              <div className="text-3xl font-light text-slate-100">{caseData.recurrence_count || '0'}</div>
              <div className="text-[10px] uppercase tracking-wider text-slate-500 mt-1">Historical Incidents</div>
            </div>
            <div className="bg-emerald-950/20 p-4 rounded-xl border border-emerald-900/30 hover:bg-emerald-950/40 transition-colors">
              <div className="text-3xl font-light text-emerald-400">{(caseData.confidence * 100).toFixed(0)}%</div>
              <div className="text-[10px] uppercase tracking-wider text-emerald-600 mt-1">Confidence Score</div>
            </div>
          </div>
        </motion.div>

        <motion.div variants={itemVariants}>
          <div className="flex items-center gap-2 mb-3 text-slate-300">
            <AlertTriangle className="w-4 h-4 text-orange-400" />
            <span className="text-sm font-semibold tracking-wide">Probable Characteristics</span>
          </div>
          <div className="grid grid-cols-1 gap-2">
            {caseData.fingerprint ? (
              Object.entries(caseData.fingerprint)
                .filter(([k]) => !excludedKeys.includes(k.toLowerCase()))
                .map(([key, val], idx) => (
                <motion.div 
                  key={key} 
                  variants={itemVariants}
                  className="p-3 bg-slate-800/20 rounded-lg border border-slate-800/60 hover:border-slate-700 transition-colors"
                >
                  <div className="flex flex-col">
                    <span className="text-slate-500 uppercase text-[10px] tracking-wider mb-1 font-semibold">{key.replace(/_/g, ' ')}</span>
                    <NestedValue val={val} />
                  </div>
                </motion.div>
              ))
            ) : (
              <div className="text-xs text-slate-500 italic p-2">No structured fingerprint available</div>
            )}
          </div>
        </motion.div>

        {hypotheses && hypotheses.length > 0 && (
          <motion.div variants={itemVariants}>
            <div className="flex items-center gap-2 mb-3 text-slate-300 border-t border-slate-800 pt-6">
              <Lightbulb className="w-4 h-4 text-yellow-400" />
              <span className="text-sm font-semibold tracking-wide">Leading Hypothesis</span>
            </div>
            <div className="bg-yellow-500/10 p-5 rounded-xl border border-yellow-500/20">
              <p className="text-sm text-yellow-200/90 leading-relaxed">
                {hypotheses[0].description || hypotheses[0].title}
              </p>
              <div className="mt-4 pt-3 border-t border-yellow-500/20 flex justify-between items-center text-xs">
                 <span className="text-yellow-600/80 uppercase tracking-wider font-bold">Confidence</span>
                 <span className="bg-yellow-500/20 text-yellow-400 px-2 py-1 rounded-md font-mono font-bold">{(hypotheses[0].confidence * 100).toFixed(0)}%</span>
              </div>
            </div>
          </motion.div>
        )}
      </motion.div>
    </div>
  );
}
