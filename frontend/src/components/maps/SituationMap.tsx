"use client";

import { useEffect } from "react";
import { MapContainer, TileLayer, Marker, Popup, CircleMarker, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { useQuery } from "@tanstack/react-query";
import { clustersApi, complaintsApi } from "@/services/api";
import { useRouter } from "next/navigation";
import { format } from "date-fns";
import { Bug } from "lucide-react";

// Fix for default marker icons in Leaflet with Webpack/Next.js
const iconUrl = 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png';
const iconRetinaUrl = 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png';
const shadowUrl = 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png';

delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconUrl,
  iconRetinaUrl,
  shadowUrl,
});

// Component to handle auto-fitting bounds based on clusters
function MapBounds({ clusters }: { clusters: any[] }) {
  const map = useMap();
  
  useEffect(() => {
    if (clusters && clusters.length > 0) {
      const validClusters = clusters.filter(c => c.centroid_lat && c.centroid_lon);
      if (validClusters.length > 0) {
        const bounds = L.latLngBounds(
          validClusters.map(c => [c.centroid_lat, c.centroid_lon])
        );
        map.fitBounds(bounds, { padding: [50, 50], maxZoom: 16 });
      }
    }
  }, [clusters, map]);

  return null;
}

export default function SituationMap() {
  const router = useRouter();
  
  // Use a default coordinate (Pune, India based on context)
  const defaultCenter: [number, number] = [18.5204, 73.8567]; 
  const defaultZoom = 12;

  const { data: clustersData, isLoading: isLoadingClusters, error: clusterError } = useQuery({
    queryKey: ['clusters'],
    queryFn: () => clustersApi.getClusters(),
  });

  return (
    <div className="absolute inset-0 w-full h-full bg-gray-900">
      <MapContainer 
        center={defaultCenter} 
        zoom={defaultZoom} 
        style={{ position: 'absolute', top: 0, bottom: 0, left: 0, right: 0, zIndex: 0 }}
      >
        <TileLayer
          attribution='Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
          url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
          maxZoom={18}
        />

        {clustersData?.clusters && <MapBounds clusters={clustersData.clusters} />}

        {clustersData?.clusters?.map((cluster) => {
          if (!cluster.centroid_lat || !cluster.centroid_lon) return null;
          
          // Calculate style based on confidence and severity
          const size = Math.max(12, Math.min(30, cluster.complaint_count * 2));
          
          return (
            <CircleMarker
              key={cluster.cluster_id}
              center={[cluster.centroid_lat, cluster.centroid_lon]}
              radius={size}
              pathOptions={{
                fillColor: cluster.confidence > 0.8 ? '#ef4444' : '#f59e0b',
                fillOpacity: 0.6,
                color: '#ffffff',
                weight: 2,
              }}
            >
              <Popup className="custom-popup">
                <div className="p-1 min-w-[220px]">
                  <div className="text-[10px] font-bold tracking-wider uppercase text-gray-500 mb-1">
                    FAILURE CLUSTER • {cluster.cluster_id.substring(0, 8)}
                  </div>
                  <h3 className="font-bold text-gray-900 text-sm mb-2 leading-tight">
                    {cluster.title}
                  </h3>
                  
                  <div className="grid grid-cols-2 gap-2 mb-3 text-sm">
                    <div className="bg-gray-50 p-2 rounded border border-gray-100">
                      <div className="text-xl font-bold text-gray-900">{cluster.complaint_count}</div>
                      <div className="text-[10px] text-gray-500 uppercase">Complaints</div>
                    </div>
                    <div className="bg-gray-50 p-2 rounded border border-gray-100">
                      <div className="text-xl font-bold text-gray-900">{(cluster.confidence * 100).toFixed(0)}%</div>
                      <div className="text-[10px] text-gray-500 uppercase">Confidence</div>
                    </div>
                  </div>

                  {cluster.cluster_rationale && (
                    <div className="text-xs text-gray-600 mb-4 line-clamp-2">
                      <span className="font-semibold block mb-1">Probable mechanism:</span>
                      {cluster.cluster_rationale}
                    </div>
                  )}

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      router.push(`/cases/${cluster.cluster_id}`);
                    }}
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold py-2 px-4 rounded transition-colors"
                  >
                    OPEN CASE
                  </button>
                </div>
              </Popup>
            </CircleMarker>
          );
        })}
      </MapContainer>

      {/* Debug Panel */}
      <div className="absolute bottom-4 left-4 z-50 max-w-sm w-full bg-gray-900/90 text-gray-100 p-4 rounded-lg shadow-xl backdrop-blur-sm border border-gray-700 max-h-64 overflow-y-auto font-mono text-xs">
        <div className="flex items-center gap-2 font-bold mb-2 text-yellow-400 border-b border-gray-700 pb-2">
          <Bug className="w-4 h-4" />
          <span>DEBUG DEV VIEW</span>
        </div>
        <div>
          <strong>Status:</strong> {isLoadingClusters ? 'Loading...' : 'Loaded'} <br />
          <strong>Error:</strong> {clusterError ? String(clusterError) : 'None'} <br />
          <strong>Total Clusters:</strong> {clustersData?.total || 0}
        </div>
        {clustersData?.clusters && clustersData.clusters.length > 0 && (
          <div className="mt-2 pt-2 border-t border-gray-700">
            <strong className="text-green-400">First Cluster Raw:</strong>
            <pre className="mt-1 whitespace-pre-wrap text-[10px] text-gray-300">
              {JSON.stringify(clustersData.clusters[0], null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}
