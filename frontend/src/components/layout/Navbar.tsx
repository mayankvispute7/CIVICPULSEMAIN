import Link from 'next/link';
import { Activity } from 'lucide-react';

export function Navbar() {
  const stages = [
    { name: "INGEST", path: "/intake", activePaths: ["/intake"] },
    { name: "UNDERSTAND", path: "/situation", activePaths: ["/situation"] },
    { name: "CONNECT", path: "/cases", activePaths: ["/cases"] }, // Actually, cases page might be the hub
    { name: "INVESTIGATE", path: "/cases", activePaths: ["/cases"] },
    { name: "DECIDE", path: "/cases", activePaths: ["/cases"] },
    { name: "ACT", path: "/execution", activePaths: ["/execution"] },
    { name: "VERIFY", path: "/execution", activePaths: ["/execution"] },
    { name: "LEARN", path: "/memory", activePaths: ["/memory"] },
  ];

  return (
    <header className="border-b bg-[#0a0f1c] border-slate-800 sticky top-0 z-50 shadow-md">
      <div className="px-4 sm:px-6 lg:px-8 w-full">
        <div className="flex justify-between items-center h-14">
          <div className="flex items-center gap-8">
            <Link href="/" className="flex-shrink-0 flex items-center gap-2">
              <Activity className="h-5 w-5 text-blue-500" />
              <span className="font-bold text-sm tracking-widest text-slate-100">
                CIVIC PULSE
              </span>
            </Link>
            
            <nav className="hidden lg:flex items-center space-x-1">
              {stages.map((stage, idx) => (
                <div key={idx} className="flex items-center">
                  <Link
                    href={stage.path}
                    className="px-3 py-1 rounded text-[10px] font-bold tracking-widest text-slate-400 hover:text-slate-100 hover:bg-slate-800 transition-colors"
                  >
                    {stage.name}
                  </Link>
                  {idx < stages.length - 1 && (
                    <span className="text-slate-700 text-xs mx-1">›</span>
                  )}
                </div>
              ))}
            </nav>
          </div>
          
          <div className="flex items-center">
            <span className="px-2 py-0.5 rounded text-[9px] font-bold uppercase tracking-widest bg-blue-900/30 text-blue-400 border border-blue-800/50">
              MUNICIPAL INTELLIGENCE
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}
