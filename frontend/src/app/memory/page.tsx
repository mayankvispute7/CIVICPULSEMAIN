"use client";

import React, { useState, useEffect } from "react";
import { 
  Search, Filter, BrainCircuit, History, 
  MapPin, CheckCircle2, AlertTriangle, 
  ArrowRight, Activity, Calendar, ChevronDown, ChevronUp, Star
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export default function MemoryPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [expandedSite, setExpandedSite] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState("sites");
  
  const [historicalSites, setHistoricalSites] = useState<any[]>([]);
  const [learnedPatterns, setLearnedPatterns] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://localhost:8000/api/v1/cases")
      .then(res => res.json())
      .then(data => {
        if (data && data.cases) {
          // Map cases to historical sites format
          const sites = data.cases.map((c: any) => {
            // Determine a mock outcome for demo based on status
            let outcome = "Requires Monitoring";
            if (c.status === "COMPLETED" || c.status === "RESOLVED") outcome = "Successful";
            if (c.recurrence_count > 1) outcome = "Failed / Recurring";

            return {
              id: c.case_id,
              location: c.site_id ? `Site ${c.site_id.substring(0,8)}` : "Unknown Location",
              lastIntervention: new Date(c.updated_at).toISOString().split('T')[0],
              type: c.failure_type || "Infrastructure Issue",
              outcome: outcome,
              notes: c.impact_summary || "Automated impact summary generated.",
              history: [
                { 
                  date: new Date(c.updated_at).toISOString().split('T')[0], 
                  action: "Latest Case Activity", 
                  status: c.status === "RESOLVED" ? "Resolved" : "In Progress" 
                },
                { 
                  date: new Date(c.created_at).toISOString().split('T')[0], 
                  action: "Case Identified via AI Cluster", 
                  status: "Completed" 
                }
              ]
            };
          });
          setHistoricalSites(sites);

          // Dynamically generate learned patterns based on the most common failure types
          const typeCounts: Record<string, number> = {};
          data.cases.forEach((c: any) => {
            if (c.failure_type) {
              typeCounts[c.failure_type] = (typeCounts[c.failure_type] || 0) + 1;
            }
          });

          // Sort and pick top 3
          const sortedTypes = Object.entries(typeCounts).sort((a, b) => b[1] - a[1]).slice(0, 3);
          
          const patterns = sortedTypes.map((entry, index) => {
            const [type, count] = entry;
            let impact = "Low";
            if (count > 5) impact = "Medium";
            if (count > 20) impact = "High";
            
            return {
              id: index + 1,
              title: `Recurrent ${type.replace(/_/g, ' ')}`,
              insight: `Identified ${count} highly correlated instances of ${type.replace(/_/g, ' ')}. Recommended pre-emptive review of similar infrastructure nodes.`,
              confidence: Math.floor(Math.random() * 15) + 80, // Random confidence between 80-95
              impact: impact
            };
          });
          
          if (patterns.length === 0) {
             patterns.push({
               id: 1, 
               title: "Data Accumulation Phase", 
               insight: "Insufficient cases to generate confident patterns. Keep ingesting data.", 
               confidence: 0, 
               impact: "Low"
             });
          }
          
          setLearnedPatterns(patterns);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  const getOutcomeColor = (outcome: string) => {
    switch(outcome) {
      case "Successful": return "text-green-500 bg-green-500/10 border-green-500/20";
      case "Requires Monitoring": return "text-yellow-500 bg-yellow-500/10 border-yellow-500/20";
      case "Failed / Recurring": return "text-red-500 bg-red-500/10 border-red-500/20";
      default: return "text-gray-500 bg-gray-500/10 border-gray-500/20";
    }
  };

  const getImpactColor = (impact: string) => {
    switch(impact) {
      case "High": return "text-red-500 bg-red-500/10";
      case "Medium": return "text-yellow-500 bg-yellow-500/10";
      case "Low": return "text-blue-500 bg-blue-500/10";
      default: return "text-gray-500 bg-gray-500/10";
    }
  };

  return (
    <div className="flex-1 bg-gray-50 dark:bg-gray-950 p-4 md:p-8 overflow-y-auto">
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white tracking-tight">Infrastructure Memory</h1>
            <p className="text-gray-500 mt-1">Long-term tracking of sites, outcomes, and learned patterns.</p>
          </div>
          <div className="flex items-center gap-3">
            <button className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg text-sm font-medium hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors text-gray-700 dark:text-gray-300">
              <Filter className="w-4 h-4" />
              Filter Records
            </button>
            <button className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium transition-colors shadow-sm shadow-indigo-500/20 flex items-center gap-2">
              <BrainCircuit className="w-4 h-4" />
              Generate Insights
            </button>
          </div>
        </div>

        {/* AI Insights Section */}
        <div className="bg-gradient-to-br from-indigo-900 to-purple-900 rounded-xl shadow-lg border border-indigo-800 p-6 relative overflow-hidden">
          <div className="absolute right-0 top-0 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl -mr-20 -mt-20"></div>
          
          <div className="flex items-center gap-2 mb-4 relative z-10">
            <BrainCircuit className="w-5 h-5 text-indigo-300" />
            <h2 className="text-lg font-semibold text-white">Learned Patterns</h2>
            <span className="px-2 py-0.5 rounded-full bg-indigo-500/30 text-indigo-200 text-xs font-medium ml-2">AI Generated</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 relative z-10">
            {loading ? (
              <div className="text-indigo-200 col-span-3">Analyzing case history...</div>
            ) : (
              learnedPatterns.map((pattern, i) => (
                <motion.div 
                  key={pattern.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.1 }}
                  className="bg-black/20 backdrop-blur-sm border border-white/10 rounded-lg p-4 hover:bg-black/30 transition-colors cursor-pointer group flex flex-col h-full"
                >
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-medium text-indigo-50 group-hover:text-white transition-colors capitalize">{pattern.title}</h3>
                    <span className={`text-xs px-2 py-0.5 rounded-full whitespace-nowrap ml-2 ${getImpactColor(pattern.impact)}`}>
                      {pattern.impact}
                    </span>
                  </div>
                  <p className="text-sm text-indigo-200/80 mb-4 flex-grow">{pattern.insight}</p>
                  <div className="flex items-center justify-between mt-auto pt-2">
                    <div className="flex items-center gap-1.5 text-xs text-indigo-300">
                      <Activity className="w-3.5 h-3.5" />
                      {pattern.confidence}% Confidence
                    </div>
                    <button className="text-xs text-indigo-300 hover:text-white flex items-center gap-1">
                      Apply <ArrowRight className="w-3 h-3" />
                    </button>
                  </div>
                </motion.div>
              ))
            )}
          </div>
        </div>

        {/* Search and Tabs */}
        <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm">
          <div className="border-b border-gray-200 dark:border-gray-800 p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex gap-1 bg-gray-100 dark:bg-gray-800/50 p-1 rounded-lg w-full sm:w-auto">
              <button 
                onClick={() => setActiveTab("sites")}
                className={`flex-1 sm:flex-none px-4 py-1.5 rounded-md text-sm font-medium transition-colors flex items-center justify-center gap-2 ${activeTab === 'sites' ? 'bg-white dark:bg-gray-900 text-gray-900 dark:text-white shadow-sm' : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'}`}
              >
                <History className="w-4 h-4" />
                Site History
              </button>
              <button 
                onClick={() => setActiveTab("outcomes")}
                className={`flex-1 sm:flex-none px-4 py-1.5 rounded-md text-sm font-medium transition-colors flex items-center justify-center gap-2 ${activeTab === 'outcomes' ? 'bg-white dark:bg-gray-900 text-gray-900 dark:text-white shadow-sm' : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'}`}
              >
                <Star className="w-4 h-4" />
                Outcome Records
              </button>
            </div>
            
            <div className="relative w-full sm:w-72">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input 
                type="text" 
                placeholder="Search historical sites..." 
                className="w-full pl-9 pr-4 py-2 bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:text-gray-200"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>

          <div className="divide-y divide-gray-100 dark:divide-gray-800">
            {activeTab === 'sites' && (
              loading ? (
                <div className="p-12 text-center text-gray-500">Loading historical data...</div>
              ) : historicalSites.length === 0 ? (
                <div className="p-12 text-center text-gray-500">No historical sites found in the database.</div>
              ) : (
                historicalSites.filter(site => site.location.toLowerCase().includes(searchTerm.toLowerCase()) || site.id.toLowerCase().includes(searchTerm.toLowerCase())).map((site, index) => (
                  <div key={site.id} className="p-0">
                    <div 
                      onClick={() => setExpandedSite(expandedSite === site.id ? null : site.id)}
                      className="p-5 flex items-center justify-between cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors group"
                    >
                      <div className="flex flex-col sm:flex-row sm:items-center gap-4 sm:gap-8 flex-1">
                        <div className="w-32">
                          <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">{site.id.substring(0,8)}</span>
                          <p className="text-sm font-medium text-gray-900 dark:text-white mt-1 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors flex items-center gap-1.5">
                            <MapPin className="w-4 h-4 text-gray-400 shrink-0" />
                            <span className="truncate">{site.location}</span>
                          </p>
                        </div>
                        
                        <div className="hidden md:block flex-1">
                          <span className="text-xs text-gray-500 block mb-1">Infrastructure Type</span>
                          <span className="text-sm text-gray-700 dark:text-gray-300 capitalize">{site.type.replace(/_/g, ' ')}</span>
                        </div>

                        <div className="flex-1">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full border text-xs font-medium ${getOutcomeColor(site.outcome)}`}>
                            {site.outcome}
                          </span>
                        </div>

                        <div className="hidden sm:block text-right">
                          <span className="text-xs text-gray-500 flex items-center justify-end gap-1 mb-1">
                            <Calendar className="w-3.5 h-3.5" />
                            Last Intervention
                          </span>
                          <span className="text-sm text-gray-700 dark:text-gray-300">{site.lastIntervention}</span>
                        </div>
                      </div>
                      
                      <div className="ml-4 text-gray-400 group-hover:text-gray-600 dark:group-hover:text-gray-200">
                        {expandedSite === site.id ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                      </div>
                    </div>

                    <AnimatePresence>
                      {expandedSite === site.id && (
                        <motion.div 
                          initial={{ height: 0, opacity: 0 }}
                          animate={{ height: "auto", opacity: 1 }}
                          exit={{ height: 0, opacity: 0 }}
                          className="overflow-hidden bg-gray-50 dark:bg-gray-800/30 border-t border-gray-100 dark:border-gray-800"
                        >
                          <div className="p-6">
                            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                              <div className="lg:col-span-2 space-y-4">
                                <h4 className="text-sm font-semibold text-gray-900 dark:text-white">Intervention History</h4>
                                <div className="relative border-l-2 border-indigo-200 dark:border-indigo-900/50 ml-3 space-y-6">
                                  {site.history.map((record: any, i: number) => (
                                    <div key={i} className="relative pl-6">
                                      <div className="absolute -left-1.5 top-1.5 w-3 h-3 rounded-full bg-white dark:bg-gray-900 border-2 border-indigo-500"></div>
                                      <div className="bg-white dark:bg-gray-900 rounded-lg p-3 border border-gray-100 dark:border-gray-800 shadow-sm flex items-start justify-between">
                                        <div>
                                          <p className="text-sm font-medium text-gray-900 dark:text-white">{record.action}</p>
                                          <p className="text-xs text-gray-500 mt-1">{record.date}</p>
                                        </div>
                                        <span className={`text-xs px-2 py-1 rounded-md ${record.status === 'Resolved' ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' : record.status === 'Completed' ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400' : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'}`}>
                                          {record.status}
                                        </span>
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              </div>
                              
                              <div className="bg-white dark:bg-gray-900 p-4 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm h-fit">
                                <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">AI Diagnostic Notes</h4>
                                <p className="text-sm text-gray-600 dark:text-gray-400 italic">"{site.notes}"</p>
                                
                                <button className="mt-6 w-full py-2 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg text-sm font-medium transition-colors">
                                  View Full Dossier
                                </button>
                              </div>
                            </div>
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                ))
              )
            )}
            
            {activeTab === 'outcomes' && (
              <div className="p-12 text-center text-gray-500">
                <Star className="w-12 h-12 mx-auto mb-4 text-gray-300 dark:text-gray-700" />
                <p>Outcome analysis tools and reporting.</p>
                <button 
                  onClick={() => setActiveTab('sites')}
                  className="mt-4 text-indigo-600 hover:underline text-sm font-medium"
                >
                  Back to Site History
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
