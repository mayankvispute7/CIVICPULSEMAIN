import { Metadata } from "next";
import { DynamicMap } from "@/components/maps/DynamicMap";
import { SituationHeader } from "@/components/maps/SituationHeader";
import { ClusterList } from "@/components/situation/ClusterList";
import { CityMetrics } from "@/components/situation/CityMetrics";

export const metadata: Metadata = {
  title: "Situation | Civic Pulse",
  description: "City-wide infrastructure failure map",
};

export default function SituationPage() {
  return (
    <div className="flex-1 flex flex-col h-[calc(100vh-64px)] overflow-hidden bg-[#0a0f1c]">
      <SituationHeader />
      <div className="flex-1 flex flex-row overflow-hidden">
        {/* Center Panel: Satellite Map (takes up 75% or flex-1) */}
        <div className="flex-1 h-full relative border-r border-gray-800">
          <DynamicMap />
        </div>
        
        {/* Right Panel: Active Failure Clusters (takes up 25%) */}
        <div className="w-[380px] h-full z-10 shadow-xl bg-[#0a0f1c] flex flex-col">
          <ClusterList />
        </div>
      </div>
    </div>
  );
}
