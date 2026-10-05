import { useQuery } from "@tanstack/react-query";
import { casesApi } from "@/services/api";
import { Loader2, CheckCircle2, SlidersHorizontal, ArrowRight, Zap, Target, Clock, Coins } from "lucide-react";
import { formatCurrency } from "@/lib/utils";

export function InterventionLab({ caseId }: { caseId: string }) {
  const { data, isLoading } = useQuery({
    queryKey: ['case-interventions', caseId],
    queryFn: () => casesApi.getInterventions(caseId),
  });

  if (isLoading) return <div className="p-8 text-center"><Loader2 className="mx-auto animate-spin" /></div>;

  const interventions = data?.interventions || [];

  return (
    <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl shadow-sm min-h-full flex flex-col">
      <div className="p-6 border-b border-gray-200 dark:border-gray-800 flex justify-between items-center">
        <div>
          <h2 className="text-lg font-bold text-gray-900 dark:text-white">Intervention Options</h2>
          <p className="text-sm text-gray-500 mt-1">Evaluated approaches to resolve this infrastructure failure.</p>
        </div>
        <button className="flex items-center gap-2 px-3 py-1.5 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-md text-sm font-medium transition-colors border border-gray-200 dark:border-gray-700">
          <SlidersHorizontal className="w-4 h-4" />
          Constraints
        </button>
      </div>

      <div className="p-6 flex-1 overflow-y-auto bg-gray-50 dark:bg-gray-950/50">
        <div className="grid gap-6">
          {interventions.sort((a, b) => b.overall_score - a.overall_score).map((option, idx) => (
            <div 
              key={option.intervention_id} 
              className={`relative bg-white dark:bg-gray-900 border rounded-xl p-6 transition-all ${
                idx === 0 
                  ? 'border-blue-500 shadow-md ring-1 ring-blue-500' 
                  : 'border-gray-200 dark:border-gray-800 shadow-sm hover:border-gray-300 dark:hover:border-gray-700'
              }`}
            >
              {idx === 0 && (
                <div className="absolute -top-3 left-6 bg-blue-500 text-white text-[10px] font-bold uppercase tracking-wider px-3 py-1 rounded-full flex items-center gap-1 shadow-sm">
                  <CheckCircle2 className="w-3 h-3" />
                  Recommended
                </div>
              )}
              
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-bold text-gray-900 dark:text-white">{option.title}</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{option.description}</p>
                </div>
                <div className="text-right shrink-0 ml-4">
                  <div className="text-2xl font-black text-gray-900 dark:text-white">{(option.overall_score * 100).toFixed(0)}</div>
                  <div className="text-[10px] uppercase font-bold text-gray-500">Score</div>
                </div>
              </div>

              <div className="grid grid-cols-4 gap-4 mt-6">
                <div className="bg-gray-50 dark:bg-gray-800/50 p-3 rounded-lg border border-gray-100 dark:border-gray-800">
                  <div className="flex items-center gap-1.5 text-xs font-semibold text-gray-500 uppercase mb-1">
                    <Coins className="w-3.5 h-3.5" />
                    Est. Cost
                  </div>
                  <div className="text-sm font-bold text-gray-900 dark:text-white">{formatCurrency(option.estimated_cost)}</div>
                </div>
                <div className="bg-gray-50 dark:bg-gray-800/50 p-3 rounded-lg border border-gray-100 dark:border-gray-800">
                  <div className="flex items-center gap-1.5 text-xs font-semibold text-gray-500 uppercase mb-1">
                    <Clock className="w-3.5 h-3.5" />
                    Duration
                  </div>
                  <div className="text-sm font-bold text-gray-900 dark:text-white">{option.estimated_duration_days} days</div>
                </div>
                <div className="bg-gray-50 dark:bg-gray-800/50 p-3 rounded-lg border border-gray-100 dark:border-gray-800">
                  <div className="flex items-center gap-1.5 text-xs font-semibold text-gray-500 uppercase mb-1">
                    <Target className="w-3.5 h-3.5" />
                    Impact
                  </div>
                  <div className="text-sm font-bold text-gray-900 dark:text-white">{option.complaints_addressed} complaints</div>
                </div>
                <div className="bg-gray-50 dark:bg-gray-800/50 p-3 rounded-lg border border-gray-100 dark:border-gray-800">
                  <div className="flex items-center gap-1.5 text-xs font-semibold text-gray-500 uppercase mb-1">
                    <Zap className="w-3.5 h-3.5" />
                    Risk Red.
                  </div>
                  <div className="text-sm font-bold text-green-600 dark:text-green-400">{(option.expected_risk_reduction * 100).toFixed(0)}%</div>
                </div>
              </div>

              <div className="mt-6 flex justify-between items-center">
                <div className="text-xs text-gray-500 uppercase font-bold tracking-wider px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded">
                  {option.data_truth}
                </div>
                <div className="flex gap-2">
                  <button className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 dark:bg-gray-800 dark:text-gray-300 dark:border-gray-700 dark:hover:bg-gray-700">
                    Compare
                  </button>
                  <button className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 flex items-center gap-2">
                    Execute <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}

          {interventions.length === 0 && (
            <div className="text-center p-12 border-2 border-dashed border-gray-200 dark:border-gray-800 rounded-xl text-gray-500">
              No intervention options have been generated for this case.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
