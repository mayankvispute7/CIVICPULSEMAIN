"use client";

import React, { useState } from "react";
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
  Search
} from "lucide-react";
import { motion } from "framer-motion";

// Mock data
const stats = [
  { label: "Active Work Orders", value: "24", icon: ClipboardList, color: "text-blue-500", bg: "bg-blue-500/10" },
  { label: "Pending Verification", value: "12", icon: Camera, color: "text-amber-500", bg: "bg-amber-500/10" },
  { label: "Replanned (7d)", value: "3", icon: AlertTriangle, color: "text-red-500", bg: "bg-red-500/10" },
  { label: "Completed (Today)", value: "8", icon: CheckCircle2, color: "text-green-500", bg: "bg-green-500/10" }
];

const workOrders = [
  { id: "WO-2023-089", title: "Pothole Repair - 5th Ave", location: "Downtown District", status: "In Progress", priority: "High", assignee: "Crew Alpha", time: "Started 2h ago" },
  { id: "WO-2023-090", title: "Traffic Light Sync", location: "Main St & 4th", status: "Delayed", priority: "Critical", assignee: "Traffic Ops", time: "Delayed by 1h" },
  { id: "WO-2023-091", title: "Street Sweeping", location: "Westside Zone", status: "Scheduled", priority: "Medium", assignee: "Sanitation B", time: "Starts in 30m" },
  { id: "WO-2023-092", title: "Graffiti Removal", location: "Central Park", status: "Completed", priority: "Low", assignee: "Parks Dept", time: "Completed 1h ago" },
];

const evidence = [
  { id: 1, type: "Photo", wo: "WO-2023-092", desc: "Before & After uploaded", user: "J. Smith", time: "10 min ago" },
  { id: 2, type: "Status", wo: "WO-2023-089", desc: "Arrived at location", user: "T. Johnson", time: "45 min ago" },
  { id: 3, type: "Issue", wo: "WO-2023-090", desc: "Equipment malfunction reported", user: "M. Davis", time: "1 hour ago" },
];

export default function ExecutionPage() {
  const [searchTerm, setSearchTerm] = useState("");

  const getStatusColor = (status: string) => {
    switch(status) {
      case "In Progress": return "bg-blue-500/10 text-blue-500 border-blue-500/20";
      case "Delayed": return "bg-red-500/10 text-red-500 border-red-500/20";
      case "Scheduled": return "bg-gray-500/10 text-gray-500 border-gray-500/20";
      case "Completed": return "bg-green-500/10 text-green-500 border-green-500/20";
      default: return "bg-gray-500/10 text-gray-500 border-gray-500/20";
    }
  };

  const getPriorityIcon = (priority: string) => {
    switch(priority) {
      case "Critical": return <AlertTriangle className="w-4 h-4 text-red-500" />;
      case "High": return <AlertTriangle className="w-4 h-4 text-orange-500" />;
      case "Medium": return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
      case "Low": return <AlertTriangle className="w-4 h-4 text-blue-500" />;
      default: return null;
    }
  };

  return (
    <div className="flex-1 bg-gray-50 dark:bg-gray-950 p-4 md:p-8 overflow-y-auto">
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
            <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors shadow-sm shadow-blue-500/20">
              New Work Order
            </button>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {stats.map((stat, i) => (
            <motion.div 
              key={i}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className="bg-white dark:bg-gray-900 p-6 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm flex items-center justify-between"
            >
              <div>
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">{stat.label}</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">{stat.value}</p>
              </div>
              <div className={`w-12 h-12 rounded-full flex items-center justify-center ${stat.bg}`}>
                <stat.icon className={`w-6 h-6 ${stat.color}`} />
              </div>
            </motion.div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content - Work Orders */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm overflow-hidden">
              <div className="p-6 border-b border-gray-200 dark:border-gray-800 flex items-center justify-between">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Active Work Orders</h2>
                <button className="text-sm text-blue-600 dark:text-blue-400 hover:underline">View All</button>
              </div>
              <div className="divide-y divide-gray-100 dark:divide-gray-800">
                {workOrders.map((wo, i) => (
                  <motion.div 
                    key={wo.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.2 + i * 0.1 }}
                    className="p-5 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors group cursor-pointer"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex gap-4">
                        <div className={`mt-1 px-2.5 py-0.5 rounded-full border text-xs font-medium whitespace-nowrap ${getStatusColor(wo.status)}`}>
                          {wo.status}
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <h3 className="text-base font-semibold text-gray-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">{wo.title}</h3>
                            {getPriorityIcon(wo.priority)}
                          </div>
                          <div className="flex flex-wrap items-center gap-4 mt-2 text-sm text-gray-500 dark:text-gray-400">
                            <span className="flex items-center gap-1.5"><MapPin className="w-3.5 h-3.5" /> {wo.location}</span>
                            <span className="flex items-center gap-1.5"><ClipboardList className="w-3.5 h-3.5" /> {wo.id}</span>
                            <span className="flex items-center gap-1.5"><Clock className="w-3.5 h-3.5" /> {wo.time}</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="hidden sm:flex items-center gap-2">
                          <div className="w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-900/50 flex items-center justify-center text-blue-700 dark:text-blue-300 font-medium text-xs">
                            {wo.assignee.charAt(0)}
                          </div>
                          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{wo.assignee}</span>
                        </div>
                        <button className="p-1.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800 opacity-0 group-hover:opacity-100 transition-all">
                          <MoreVertical className="w-5 h-5" />
                        </button>
                      </div>
                    </div>
                  </motion.div>
                ))}
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
                      <div className="flex items-center justify-between mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
                        <div className="flex items-center gap-1.5 text-xs text-gray-500">
                          {item.type === 'Photo' ? <Camera className="w-3.5 h-3.5" /> : <Clock className="w-3.5 h-3.5" />}
                          {item.type}
                        </div>
                        <span className="text-xs text-gray-500">{item.user}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              <button className="w-full mt-6 py-2 border border-gray-200 dark:border-gray-800 rounded-lg text-sm font-medium text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
                View All Activity
              </button>
            </div>
            
            {/* Quick Actions */}
            <div className="bg-gradient-to-br from-blue-600 to-indigo-700 rounded-xl shadow-lg p-6 text-white relative overflow-hidden">
              <div className="absolute right-0 top-0 w-32 h-32 bg-white/10 rounded-bl-full -mr-8 -mt-8"></div>
              <h3 className="text-lg font-semibold mb-2 relative z-10">Need to replan?</h3>
              <p className="text-blue-100 text-sm mb-4 relative z-10">Run AI-assisted schedule optimization for delayed tasks.</p>
              <button className="bg-white text-blue-700 px-4 py-2 rounded-lg text-sm font-bold shadow-sm hover:bg-blue-50 transition-colors w-full relative z-10">
                Run Optimization
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
