import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { casesApi } from "@/services/api";
import { motion, AnimatePresence } from "framer-motion";
import { HistoryResponse } from "@/types/api";
import { 
  AlertTriangle, ArrowRight, Activity, Clock, FileWarning, AlertCircle, TrendingUp, Info, CheckCircle2
} from "lucide-react";
import {
  AreaChart, Area, XAxis, YAxis, Tooltip as RechartsTooltip, ResponsiveContainer, CartesianGrid, ComposedChart, Line
} from "recharts";

export function PredictView({ caseId, history }: { caseId: string, history?: HistoryResponse }) {
  const { data: prediction, isLoading, error } = useQuery({
    queryKey: ['case-prediction', caseId],
    queryFn: () => casesApi.getCasePrediction(caseId),
    enabled: !!caseId
  });

  const [loadingStep, setLoadingStep] = useState(0);
  const loadingSteps = [
    "Reading historical incidents...",
    "Analyzing recurrence...",
    "Evaluating infrastructure signals...",
    "Building baseline...",
    "Generating 5-year screening..."
  ];

  useEffect(() => {
    if (isLoading) {
      const interval = setInterval(() => {
        setLoadingStep(s => (s < loadingSteps.length - 1 ? s + 1 : s));
      }, 600);
      return () => clearInterval(interval);
    }
  }, [isLoading]);

  const CountUp = ({ to, duration = 2 }: { to: number, duration?: number }) => {
    const [count, setCount] = useState(0);
    useEffect(() => {
      let startTime: number;
      let animationFrame: number;
      const animate = (timestamp: number) => {
        if (!startTime) startTime = timestamp;
        const progress = (timestamp - startTime) / (duration * 1000);
        if (progress < 1) {
          setCount(Math.floor(progress * to));
          animationFrame = requestAnimationFrame(animate);
        } else {
          setCount(to);
        }
      };
      animationFrame = requestAnimationFrame(animate);
      return () => cancelAnimationFrame(animationFrame);
    }, [to, duration]);
    return <span>{count}</span>;
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-full min-h-[500px] text-slate-300">
        <Activity className="w-12 h-12 text-blue-500 mb-6 animate-pulse" />
        <h2 className="text-xl font-bold tracking-widest uppercase mb-6 text-slate-100">Analyzing Case History</h2>
        <div className="space-y-3 w-64">
          {loadingSteps.map((step, i) => (
            <div key={i} className={`text-sm flex items-center gap-3 transition-opacity duration-500 ${i <= loadingStep ? 'opacity-100' : 'opacity-0'}`}>
              <div className={`w-2 h-2 rounded-full ${i === loadingStep ? 'bg-blue-400 animate-ping' : 'bg-emerald-500'}`} />
              <span className={i === loadingStep ? 'text-blue-200' : 'text-slate-400'}>{step}</span>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error || !prediction) {
    return (
      <div className="flex flex-col items-center justify-center h-full min-h-[400px]">
        <AlertTriangle className="w-12 h-12 text-red-500 mb-4" />
        <h2 className="text-xl font-bold text-red-400 tracking-widest uppercase mb-2">Prediction Unavailable</h2>
        <p className="text-red-400/70 text-sm">{(error as any)?.message || "Failed to load prediction model data."}</p>
      </div>
    );
  }

  const riskPercentage = Math.round(prediction.current_risk_score * 100);
  const riskColor = riskPercentage >= 80 ? 'text-red-500' : riskPercentage >= 60 ? 'text-orange-500' : riskPercentage >= 40 ? 'text-yellow-500' : 'text-emerald-500';
  const riskBg = riskPercentage >= 80 ? 'bg-red-500' : riskPercentage >= 60 ? 'bg-orange-500' : riskPercentage >= 40 ? 'bg-yellow-500' : 'bg-emerald-500';

  const containerVariants = { hidden: { opacity: 0 }, show: { opacity: 1, transition: { staggerChildren: 0.15 } } };
  const itemVariants = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0, transition: { duration: 0.5, ease: "easeOut" } } };

  // Setup Timeline Events
  const timelineEvents = [];
  if (history?.historical_incidents) {
    [...history.historical_incidents].sort((a, b) => new Date(a.occurred_at).getTime() - new Date(b.occurred_at).getTime()).forEach((inc) => {
      const year = new Date(inc.occurred_at).getFullYear();
      if (inc.intervention_taken) {
        timelineEvents.push({ year, label: "Intervention", desc: inc.intervention_taken, type: 'intervention' });
        if (inc.recurrence_after_days) {
          const nextYear = new Date(new Date(inc.occurred_at).getTime() + inc.recurrence_after_days * 24 * 60 * 60 * 1000).getFullYear();
          timelineEvents.push({ year: nextYear, label: "Recurrence", desc: inc.intervention_outcome || "Failed", type: 'recurrence' });
        }
      } else {
        timelineEvents.push({ year, label: "Incident", desc: inc.title, type: 'incident' });
      }
    });
  }
  const currentYear = new Date().getFullYear();
  timelineEvents.push({ year: currentYear, label: "Current Case", desc: `${history?.previous_complaints?.length || 0} active reports`, type: 'current' });
  const displayTimeline = timelineEvents.filter((v, i, a) => a.findIndex(t => (t.label === v.label && t.year === v.year)) === i);

  // Setup Chart Data
  const chartData = prediction.yearly_projection.map((y: any) => ({
    year: y.year,
    risk: y.risk * 100,
    incidents: [y.incident_min, y.incident_max],
    complaints: [y.complaint_min, y.complaint_max],
    incidentAvg: (y.incident_min + y.incident_max) / 2,
    complaintAvg: (y.complaint_min + y.complaint_max) / 2,
    exposure: y.exposure,
    data_origin: y.data_origin,
    raw: y
  }));

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload.raw;
      return (
        <div className="bg-slate-900 border border-slate-700 p-4 rounded-lg shadow-xl text-sm min-w-[200px]">
          <div className="font-black text-lg mb-2 text-slate-100">{label}</div>
          <div className="flex justify-between items-center mb-1">
            <span className="text-slate-400">Risk:</span>
            <span className={`font-bold ${data.risk >= 0.8 ? 'text-red-400' : 'text-orange-400'}`}>{Math.round(data.risk * 100)}% ({data.exposure})</span>
          </div>
          <div className="flex justify-between items-center mb-1">
            <span className="text-slate-400">Expected incidents:</span>
            <span className="font-bold text-slate-200">{data.incident_min}–{data.incident_max}</span>
          </div>
          <div className="flex justify-between items-center mb-3">
            <span className="text-slate-400">Expected complaints:</span>
            <span className="font-bold text-slate-200">{data.complaint_min}–{data.complaint_max}</span>
          </div>
          <div className="text-[10px] uppercase tracking-wider text-slate-500 border-t border-slate-800 pt-2 text-right">
            {data.data_origin.replace('_', ' ')}
          </div>
        </div>
      );
    }
    return null;
  };

  const handleExplore = () => {
    // Attempt to click the actual workspace Next button
    const btns = Array.from(document.querySelectorAll('button'));
    const nextBtn = btns.find(b => b.textContent?.includes('Explore Solutions') || b.textContent?.includes('Simulate'));
    if (nextBtn) nextBtn.click();
  };

  return (
    <div className="bg-slate-950/80 border border-slate-800/80 rounded-2xl p-8 shadow-2xl h-full mx-auto w-full overflow-y-auto custom-scrollbar relative">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/10 via-slate-900/0 to-slate-900/0 pointer-events-none" />
      
      <motion.div variants={containerVariants} initial="hidden" animate="show" className="relative z-10 flex flex-col max-w-4xl mx-auto gap-12 pb-12">
        
        {/* HEADER */}
        <motion.div variants={itemVariants} className="text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-900/20 border border-blue-800/50 text-blue-400 text-[10px] font-bold uppercase tracking-widest shadow-sm mb-4">
            MODEL ESTIMATION · SCREENING LEVEL
          </div>
          <h1 className="text-4xl font-black text-slate-100 tracking-tight mb-2">PREDICT</h1>
          <h2 className="text-xl text-slate-400 tracking-wide">What If We Do Nothing?</h2>
          <p className="text-sm text-slate-500 mt-4 max-w-lg mx-auto">
            Screen the likely recurrence of this infrastructure failure if current conditions remain unchanged.
          </p>
        </motion.div>

        {/* HERO - CURRENT RISK */}
        <motion.div variants={itemVariants} className="flex flex-col items-center bg-slate-900/60 p-8 rounded-2xl border border-slate-800 relative overflow-hidden shadow-xl">
          <div className="text-xs font-bold uppercase tracking-widest text-slate-500 mb-6">Current Recurrence Risk</div>
          
          <div className="relative flex flex-col items-center justify-end h-40 mb-2 w-full">
            {/* Animated Gauge Background */}
            <svg className="absolute top-0 w-64 h-32" viewBox="0 0 100 50">
              <path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="#1e293b" strokeWidth="8" strokeLinecap="round" />
              <motion.path 
                d="M 10 50 A 40 40 0 0 1 90 50" 
                fill="none" 
                stroke="currentColor" 
                className={riskColor}
                strokeWidth="8" 
                strokeLinecap="round"
                initial={{ pathLength: 0 }}
                animate={{ pathLength: prediction.current_risk_score }}
                transition={{ duration: 1.5, ease: "easeOut" }}
              />
            </svg>
            <div className="flex flex-col items-center z-10 pt-16">
              <div className={`text-6xl font-black tracking-tighter ${riskColor} leading-none`}>
                <CountUp to={riskPercentage} />%
              </div>
              <div className={`text-sm font-bold uppercase tracking-widest mt-2 px-3 py-1 bg-slate-900 rounded-full border border-slate-700 ${riskColor}`}>
                {prediction.risk_level}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-3 w-full border-t border-slate-800 mt-6 pt-6">
            <div className="text-center border-r border-slate-800 px-4">
              <div className="text-3xl font-black text-slate-200 mb-1">{history?.previous_complaints?.length || 0}</div>
              <div className="text-[10px] uppercase tracking-wider text-slate-500 font-bold">Related Complaints</div>
            </div>
            <div className="text-center border-r border-slate-800 px-4">
              <div className="text-3xl font-black text-slate-200 mb-1">{history?.historical_incidents?.length || 0}</div>
              <div className="text-[10px] uppercase tracking-wider text-slate-500 font-bold">Historical Incidents</div>
            </div>
            <div className="text-center px-4">
              <div className="text-3xl font-black text-slate-200 mb-1">{history?.historical_incidents?.filter(i => i.intervention_taken)?.length || 0}</div>
              <div className="text-[10px] uppercase tracking-wider text-slate-500 font-bold">Previous Interventions</div>
            </div>
          </div>
        </motion.div>

        {/* EVIDENCE CHAIN */}
        <motion.div variants={itemVariants} className="w-full">
          <div className="text-center mb-8">
            <h3 className="text-sm font-bold uppercase tracking-widest text-slate-400">Why does the model expect recurrence?</h3>
          </div>
          <div className="flex flex-col items-center gap-3">
            {prediction.evidence_basis.map((ev: any, idx: number) => (
              <motion.div 
                key={idx}
                initial={{ opacity: 0, y: 10 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: idx * 0.15 }}
                className="w-full max-w-xl group cursor-pointer"
              >
                {idx > 0 && (
                  <div className="flex justify-center mb-3 text-slate-700">
                    <ArrowRight className="w-4 h-4 rotate-90" />
                  </div>
                )}
                <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl flex items-center justify-between hover:border-blue-500/30 transition-colors shadow-sm group-hover:bg-slate-800/50">
                  <div className="flex flex-col">
                    <span className="text-sm font-bold text-slate-300">{ev.label}</span>
                    <span className="text-xs text-slate-500 mt-1">{ev.value}</span>
                  </div>
                  <div className="flex flex-col items-end gap-1">
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider ${
                      ev.confidence === 'HIGH' ? 'bg-emerald-900/30 text-emerald-400 border border-emerald-800/50' : 
                      ev.confidence === 'MEDIUM' ? 'bg-yellow-900/30 text-yellow-400 border border-yellow-800/50' : 
                      'bg-slate-800 text-slate-400 border border-slate-700'
                    }`}>
                      {ev.confidence} CONFIDENCE
                    </span>
                    <span className="text-[9px] text-slate-600 uppercase tracking-widest">{ev.data_origin.replace('_', ' ')}</span>
                  </div>
                </div>
              </motion.div>
            ))}
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: prediction.evidence_basis.length * 0.15 }}
              className="mt-3 text-center"
            >
              <div className="flex justify-center mb-3 text-red-900/50">
                <ArrowRight className="w-5 h-5 rotate-90 text-red-500/50" />
              </div>
              <div className="bg-red-900/20 border border-red-800/50 px-6 py-3 rounded-xl inline-flex items-center gap-2 shadow-inner">
                <AlertCircle className="w-4 h-4 text-red-400" />
                <span className="text-sm font-black uppercase tracking-widest text-red-400">Recurrence Risk</span>
              </div>
            </motion.div>
          </div>
        </motion.div>

        {/* HISTORICAL TIMELINE */}
        {displayTimeline.length > 0 && (
          <motion.div variants={itemVariants} className="w-full bg-slate-900/40 border border-slate-800 p-8 rounded-2xl">
            <h3 className="text-sm font-bold uppercase tracking-widest text-slate-400 mb-8">Historical Timeline</h3>
            <div className="relative">
              {/* Main Line */}
              <motion.div 
                className="absolute top-1/2 left-0 h-0.5 bg-slate-700 -translate-y-1/2 rounded-full"
                initial={{ width: 0 }}
                whileInView={{ width: '100%' }}
                viewport={{ once: true }}
                transition={{ duration: 1, ease: "easeInOut" }}
              />
              
              <div className="flex justify-between relative z-10">
                {displayTimeline.map((item, idx) => (
                  <motion.div 
                    key={idx}
                    initial={{ opacity: 0, scale: 0.8 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    viewport={{ once: true }}
                    transition={{ delay: idx * 0.2 }}
                    className="flex flex-col items-center group relative cursor-pointer"
                  >
                    <div className="text-xs font-bold text-slate-500 mb-3">{item.year}</div>
                    
                    <div className={`w-4 h-4 rounded-full border-2 bg-slate-950 transition-colors ${
                      item.type === 'current' ? 'border-red-500 bg-red-900/50 shadow-[0_0_10px_rgba(239,68,68,0.5)]' :
                      item.type === 'intervention' ? 'border-blue-500' :
                      item.type === 'recurrence' ? 'border-orange-500' : 'border-slate-500'
                    }`} />
                    
                    <div className="absolute top-12 left-1/2 -translate-x-1/2 w-32 opacity-0 group-hover:opacity-100 transition-opacity bg-slate-800 border border-slate-700 p-2 rounded shadow-xl pointer-events-none z-20">
                      <div className="text-[10px] font-bold text-slate-300 uppercase">{item.label}</div>
                      <div className="text-[10px] text-slate-400 mt-1 truncate">{item.desc}</div>
                      <div className="text-[8px] text-slate-500 uppercase mt-2 text-right">
                        {item.type === 'current' ? 'REAL DATA' : 'REAL DATA / SYNTHETIC DEMO'}
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
            <div className="mt-8 text-center text-xs font-bold text-orange-400/80 uppercase tracking-widest bg-orange-900/10 py-2 rounded">
              The failure has recurred before.
            </div>
          </motion.div>
        )}

        {/* 5-YEAR DO-NOTHING FORECAST */}
        <motion.div variants={itemVariants} className="w-full bg-slate-900/80 border border-slate-700/80 p-8 rounded-2xl shadow-2xl">
          <div className="text-center mb-8">
            <h3 className="text-xl font-black text-slate-100 uppercase tracking-widest mb-2">5-Year Do-Nothing Baseline</h3>
            <p className="text-sm text-slate-400">Screening estimate if no new intervention changes the current infrastructure condition.</p>
          </div>
          
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={chartData} margin={{ top: 20, right: 0, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorRisk" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                <XAxis dataKey="year" stroke="#475569" tick={{fill: '#64748b', fontSize: 12}} axisLine={false} tickLine={false} />
                <YAxis yAxisId="left" stroke="#475569" tick={{fill: '#64748b', fontSize: 12}} axisLine={false} tickLine={false} />
                <YAxis yAxisId="right" orientation="right" stroke="#475569" tick={{fill: '#64748b', fontSize: 12}} axisLine={false} tickLine={false} />
                <RechartsTooltip content={<CustomTooltip />} cursor={{fill: '#1e293b', opacity: 0.4}} />
                
                {/* Expected Incident Range Area */}
                <Area yAxisId="left" type="monotone" dataKey="incidentAvg" stroke="none" fill="url(#colorRisk)" />
                <Line yAxisId="left" type="monotone" dataKey="incidentAvg" stroke="#ef4444" strokeWidth={3} dot={{r: 4, fill: '#ef4444', strokeWidth: 2, stroke: '#0f172a'}} activeDot={{r: 6}} />
                
                {/* Complaint Burden Line */}
                <Line yAxisId="right" type="monotone" dataKey="complaintAvg" stroke="#3b82f6" strokeWidth={2} strokeDasharray="5 5" dot={{r: 3, fill: '#3b82f6', strokeWidth: 0}} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
          <div className="flex justify-center gap-8 mt-6">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-red-500" />
              <span className="text-xs text-slate-400">Expected Recurrences (Average)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-0.5 bg-blue-500 border border-dashed" />
              <span className="text-xs text-slate-400">Expected Complaint Burden</span>
            </div>
          </div>
        </motion.div>

        {/* DO-NOTHING SUMMARY */}
        <motion.div variants={itemVariants} className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl text-center flex flex-col justify-center">
            <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-2">Expected Recurrences (5y)</div>
            <div className="text-2xl font-black text-red-400"><CountUp to={prediction.expected_incidents.min} />–<CountUp to={prediction.expected_incidents.max} /></div>
          </div>
          <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl text-center flex flex-col justify-center">
            <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-2">Complaint Burden (5y)</div>
            <div className="text-2xl font-black text-blue-400"><CountUp to={prediction.expected_complaints.min} />–<CountUp to={prediction.expected_complaints.max} /></div>
          </div>
          <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl text-center flex flex-col justify-center">
            <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-2">Current Exposure</div>
            <div className={`text-2xl font-black ${prediction.exposure_level === 'HIGH' || prediction.exposure_level === 'CRITICAL' ? 'text-orange-500' : 'text-slate-300'}`}>
              {prediction.exposure_level}
            </div>
          </div>
          <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl text-center flex flex-col justify-center">
            <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-2">Recurrence Probability</div>
            <div className="text-2xl font-black text-slate-200"><CountUp to={riskPercentage} />%</div>
          </div>
        </motion.div>

        {/* UNCERTAINTY & METHODOLOGY */}
        <motion.div variants={itemVariants} className="grid md:grid-cols-2 gap-6">
          <div className="bg-slate-900/50 border border-slate-800/80 p-6 rounded-xl">
            <div className="flex items-center gap-2 mb-4">
              <Info className="w-5 h-5 text-slate-400" />
              <h4 className="text-xs font-bold uppercase tracking-widest text-slate-300">What the model does not know</h4>
            </div>
            <ul className="space-y-3">
              {prediction.uncertainties.map((unc: string, i: number) => (
                <li key={i} className="flex gap-3 text-sm text-slate-400 items-start">
                  <div className="w-1.5 h-1.5 rounded-full bg-slate-700 mt-1.5 shrink-0" />
                  <span>{unc}</span>
                </li>
              ))}
            </ul>
            <div className="mt-6 pt-4 border-t border-slate-800/50">
              <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">Model Limitations</div>
              <p className="text-xs text-slate-500 italic">These values are screening-level estimates, not calibrated flood-depth or weather predictions.</p>
            </div>
          </div>
          
          <div className="bg-slate-900/50 border border-slate-800/80 p-6 rounded-xl flex flex-col">
            <div className="flex items-center gap-2 mb-4">
              <Activity className="w-5 h-5 text-slate-400" />
              <h4 className="text-xs font-bold uppercase tracking-widest text-slate-300">How was this estimate created?</h4>
            </div>
            <div className="text-sm text-slate-400 mb-6">
              {prediction.methodology}
            </div>
            <div className="mt-auto">
              <div className="flex items-center justify-between text-xs text-slate-500 font-bold uppercase tracking-widest mb-2">
                <span>Evidence</span> <span>→</span> <span>Weighted Model</span> <span>→</span> <span>Baseline</span>
              </div>
              <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden flex">
                <div className="h-full bg-emerald-500/50" style={{ width: '25%' }} title="Historical 25%" />
                <div className="h-full bg-blue-500/50" style={{ width: '20%' }} title="Rainfall 20%" />
                <div className="h-full bg-orange-500/50" style={{ width: '25%' }} title="Infrastructure 25%" />
                <div className="h-full bg-purple-500/50" style={{ width: '15%' }} title="Complaints 15%" />
                <div className="h-full bg-slate-500/50" style={{ width: '15%' }} title="Previous 15%" />
              </div>
            </div>
          </div>
        </motion.div>

        {/* BASELINE ESTABLISHED & TRANSITION */}
        <motion.div variants={itemVariants} className="mt-8 border-t border-slate-800 pt-12 flex flex-col items-center">
          <div className="inline-flex items-center gap-3 px-6 py-2 rounded-full bg-slate-800 border border-slate-700 text-slate-300 shadow-sm mb-6">
            <CheckCircle2 className="w-4 h-4 text-emerald-500" />
            <span className="text-xs font-bold uppercase tracking-widest">Baseline Established</span>
          </div>
          <p className="text-sm text-slate-400 mb-8 text-center max-w-md">
            Future intervention scenarios will be compared against this do-nothing baseline.
          </p>

          <button 
            onClick={handleExplore}
            className="group flex items-center gap-3 px-8 py-4 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-bold uppercase tracking-widest transition-all shadow-lg shadow-blue-900/20 hover:shadow-blue-500/20 hover:scale-105"
          >
            Explore Interventions
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </button>
        </motion.div>
      </motion.div>
    </div>
  );
}
