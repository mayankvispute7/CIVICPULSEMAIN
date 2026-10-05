import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Memory | Civic Pulse",
  description: "Infrastructure Memory & Learnings",
};

export default function MemoryPage() {
  return (
    <div className="flex-1 bg-gray-50 dark:bg-gray-950 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white tracking-tight mb-2">Infrastructure Memory</h1>
        <p className="text-gray-500 mb-8">Long-term tracking of sites, outcomes, and learned patterns.</p>
        
        <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm p-6 text-center text-gray-500 min-h-[400px] flex items-center justify-center">
          Site memory search and outcome records...
        </div>
      </div>
    </div>
  );
}
