import { Metadata } from "next";
import CasesList from "@/components/cases/CasesList";

export const metadata: Metadata = {
  title: "Cases | Civic Pulse",
  description: "Infrastructure Failure Cases",
};

export default function CasesPage() {
  return (
    <div className="flex-1 bg-gray-50 dark:bg-gray-950 p-8 overflow-y-auto">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white tracking-tight mb-2">Failure Cases</h1>
        <p className="text-gray-500 mb-8">Investigate identified infrastructure failures.</p>
        
        <CasesList />
      </div>
    </div>
  );
}
