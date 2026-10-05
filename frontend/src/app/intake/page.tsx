import { CSVUpload } from "@/components/intake/CSVUpload";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Intake | Civic Pulse",
  description: "Upload complaint datasets",
};

export default function IntakePage() {
  return (
    <div className="flex-1 bg-gray-50 dark:bg-gray-950 p-8">
      <CSVUpload />
    </div>
  );
}
