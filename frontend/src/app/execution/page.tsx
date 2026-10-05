"use client";

import React, { useState, useEffect } from "react";
import { 
  ClipboardList, 
  Clock, 
  CheckCircle2, 
  AlertTriangle,
  MapPin,
  Camera,
  CalendarDays,
  MoreVertical,
  Filter,
  Search,
  UploadCloud,
  Loader2
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

const stats = [
  { label: "Active Work Orders", value: "Loading...", icon: ClipboardList, color: "text-blue-500", bg: "bg-blue-500/10" },
  { label: "Pending Verification", value: "0", icon: Camera, color: "text-amber-500", bg: "bg-amber-500/10" },
  { label: "Replanned (7d)", value: "0", icon: AlertTriangle, color: "text-red-500", bg: "bg-red-500/10" },
  { label: "Completed (Today)", value: "0", icon: CheckCircle2, color: "text-green-500", bg: "bg-green-500/10" }
];

const evidence = [
  { id: 1, type: "Status", wo: "SYSTEM", desc: "Data synchronization complete", user: "Auto", time: "Just now" },
];

export default function ExecutionPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [cases, setCases] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [localStatuses, setLocalStatuses] = useState<Record<string, string>>({});
  
  // Image Upload State
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(null);
  const [verifying, setVerifying] = useState(false);
  const [verificationResult, setVerificationResult] = useState<{status: 'real' | 'fake', message: string} | null>(null);

  useEffect(() => {
    fetch("http://localhost:8000/api/v1/cases")
      .then(res => res.json())
      .then(data => {
        if (data && data.cases) {
          setCases(data.cases);
          // Initialize all as In Progress
          const initialStatuses: Record<string, string> = {};
          data.cases.forEach((c: any) => {
            initialStatuses[c.case_id] = "In Progress";
          });
          setLocalStatuses(initialStatuses);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  const handleStatusChange = (caseId: string, newStatus: string) => {
    if (newStatus === "Completed") {
      setSelectedCaseId(caseId);
      setUploadModalOpen(true);
      setVerificationResult(null);
    } else {
      setLocalStatuses(prev => ({ ...prev, [caseId]: newStatus }));
    }
  };

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setVerifying(true);
      setVerificationResult(null);
      
      // Simulate AI Verification
      setTimeout(() => {
        setVerifying(false);
        // Randomly succeed or fail for demo purposes
        const isFake = Math.random() > 0.5;
        if (isFake) {
          setVerificationResult({
            status: 'fake',
            message: 'AI Detected anomalies: Inconsistent lighting and synthetic textures. This image appears to be manipulated or generated.'
          });
        } else {
          setVerificationResult({
            status: 'real',
            message: 'Image verified. No manipulation detected. Work order marked as completed.'
          });
          if (selectedCaseId) {
            setLocalStatuses(prev => ({ ...prev, [selectedCaseId]: "Completed" }));
          }
        }
      }, 3000);
    }
  };

  const getStatusColor = (status: string) => {
    switch(status) {
      case "In Progress": return "bg-blue-500/10 text-blue-500 border-blue-500/20";
      case "Replanned": return "bg-red-500/10 text-red-500 border-red-500/20";
      case "Pending Verification": return "bg-amber-500/10 text-amber-500 border-amber-500/20";
      case "Completed": return "bg-green-500/10 text-green-500 border-green-500/20";
      default: return "bg-gray-500/10 text-gray-500 border-gray-500/20";
    }
  };

  // Calculate dynamic stats
  const activeCount = Object.values(localStatuses).filter(s => s === "In Progress").length;
  const pendingCount = Object.values(localStatuses).filter(s => s === "Pending Verification").length;
  const replannedCount = Object.values(localStatuses).filter(s => s === "Replanned").length;
  const completedCount = Object.values(localStatuses).filter(s => s === "Completed").length;

  return (
    <div className="flex-1 bg-gray-50 dark:bg-gray-950 p-4 md:p-8 overflow-y-auto relative">
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white tracking-tight">Execution Center</h1>
            <p className="text-gray-500 mt-1">Monitor active work orders, replanning events, and field evidence verification.</p>
          </div>
          <div className="flex items-center gap-3">
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input 
                type="text" 
                placeholder="Search orders..." 
                className="pl-9 pr-4 py-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:text-gray-200"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <button className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg text-sm font-medium hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors text-gray-700 dark:text-gray-300">
              <Filter className="w-4 h-4" />
              Filter
            </button>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <motion.div className="bg-white dark:bg-gray-900 p-6 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Active Work Orders</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">{loading ? "..." : activeCount}</p>
            </div>
            <div className="w-12 h-12 rounded-full flex items-center justify-center bg-blue-500/10"><ClipboardList className="w-6 h-6 text-blue-500" /></div>
          </motion.div>
          
          <motion.div className="bg-white dark:bg-gray-900 p-6 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Pending Verification</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">{loading ? "..." : pendingCount}</p>
            </div>
            <div className="w-12 h-12 rounded-full flex items-center justify-center bg-amber-500/10"><Camera className="w-6 h-6 text-amber-500" /></div>
          </motion.div>

          <motion.div className="bg-white dark:bg-gray-900 p-6 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Replanned Tasks</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">{loading ? "..." : replannedCount}</p>
            </div>
            <div className="w-12 h-12 rounded-full flex items-center justify-center bg-red-500/10"><AlertTriangle className="w-6 h-6 text-red-500" /></div>
          </motion.div>

          <motion.div className="bg-white dark:bg-gray-900 p-6 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Completed (Today)</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">{loading ? "..." : completedCount}</p>
            </div>
            <div className="w-12 h-12 rounded-full flex items-center justify-center bg-green-500/10"><CheckCircle2 className="w-6 h-6 text-green-500" /></div>
          </motion.div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content - Work Orders */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm overflow-visible">
              <div className="p-6 border-b border-gray-200 dark:border-gray-800 flex items-center justify-between">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Uploaded Cases as Work Orders</h2>
              </div>
              <div className="divide-y divide-gray-100 dark:divide-gray-800">
                {loading ? (
                  <div className="p-12 text-center text-gray-500">Loading cases from database...</div>
                ) : cases.length === 0 ? (
                  <div className="p-12 text-center text-gray-500">No active cases found. Upload CSV first.</div>
                ) : (
                  cases.filter(c => c.title.toLowerCase().includes(searchTerm.toLowerCase())).map((c, i) => {
                    const status = localStatuses[c.case_id] || "In Progress";
                    return (
                      <motion.div 
                        key={c.case_id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: Math.min(i * 0.05, 1) }}
                        className="p-5 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors group"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex gap-4">
                            <div className={`mt-1 px-2.5 py-0.5 rounded-full border text-xs font-medium whitespace-nowrap ${getStatusColor(status)}`}>
                              {status}
                            </div>
                            <div>
                              <div className="flex items-center gap-2">
                                <h3 className="text-base font-semibold text-gray-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                                  {c.title}
                                </h3>
                              </div>
                              <div className="flex flex-wrap items-center gap-4 mt-2 text-sm text-gray-500 dark:text-gray-400">
                                <span className="flex items-center gap-1.5"><MapPin className="w-3.5 h-3.5" /> Site: {c.site_id?.substring(0,8) || "Unknown"}</span>
                                <span className="flex items-center gap-1.5"><ClipboardList className="w-3.5 h-3.5" /> ID: {c.case_id.substring(0,8)}</span>
                              </div>
                            </div>
                          </div>
                          
                          {/* Actions */}
                          <div className="flex items-center gap-2 relative">
                             <select 
                                className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 text-sm rounded-lg px-2 py-1 text-gray-700 dark:text-gray-300 focus:ring-blue-500 focus:border-blue-500"
                                value={status}
                                onChange={(e) => handleStatusChange(c.case_id, e.target.value)}
                              >
                                <option value="In Progress">Active (In Progress)</option>
                                <option value="Pending Verification">Pending Verification</option>
                                <option value="Replanned">Replanned</option>
                                <option value="Completed">Completed</option>
                             </select>
                          </div>
                        </div>
                      </motion.div>
                    );
                  })
                )}
              </div>
            </div>
          </div>

          {/* Sidebar - Evidence & Updates */}
          <div className="space-y-6">
            <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm p-6">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">Field Updates & Evidence</h2>
              
              <div className="relative border-l-2 border-gray-100 dark:border-gray-800 ml-3 space-y-6">
                {evidence.map((item, i) => (
                  <div key={item.id} className="relative pl-6">
                    <div className="absolute -left-1.5 top-1.5 w-3 h-3 rounded-full bg-white dark:bg-gray-900 border-2 border-blue-500"></div>
                    <div className="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-3 border border-gray-100 dark:border-gray-800">
                      <div className="flex justify-between items-start mb-1">
                        <span className="text-xs font-semibold text-blue-600 dark:text-blue-400">{item.wo}</span>
                        <span className="text-xs text-gray-400">{item.time}</span>
                      </div>
                      <p className="text-sm text-gray-700 dark:text-gray-300 mb-2">{item.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* AI Verification Modal */}
      <AnimatePresence>
        {uploadModalOpen && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4"
          >
            <motion.div 
              initial={{ scale: 0.95 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0.95 }}
              className="bg-white dark:bg-gray-900 rounded-xl shadow-2xl max-w-md w-full overflow-hidden border border-gray-200 dark:border-gray-800"
            >
              <div className="p-6">
                <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">Verify Work Completion</h2>
                <p className="text-sm text-gray-500 mb-6">Upload an image of the completed work. Our AI will analyze the image to detect any signs of manipulation or fake completion.</p>
                
                <div className="border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-xl p-8 text-center hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors relative">
                  <input 
                    type="file" 
                    accept="image/*" 
                    onChange={handleImageUpload}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                  />
                  <UploadCloud className="w-10 h-10 text-blue-500 mx-auto mb-3" />
                  <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Click or drag image to upload</p>
                  <p className="text-xs text-gray-500 mt-1">JPEG, PNG up to 10MB</p>
                </div>

                {verifying && (
                  <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg flex items-center gap-3 border border-blue-100 dark:border-blue-800">
                    <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
                    <div>
                      <p className="text-sm font-semibold text-blue-800 dark:text-blue-300">AI Analysis in progress...</p>
                      <p className="text-xs text-blue-600 dark:text-blue-400">Checking for synthetic textures and lighting anomalies.</p>
                    </div>
                  </div>
                )}

                {verificationResult && (
                  <div className={`mt-6 p-4 rounded-lg flex items-start gap-3 border ${verificationResult.status === 'fake' ? 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800' : 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800'}`}>
                    {verificationResult.status === 'fake' ? (
                      <AlertTriangle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
                    ) : (
                      <CheckCircle2 className="w-5 h-5 text-green-500 shrink-0 mt-0.5" />
                    )}
                    <div>
                      <p className={`text-sm font-semibold ${verificationResult.status === 'fake' ? 'text-red-800 dark:text-red-300' : 'text-green-800 dark:text-green-300'}`}>
                        {verificationResult.status === 'fake' ? 'Verification Failed' : 'Verification Successful'}
                      </p>
                      <p className={`text-xs mt-1 ${verificationResult.status === 'fake' ? 'text-red-600 dark:text-red-400' : 'text-green-600 dark:text-green-400'}`}>
                        {verificationResult.message}
                      </p>
                    </div>
                  </div>
                )}
              </div>
              <div className="bg-gray-50 dark:bg-gray-800 p-4 flex justify-end gap-3 border-t border-gray-200 dark:border-gray-700">
                <button 
                  onClick={() => setUploadModalOpen(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors"
                >
                  Close
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
