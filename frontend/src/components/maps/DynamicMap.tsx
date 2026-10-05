"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { Loader2 } from "lucide-react";

// Dynamically import the actual map component to avoid SSR issues with Leaflet
const Map = dynamic(
  () => import("./SituationMap"),
  { 
    ssr: false,
    loading: () => (
      <div className="w-full h-full flex items-center justify-center bg-gray-100 dark:bg-gray-800 rounded-xl">
        <Loader2 className="h-8 w-8 text-blue-500 animate-spin" />
        <span className="ml-2 text-sm text-gray-500">Loading Map Intelligence...</span>
      </div>
    )
  }
);

import { ErrorBoundary } from "../common/ErrorBoundary";

export function DynamicMap() {
  return (
    <div className="w-full h-full min-h-[600px] relative z-0">
      <ErrorBoundary>
        <Map />
      </ErrorBoundary>
    </div>
  );
}
