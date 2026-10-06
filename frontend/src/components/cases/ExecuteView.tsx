import { useState } from "react";
import { ResolutionPlanResponse, TaskResponse, WorkOrderResponse } from "@/types/api";
import { Loader2, CheckCircle2, Clock, AlertTriangle, Briefcase, ChevronRight, Activity, Zap, Play, Check } from "lucide-react";
import { format, differenceInHours, addHours } from "date-fns";
import { motion } from "framer-motion";

export function ExecuteView({ 
  roadmap, 
  tasks = [], 
  workOrder 
}: { 
  roadmap?: ResolutionPlanResponse, 
  tasks?: TaskResponse[], 
  workOrder?: WorkOrderResponse 
}) {
  const wo = workOrder;

  // Calculate timeline bounds
  let minTime: Date | null = null;
  let maxTime: Date | null = null;

  if (wo?.planned_start && wo?.planned_end) {
    minTime = new Date(wo.planned_start);
    maxTime = new Date(wo.planned_end);
  }

  // Fallback to tasks
  if (tasks.length > 0) {
    tasks.forEach(task => {
      if (task.planned_start) {
        const d = new Date(task.planned_start);
        if (!minTime || d < minTime) minTime = d;
      }
      if (task.planned_end) {
        const d = new Date(task.planned_end);
        if (!maxTime || d > maxTime) maxTime = d;
      }
    });
  }

  const totalHours = minTime && maxTime ? differenceInHours(maxTime, minTime) : 0;

  const [chatMessages, setChatMessages] = useState<{role: 'user'|'system', text: string}[]>([
    { role: 'system', text: 'Execution initialized. I am monitoring field updates. Let me know if any delays occur (e.g., rain, worker absence) so I can dynamically replan.' }
  ]);
  const [chatInput, setChatInput] = useState('');
  const [activeTaskPrompt, setActiveTaskPrompt] = useState<string | null>(null);
  const [completedTasks, setCompletedTasks] = useState<Set<string>>(new Set());
  
  const handleChat = (e: React.FormEvent) => {
    e.preventDefault();
    if(!chatInput.trim()) return;
    setChatMessages(prev => [...prev, {role: 'user', text: chatInput}]);
    const currentInput = chatInput.toLowerCase();
    setChatInput('');
    
    setTimeout(() => {
      if (currentInput.includes('rain') || currentInput.includes('weather')) {
        setChatMessages(prev => [...prev, {role: 'system', text: 'Weather delay detected. Adjusting downstream tasks by +2 days. Reallocating concrete curing phase. Gantt chart updated.'}]);
      } else if (currentInput.includes('worker') || currentInput.includes('absent')) {
        setChatMessages(prev => [...prev, {role: 'system', text: 'Worker shortage noted. Increasing duration for "Excavation" by 12 hours. Cost impact: +₹4,500 for overtime. Re-simulating critical path... done.'}]);
      } else {
        setChatMessages(prev => [...prev, {role: 'system', text: 'Noted. I will keep monitoring the timeline.'}]);
      }
    }, 1000);
  };

  const handleTaskCheck = (taskId: string) => {
    setActiveTaskPrompt(taskId);
  };

  const handleTaskTimeSubmit = (taskId: string, onTime: boolean) => {
    setActiveTaskPrompt(null);
    setCompletedTasks(prev => {
      const next = new Set(prev);
      next.add(taskId);
      return next;
    });
    if (!onTime) {
      setChatMessages(prev => [...prev, {role: 'system', text: `Task delayed. Recalculating schedule dependencies... Please provide reason if possible.`}]);
    } else {
      setChatMessages(prev => [...prev, {role: 'system', text: `Task completed on schedule. Great progress.`}]);
    }
  };

  return (
    <div className="flex flex-col gap-6 h-full w-full">
      
      {/* Top Banner */}
      <div className="bg-slate-900/80 backdrop-blur-md border border-slate-800 rounded-xl p-6 shadow-xl flex items-center justify-between shrink-0">
        <div className="flex items-center gap-4">
           <div className="p-3 bg-blue-500/10 rounded-lg">
             <Briefcase className="w-6 h-6 text-blue-400" />
           </div>
           <div>
             <h2 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-1">Active Work Order</h2>
             <h3 className="text-xl font-black text-slate-100">{wo?.title || roadmap?.title || "No Active Plan"}</h3>
             {wo && (
               <div className="flex items-center gap-2 mt-1 text-sm text-slate-500">
                 <span className="font-mono text-slate-400 text-xs">{wo.work_order_id.split('-')[0]}</span>
                 <span>&bull;</span>
                 <span>Budget: <span className="text-slate-300 font-semibold">₹{roadmap?.total_estimated_cost?.toLocaleString() || '0'}</span></span>
               </div>
             )}
           </div>
        </div>

        {wo && (
           <div className="flex items-center gap-6">
              <div className="text-right">
                <div className="text-xs text-slate-400 uppercase tracking-wider font-bold mb-1">Status</div>
                <div className="px-3 py-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 rounded-full text-xs font-bold tracking-wider inline-flex items-center gap-1.5">
                  <Play className="w-3 h-3 fill-emerald-400" /> {wo.status}
                </div>
              </div>
              <div className="h-10 w-px bg-slate-800" />
              <div className="text-right">
                <div className="text-xs text-slate-400 uppercase tracking-wider font-bold mb-1">Duration</div>
                <div className="text-lg font-black text-slate-200">{roadmap?.total_duration_days || '-'} Days</div>
              </div>
           </div>
        )}
      </div>
      
      <div className="flex-1 flex gap-6 overflow-hidden">
        {/* Left: Gantt Chart Area */}
        <div className="flex-[2] bg-slate-900/80 backdrop-blur-md border border-slate-800 rounded-xl overflow-hidden flex flex-col shadow-xl">
          <div className="p-4 border-b border-slate-800 bg-slate-950 flex justify-between items-center">
             <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
               <Activity className="w-4 h-4 text-blue-400" /> 
               Execution Gantt Chart
             </h3>
             <div className="flex gap-4 text-xs font-semibold text-slate-400">
               <div className="flex items-center gap-1.5"><div className="w-2 h-2 rounded-full bg-emerald-500"></div> Completed</div>
               <div className="flex items-center gap-1.5"><div className="w-2 h-2 rounded-full bg-blue-500"></div> Pending</div>
               <div className="flex items-center gap-1.5"><div className="w-2 h-2 rounded-full bg-red-500"></div> Delayed</div>
             </div>
          </div>

          <div className="flex-1 overflow-y-auto p-6 relative">
            {!wo || tasks.length === 0 ? (
               <div className="h-full flex items-center justify-center text-slate-500 flex-col gap-3">
                 <AlertTriangle className="w-10 h-10 text-slate-600" />
                 <p>No task data available for visualization.</p>
               </div>
            ) : (
               <div className="relative min-w-[700px] h-full">
                 {/* Timeline Header */}
                 <div className="flex border-b border-slate-800 pb-2 mb-4 relative ml-48">
                    {[0, 0.25, 0.5, 0.75, 1].map((pct, i) => {
                       const date = minTime ? addHours(minTime, totalHours * pct) : new Date();
                       return (
                         <div key={i} className="absolute text-xs text-slate-500 font-mono -translate-x-1/2 whitespace-nowrap" style={{ left: `${pct * 100}%` }}>
                           {format(date, 'MMM d, ha')}
                         </div>
                       );
                    })}
                 </div>

                 {/* Grid Lines */}
                 <div className="absolute inset-0 ml-48 mt-8 pointer-events-none">
                    {[0, 0.25, 0.5, 0.75, 1].map((pct, i) => (
                      <div key={i} className="absolute top-0 bottom-0 border-l border-slate-800/50 border-dashed" style={{ left: `${pct * 100}%` }} />
                    ))}
                 </div>

                 {/* Tasks list */}
                 <div className="space-y-4 mt-8 relative z-10">
                   {tasks.map((task, idx) => {
                     let leftPct = 0;
                     let widthPct = 0;

                     if (minTime && totalHours > 0 && task.planned_start && task.planned_end) {
                       const taskStart = new Date(task.planned_start);
                       const taskEnd = new Date(task.planned_end);
                       leftPct = (differenceInHours(taskStart, minTime) / totalHours) * 100;
                       widthPct = (differenceInHours(taskEnd, taskStart) / totalHours) * 100;
                     } else {
                       leftPct = (idx / tasks.length) * 100 * 0.8;
                       widthPct = 100 / tasks.length * 0.8;
                     }
                     
                     if (widthPct < 5) widthPct = 5;
                     if (leftPct + widthPct > 100) widthPct = 100 - leftPct;

                     const isCompleted = task.status === 'COMPLETED';

                     return (
                       <div key={task.task_id} className="flex items-center group">
                         {/* Left Panel: Task Info */}
                         <div className="w-48 pr-4 shrink-0 border-r border-slate-800 relative bg-slate-900/50 backdrop-blur-sm z-20 py-1">
                            <div className="text-xs font-bold text-slate-200 line-clamp-1 group-hover:text-blue-400 transition-colors">
                              {task.sequence}. {task.title}
                            </div>
                            <div className="text-[10px] text-slate-500 uppercase tracking-wider flex justify-between mt-0.5">
                              <span>{task.planned_duration_hours}H</span>
                              <span className={isCompleted ? 'text-emerald-500' : 'text-blue-500/70'}>{task.status}</span>
                            </div>
                         </div>

                         {/* Right Panel: Gantt Bar */}
                         <div className="flex-1 relative h-10 ml-2">
                            <motion.div 
                              initial={{ width: 0, opacity: 0 }}
                              animate={{ width: `${widthPct}%`, opacity: 1 }}
                              transition={{ duration: 0.5, delay: idx * 0.1, type: "spring", bounce: 0.2 }}
                              className={`absolute top-1 bottom-1 rounded-md border flex items-center px-2 overflow-hidden shadow-lg ${
                                isCompleted 
                                  ? 'bg-emerald-500/20 border-emerald-500/50 text-emerald-300' 
                                  : 'bg-blue-600/30 border-blue-500/50 text-blue-200 cursor-pointer hover:bg-blue-500/40 transition-colors'
                              }`}
                              style={{ left: `${leftPct}%` }}
                            >
                              <div className="text-[10px] font-bold truncate">
                                {isCompleted && <Check className="w-3 h-3 inline mr-1" />}
                                {task.title}
                              </div>
                            </motion.div>
                         </div>
                       </div>
                     );
                   })}
                 </div>
               </div>
            )}
          </div>
        </div>

        {/* Right: To-Do & Dynamic Replanning */}
        <div className="flex-1 flex flex-col gap-6">
           <div className="flex-1 bg-slate-900/80 backdrop-blur-md border border-slate-800 rounded-xl overflow-hidden flex flex-col shadow-xl">
             <div className="p-4 border-b border-slate-800 bg-slate-950">
               <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                 <CheckCircle2 className="w-4 h-4 text-emerald-400" /> 
                 Field Checklist
               </h3>
             </div>
             <div className="flex-1 overflow-y-auto p-4 space-y-3">
                {tasks.map(task => {
                  const isCompleted = task.status === 'COMPLETED' || completedTasks.has(task.task_id);
                  return (
                    <div key={task.task_id} className={`bg-slate-800/40 border ${isCompleted ? 'border-emerald-900/50' : 'border-slate-700/50'} rounded-lg p-3 transition-colors`}>
                      <div className="flex items-start gap-3">
                         <button onClick={() => !isCompleted && handleTaskCheck(task.task_id)} className="mt-0.5 cursor-pointer">
                           {isCompleted ? (
                             <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                           ) : (
                             <div className="w-5 h-5 rounded-full border-2 border-slate-600 hover:border-blue-400 transition-colors" />
                           )}
                         </button>
                         <div className="flex-1">
                           <h4 className={`text-sm font-bold transition-colors ${isCompleted ? 'text-emerald-500/70 line-through' : 'text-slate-200'}`}>{task.title}</h4>
                           <p className="text-xs text-slate-500 mt-1">{task.description}</p>
                         </div>
                      </div>
                      {activeTaskPrompt === task.task_id && (
                         <motion.div initial={{opacity:0, height:0}} animate={{opacity:1, height:'auto'}} className="mt-3 pl-8">
                           <div className="bg-slate-900 p-3 rounded border border-slate-700 text-xs">
                              <p className="text-slate-300 mb-2 font-bold uppercase tracking-wider">Was this task completed on time?</p>
                              <div className="flex gap-2">
                                 <button onClick={() => handleTaskTimeSubmit(task.task_id, true)} className="px-3 py-1.5 bg-emerald-600/20 text-emerald-400 border border-emerald-500/50 rounded hover:bg-emerald-600/30 font-semibold transition-colors">Yes, on time</button>
                                 <button onClick={() => handleTaskTimeSubmit(task.task_id, false)} className="px-3 py-1.5 bg-red-600/20 text-red-400 border border-red-500/50 rounded hover:bg-red-600/30 font-semibold transition-colors">No, delayed</button>
                              </div>
                           </div>
                         </motion.div>
                      )}
                    </div>
                  );
                })}
             </div>
           </div>

           <div className="h-[250px] bg-slate-900/80 backdrop-blur-md border border-slate-800 rounded-xl overflow-hidden flex flex-col shadow-xl">
             <div className="p-3 border-b border-slate-800 bg-slate-950 flex items-center gap-2">
                <Zap className="w-4 h-4 text-purple-400" />
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">Replanning Copilot</h3>
             </div>
             <div className="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar">
                {chatMessages.map((msg, i) => (
                  <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-[85%] rounded-xl p-3 text-xs shadow-md ${
                      msg.role === 'user' ? 'bg-blue-600 text-white rounded-br-none' : 'bg-slate-800 border border-slate-700 text-slate-300 rounded-bl-none'
                    }`}>
                      {msg.text}
                    </div>
                  </div>
                ))}
             </div>
             <form onSubmit={handleChat} className="p-2 border-t border-slate-800 bg-slate-950 flex gap-2">
                <input 
                  type="text" 
                  value={chatInput} 
                  onChange={e=>setChatInput(e.target.value)} 
                  placeholder="Report rain, worker absence..." 
                  className="flex-1 bg-slate-900 border border-slate-700 rounded px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-purple-500"
                />
             </form>
           </div>
        </div>
      </div>
    </div>
  );
}
