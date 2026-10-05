import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Execution Center | Civic Pulse",
  description: "Monitor active work orders and field execution.",
};

export default function ExecutionPage() {
  return (
    <div className="flex-1 bg-gray-50 dark:bg-gray-950 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white tracking-tight mb-2">Execution Center</h1>
        <p className="text-gray-500 mb-8">Monitor active work orders, replanning events, and field evidence verification.</p>
        
        <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm p-6">
          <p className="text-center text-gray-500 my-12">Execution dashboard coming soon...</p>
        </div>
      </div>
    </div>
  );
}
