"use client";

import React, { Component, ErrorInfo, ReactNode } from "react";
import { Map as MapIcon, AlertTriangle } from "lucide-react";

interface Props {
  children?: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false
  };

  public static getDerivedStateFromError(_: Error): State {
    return { hasError: true };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Map Error caught by ErrorBoundary:", error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }
      return (
        <div className="w-full h-full flex flex-col items-center justify-center bg-gray-900/50 rounded-xl border border-red-900/30 p-6 text-center">
          <div className="bg-red-900/20 p-4 rounded-full mb-4">
            <AlertTriangle className="h-8 w-8 text-red-500" />
          </div>
          <h3 className="text-lg font-bold text-gray-200 mb-2">Live Map Unavailable</h3>
          <p className="text-sm text-gray-400 max-w-sm">
            The infrastructure map layer failed to load. The application is using a fallback evidence snapshot.
          </p>
        </div>
      );
    }

    return this.props.children;
  }
}
