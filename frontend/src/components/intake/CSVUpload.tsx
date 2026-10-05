"use client";

import { useState, useRef } from "react";
import { UploadCloud, CheckCircle, AlertCircle, Loader2 } from "lucide-react";
import { complaintsApi, clustersApi } from "@/services/api";
import { ImportSummary } from "@/types/api";

export function CSVUpload() {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [result, setResult] = useState<ImportSummary | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [clusterResult, setClusterResult] = useState<any>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragging(true);
    } else if (e.type === "dragleave") {
      setIsDragging(false);
    }
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      await handleUpload(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      await handleUpload(e.target.files[0]);
    }
  };

  const handleUpload = async (file: File) => {
    if (!file.name.endsWith('.csv')) {
      setError("Please upload a valid CSV file.");
      return;
    }
    
    setIsUploading(true);
    setError(null);
    setResult(null);
    setClusterResult(null);
    
    try {
      // 1. Upload CSV
      const summary = await complaintsApi.uploadCsv(file);
      setResult(summary);
      
      // 2. Trigger Clustering
      const clustering = await clustersApi.runClustering();
      setClusterResult(clustering);
      
    } catch (err: any) {
      setError(err.message || "Failed to process dataset");
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto mt-8">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white tracking-tight">Complaint Intake</h2>
        <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">Upload complaint dataset (CSV) to begin infrastructure analysis.</p>
      </div>

      {!result && !isUploading && (
        <div
          className={`relative border-2 border-dashed rounded-xl p-12 text-center transition-all cursor-pointer ${
            isDragging
              ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
              : "border-gray-300 dark:border-gray-700 hover:border-blue-400 hover:bg-gray-50 dark:hover:bg-gray-800/50"
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept=".csv"
            className="hidden"
          />
          <UploadCloud className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-4 text-sm font-semibold text-gray-900 dark:text-white">Drop CSV here</h3>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">or click to browse</p>
          <div className="mt-6 flex justify-center text-xs text-gray-500 dark:text-gray-500">
            Supported: CSV
          </div>
        </div>
      )}

      {isUploading && (
        <div className="border border-gray-200 dark:border-gray-800 rounded-xl p-12 text-center bg-white dark:bg-gray-900 shadow-sm">
          <Loader2 className="mx-auto h-8 w-8 text-blue-600 animate-spin" />
          <h3 className="mt-4 text-sm font-bold tracking-widest text-gray-900 dark:text-white uppercase">Processing Dataset</h3>
          <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">Analyzing spatial clusters and preparing infrastructure mapping...</p>
        </div>
      )}

      {error && (
        <div className="mt-4 p-4 bg-red-50 dark:bg-red-900/20 rounded-lg flex items-start gap-3 border border-red-200 dark:border-red-800">
          <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400 mt-0.5 flex-shrink-0" />
          <div>
            <h4 className="text-sm font-medium text-red-800 dark:text-red-300">Upload failed</h4>
            <p className="text-sm text-red-700 dark:text-red-400 mt-1">{error}</p>
            <button 
              onClick={() => setError(null)}
              className="mt-3 text-sm font-medium text-red-600 dark:text-red-400 hover:underline"
            >
              Try again
            </button>
          </div>
        </div>
      )}

      {result && clusterResult && (
        <div className="border border-gray-200 dark:border-gray-800 rounded-xl p-8 bg-white dark:bg-gray-900 shadow-sm">
          <div className="flex items-center justify-center gap-3 text-green-600 dark:text-green-500 mb-2">
            <CheckCircle className="h-6 w-6" />
            <h3 className="text-lg font-bold uppercase tracking-wider">Dataset Imported</h3>
          </div>
          
          <div className="text-center mb-8">
            <div className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300">
              SYNTHETIC DATA
            </div>
          </div>
          
          <div className="max-w-md mx-auto">
            <div className="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-6 mb-6">
              <div className="text-center mb-4">
                <span className="text-3xl font-bold text-gray-900 dark:text-white">{result.total_rows}</span>
                <span className="ml-2 text-sm text-gray-600 dark:text-gray-400">complaints analyzed</span>
              </div>
              
              <div className="flex justify-center gap-12 text-center">
                <div>
                  <div className="text-2xl font-bold text-green-600 dark:text-green-500">{result.accepted_rows || 0}</div>
                  <div className="text-xs uppercase tracking-wider text-gray-500">Accepted</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-yellow-600 dark:text-yellow-500">{result.duplicate_rows || 0}</div>
                  <div className="text-xs uppercase tracking-wider text-gray-500">Duplicates</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-red-600 dark:text-red-500">{result.rejected_rows || 0}</div>
                  <div className="text-xs uppercase tracking-wider text-gray-500">Rejected</div>
                </div>
              </div>
              
              <div className="text-center mt-6 text-xs text-gray-500 dark:text-gray-400">
                Synthetic demonstration dataset<br/>Imported successfully
              </div>
            </div>

            <div className="mb-8">
              <h4 className="text-sm font-bold text-gray-900 dark:text-white mb-4 border-b border-gray-200 dark:border-gray-700 pb-2">
                Civic Pulse found:
              </h4>
              <ul className="space-y-3">
                <li className="flex items-start">
                  <span className="text-blue-600 dark:text-blue-400 mr-2 font-bold">•</span>
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    <strong className="text-gray-900 dark:text-white">{clusterResult.total_clusters}</strong> potential failure clusters
                  </span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-600 dark:text-blue-400 mr-2 font-bold">•</span>
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    <strong className="text-gray-900 dark:text-white">{clusterResult.total_complaints - clusterResult.unclustered_complaints}</strong> complaints appear related to recurring infrastructure conditions
                  </span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-600 dark:text-blue-400 mr-2 font-bold">•</span>
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    <strong className="text-gray-900 dark:text-white">{clusterResult.clusters.filter((c: any) => c.confidence > 0.8).length || clusterResult.total_clusters}</strong> clusters require investigation
                  </span>
                </li>
              </ul>
            </div>
            
            <a 
              href="/situation"
              className="block w-full text-center px-4 py-3 text-sm font-bold text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors shadow-sm"
            >
              View Infrastructure Situation
            </a>
            
            <button 
              onClick={() => {
                setResult(null);
                setClusterResult(null);
              }}
              className="mt-4 block w-full text-center px-4 py-2 text-xs font-medium text-gray-500 hover:text-gray-900 dark:hover:text-white transition-colors"
            >
              Upload a different dataset
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
