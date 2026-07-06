import { Card } from "@/components/ui/card.tsx";

export default function ApprovalHierarchy({ stages, currentStage }) {
  const currentIdx = stages.indexOf(currentStage);

  return (
    <Card size="sm" className="p-5 mb-4">
      <h3 className="text-sm font-semibold mb-4">Approval Hierarchy</h3>
      <div className="overflow-x-auto pb-2">
        <div className="flex items-start min-w-max gap-0">
          {stages.map((stage, idx) => {
            const done = idx <= currentIdx;
            return (
              <div key={stage} className="flex items-center">
                <div className="flex flex-col items-center w-28 px-1">
                  <div
                    className={`h-3 w-3 rounded-full border-2 ${
                      done ? "bg-primary border-primary" : "bg-muted border-muted-foreground/30"
                    }`}
                  />
                  <p className={`text-xs text-center mt-2 leading-tight ${done ? "font-medium" : "text-muted-foreground"}`}>
                    {stage}
                  </p>
                </div>
                {idx < stages.length - 1 && (
                  <div className={`h-0.5 w-8 -mt-6 ${idx < currentIdx ? "bg-primary" : "bg-muted"}`} />
                )}
              </div>
            );
          })}
        </div>
      </div>
    </Card>
  );
}