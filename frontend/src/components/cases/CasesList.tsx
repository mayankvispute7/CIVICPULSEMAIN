"use client";

import { useQuery } from "@tanstack/react-query";
import { casesApi } from "@/services/api";
import Link from "next/link";
import { AlertCircle, Activity, ChevronRight, CheckCircle2, Clock } from "lucide-react";
import { format } from "date-fns";

export default function CasesList() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['cases'],
    queryFn: () => casesApi.getCases(),
  });

  if (isLoading) {
    return (
      <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm p-6 text-center text-gray-500 py-12 animate-pulse">
        Loading cases...
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 p-6 rounded-xl">
        Error loading cases: {(error as Error).message}
      </div>
    );
  }

  if (!data?.cases || data.cases.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm p-12 text-center">
        <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 dark:text-white">No Failure Cases Found</h3>
        <p className="text-gray-500 mt-2">Cases are generated from high-confidence complaint clusters.</p>
        <Link href="/situation" className="inline-block mt-4 text-blue-600 hover:underline">
          Go to Situation Center
        </Link>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-gray-50 dark:bg-gray-800/50 border-b border-gray-200 dark:border-gray-800 text-xs uppercase tracking-wider text-gray-500 dark:text-gray-400">
              <th className="p-4 font-semibold">Case Title</th>
              <th className="p-4 font-semibold">Type</th>
              <th className="p-4 font-semibold">Status</th>
              <th className="p-4 font-semibold">Confidence</th>
              <th className="p-4 font-semibold text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 dark:divide-gray-800">
            {data.cases.map((fc) => (
              <tr key={fc.case_id} className="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                <td className="p-4">
                  <div className="font-semibold text-gray-900 dark:text-white">{fc.title}</div>
                  <div className="text-xs text-gray-500 mt-1">{fc.case_id}</div>
                </td>
                <td className="p-4">
                  <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400 border border-blue-200 dark:border-blue-800">
                    <Activity className="w-3.5 h-3.5" />
                    {fc.failure_type.replace(/_/g, ' ')}
                  </span>
                </td>
                <td className="p-4">
                  <div className="flex items-center gap-2 text-sm">
                    {fc.status === 'INVESTIGATING' ? (
                      <Clock className="w-4 h-4 text-amber-500" />
                    ) : (
                      <CheckCircle2 className="w-4 h-4 text-green-500" />
                    )}
                    <span className="text-gray-700 dark:text-gray-300 capitalize">{fc.status.toLowerCase()}</span>
                  </div>
                </td>
                <td className="p-4">
                  <div className="flex items-center gap-2">
                    <div className="w-16 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                      <div 
                        className={`h-full rounded-full ${fc.confidence > 0.8 ? 'bg-red-500' : 'bg-amber-500'}`}
                        style={{ width: `${fc.confidence * 100}%` }}
                      />
                    </div>
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      {(fc.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                </td>
                <td className="p-4 text-right">
                  <Link 
                    href={`/cases/${fc.case_id}`}
                    className="inline-flex items-center gap-1 text-sm font-semibold text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
                  >
                    View Case <ChevronRight className="w-4 h-4" />
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
