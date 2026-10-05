import { Metadata } from "next";
import { CaseWorkspace } from "@/components/cases/CaseWorkspace";

export const metadata: Metadata = {
  title: "Failure Case | Civic Pulse",
  description: "Infrastructure failure investigation",
};

export default async function CasePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <CaseWorkspace caseId={id} />;
}
