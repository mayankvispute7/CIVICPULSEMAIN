"use client";

import { useQuery } from "@tanstack/react-query";
import { executionApi } from "@/services/api";
import { Loader2, Briefcase, Clock, CheckCircle2, AlertTriangle, Calendar, MapPin, ChevronRight, Play } from "lucide-react";
import { format } from "date-fns";
import Link from "next/link";
import { motion } from "framer-motion";

export default function ExecutionPage() {
  const { data: workOrders, isLoading } = useQuery({
    queryKey: ['work-orders'],
    queryFn: () => executionApi.getWorkOrders()
  });

  return (
    <div className="flex-1 bg-slate-950 p-8 min-h-screen">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Header */}
        <div>
          <h1 className="text-3xl font-black text-slate-100 tracking-tight flex items-center gap-3">
            <Briefcase className="w-8 h-8 text-blue-500" />
            Execution Center
          </h1>
          <p className="text-slate-400 mt-2 text-lg">Monitor active work orders, field tasks, and operational readiness.</p>
        </div>

        {/* Dashboard Content */}
        {isLoading ? (
          <div className="flex justify-center items-center py-24">
             <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
          </div>
        ) : !workOrders || workOrders.length === 0 ? (
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-12 text-center shadow-xl">
             <AlertTriangle className="w-12 h-12 text-slate-600 mx-auto mb-4" />
             <h3 className="text-xl font-bold text-slate-300 mb-2">No Active Work Orders</h3>
             <p className="text-slate-500">Go to a case and approve an intervention plan to generate a work order.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {workOrders.map((wo, idx) => (
              <motion.div 
                key={wo.work_order_id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.1 }}
                className="bg-slate-900/80 backdrop-blur-sm border border-slate-800 hover:border-blue-500/50 rounded-2xl p-6 shadow-xl transition-all group flex flex-col"
              >
                <div className="flex justify-between items-start mb-4">
                  <div className="px-3 py-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-full text-[10px] font-bold uppercase tracking-wider flex items-center gap-1.5">
                    <Play className="w-3 h-3 fill-emerald-400" /> {wo.status}
                  </div>
                  <div className="text-[10px] font-mono text-slate-500 border border-slate-700 bg-slate-800 px-2 py-0.5 rounded">
                    {wo.work_order_id.split('-')[0]}
                  </div>
                </div>

                <div className="mb-6 flex-1">
                  <h3 className="text-lg font-bold text-slate-200 leading-tight mb-2 group-hover:text-blue-400 transition-colors">{wo.title}</h3>
                  <div className="text-sm text-slate-500 line-clamp-2">{wo.description}</div>
                </div>

                <div className="space-y-3 mb-6 bg-slate-950/50 p-4 rounded-xl border border-slate-800/50">
                  <div className="flex items-center gap-3 text-sm text-slate-400">
                    <Calendar className="w-4 h-4 text-slate-500" />
                    <span>Start: <strong className="text-slate-300">{wo.planned_start ? format(new Date(wo.planned_start), 'MMM d, yyyy') : 'TBD'}</strong></span>
                  </div>
                  <div className="flex items-center gap-3 text-sm text-slate-400">
                    <Clock className="w-4 h-4 text-slate-500" />
                    <span>End: <strong className="text-slate-300">{wo.planned_end ? format(new Date(wo.planned_end), 'MMM d, yyyy') : 'TBD'}</strong></span>
                  </div>
                  <div className="flex items-center gap-3 text-sm text-slate-400">
                    <MapPin className="w-4 h-4 text-slate-500" />
                    <span className="truncate">Case <strong className="text-blue-400 font-mono text-xs">{wo.case_id.split('-')[0]}</strong></span>
                  </div>
                </div>

                <Link 
                  href={`/cases/${wo.case_id}`}
                  className="w-full py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-sm font-bold flex items-center justify-center gap-2 transition-colors shadow-lg shadow-blue-900/20"
                >
                  Manage Execution <ChevronRight className="w-4 h-4" />
                </Link>
              </motion.div>
            ))}
          </div>
        )}

      </div>
    </div>
  );
}
