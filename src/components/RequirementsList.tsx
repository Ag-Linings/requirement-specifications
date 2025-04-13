
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Requirement, RequirementCategory } from "@/services/requirementsService";

interface RequirementsListProps {
  requirements: Requirement[];
  summary?: string;
}

const RequirementsList = ({ requirements, summary }: RequirementsListProps) => {
  const getCategoryColor = (category: RequirementCategory): string => {
    const colors: Record<RequirementCategory, string> = {
      functional: "bg-req-functional",
      "non-functional": "bg-req-non-functional",
      constraints: "bg-req-constraints",
      interface: "bg-req-interface",
      business: "bg-req-business",
      security: "bg-req-security",
      performance: "bg-req-performance",
      unknown: "bg-gray-500",
    };
    return colors[category];
  };

  const getCategoryLabel = (category: RequirementCategory): string => {
    const labels: Record<RequirementCategory, string> = {
      functional: "Functional",
      "non-functional": "Non-Functional",
      constraints: "Constraint",
      interface: "Interface",
      business: "Business",
      security: "Security",
      performance: "Performance",
      unknown: "Uncategorized",
    };
    return labels[category];
  };

  return (
    <Card className="p-6 h-full flex flex-col">
      <h2 className="text-xl font-semibold mb-4">Refined Requirements</h2>
      
      {summary && (
        <div className="mb-6 p-4 bg-accent rounded-md">
          <h3 className="font-medium mb-2">Summary</h3>
          <p className="text-sm text-muted-foreground">{summary}</p>
        </div>
      )}
      
      {requirements.length === 0 ? (
        <div className="flex-grow flex items-center justify-center">
          <p className="text-muted-foreground text-center">
            Refined requirements will appear here after processing.
          </p>
        </div>
      ) : (
        <div className="space-y-4 overflow-y-auto flex-grow">
          {requirements.map((req) => (
            <div
              key={req.id}
              className={`requirement-card p-4 bg-card rounded-md shadow-sm 
                          requirement-${req.category}`}
            >
              <div className="flex justify-between items-start mb-2">
                <Badge variant="outline" className="text-xs font-mono">
                  {req.id}
                </Badge>
                <Badge className={`${getCategoryColor(req.category)} text-white`}>
                  {getCategoryLabel(req.category)}
                </Badge>
              </div>
              <p className="text-sm">{req.description}</p>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
};

export default RequirementsList;
