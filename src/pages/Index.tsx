import { useState } from "react";
import RequirementsInput from "@/components/RequirementsInput";
import RequirementsList from "@/components/RequirementsList";
import { mockRefineRequirements, RequirementsResponse } from "@/services/requirementsService";

const Index = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [requirementsData, setRequirementsData] = useState<RequirementsResponse>({
    requirements: [],
  });

  const handleSubmitRequirements = async (input: string) => {
    setIsLoading(true);
    try {
      // In production, you would use the real API:
      // const data = await refineRequirements(input);
      const data = await mockRefineRequirements(input);
      setRequirementsData(data);
    } catch (error) {
      console.error("Error processing requirements:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <header className="w-full py-6 border-b bg-[#a98467]">
        <div className="container px-4 mx-auto">
          <div className="flex flex-col sm:flex-row items-center justify-between">
            <div className="flex items-center mb-4 sm:mb-0">
              <div className="w-10 h-10 rounded-lg bg-gradient-req mr-3 flex items-center justify-center">
                <span className="text-white font-bold">RM</span>
              </div>
              <h1 className="text-2xl font-bold text-white">Requirements Manager</h1>
            </div>
            <div className="text-sm text-muted-foreground text-white">
              Software Engineering Lab
            </div>
          </div>
        </div>
      </header>

      <main className="flex-grow container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 h-full">
          <div className="h-full">
            <RequirementsInput 
              onSubmit={handleSubmitRequirements} 
              isLoading={isLoading} 
            />
          </div>
          <div className="h-full">
            <RequirementsList 
              requirements={requirementsData.requirements} 
              summary={requirementsData.summary}
            />
          </div>
        </div>
      </main>

      <footer className="w-full py-4 border-t mt-auto">
        <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
          Requirements Manager · Virtual Software Engineering Lab
        </div>
      </footer>
    </div>
  );
};

export default Index;
