import { useQuery } from "@tanstack/react-query";
import { casesApi } from "@/services/api";
import { Loader2, ShieldCheck, Database, Camera, CloudRain, AlertTriangle } from "lucide-react";

export function EvidenceLedger({ caseId }: { caseId: string }) {
  const { data: evidence, isLoading } = useQuery({
    queryKey: ['case-evidence', caseId],
    queryFn: () => casesApi.getEvidence(caseId),
  });

  if (isLoading) return <div className="p-8 text-center"><Loader2 className="mx-auto animate-spin" /></div>;

  const getIcon = (type: string) => {
    if (type.includes('SATELLITE') || type.includes('EO')) return <Database className="w-4 h-4" />;
    if (type.includes('PHOTO')) return <Camera className="w-4 h-4" />;
    if (type.includes('RAIN')) return <CloudRain className="w-4 h-4" />;
    return <FileText className="w-4 h-4" />;
  };

  return (
    <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-6 shadow-sm min-h-full">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-bold text-gray-900 dark:text-white">Evidence Ledger</h2>
        <div className="flex items-center gap-1 text-xs font-semibold text-green-600 bg-green-50 dark:bg-green-900/30 px-2 py-1 rounded">
          <ShieldCheck className="w-3 h-3" />
          Audit Trail Active
        </div>
      </div>

      <div className="space-y-4">
        {evidence?.map((item) => (
          <div key={item.evidence_id} className="border border-gray-100 dark:border-gray-800 rounded-lg p-4 bg-gray-50 dark:bg-gray-800/50 hover:bg-white dark:hover:bg-gray-800 transition-colors">
            <div className="flex items-start justify-between">
              <div className="flex gap-3">
                <div className="bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 p-2 rounded-lg h-8 w-8 flex items-center justify-center shrink-0">
                  {getIcon(item.type)}
                </div>
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-bold text-gray-500 uppercase">{item.type}</span>
                    <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300 uppercase tracking-wider">
                      {item.data_truth}
                    </span>
                  </div>
                  <h4 className="font-semibold text-gray-900 dark:text-white text-sm">{item.title}</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{item.description}</p>
                </div>
              </div>
              <div className="text-right shrink-0">
                <div className="text-sm font-bold text-gray-900 dark:text-white">{(item.confidence * 100).toFixed(0)}%</div>
                <div className="text-[10px] text-gray-500 uppercase">Confidence</div>
              </div>
            </div>

            {item.limitations && item.limitations.length > 0 && (
              <div className="mt-4 pt-3 border-t border-gray-200 dark:border-gray-700">
                <div className="flex items-center gap-1 text-xs font-semibold text-orange-600 dark:text-orange-400 mb-1">
                  <AlertTriangle className="w-3 h-3" />
                  Limitations
                </div>
                <ul className="text-xs text-gray-600 dark:text-gray-400 list-disc pl-4">
                  {item.limitations.map((lim, i) => (
                    <li key={i}>{lim}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
        {(!evidence || evidence.length === 0) && (
          <div className="text-center p-8 text-gray-500 border border-dashed rounded-lg">
            No evidence records found for this case.
          </div>
        )}
      </div>
    </div>
  );
}

// Ensure FileText icon works if not imported above
import { FileText } from "lucide-react";
