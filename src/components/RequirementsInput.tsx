
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { RefreshCw } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";

interface RequirementsInputProps {
  onSubmit: (input: string) => void;
  isLoading: boolean;
}

interface RequirementTemplate {
  id: string;
  text: string;
  blanks: string[];
  values: string[];
  isSelected: boolean;
}

const RequirementsInput = ({ onSubmit, isLoading }: RequirementsInputProps) => {
  const [activeTab, setActiveTab] = useState("ui");
  
  const [uiRequirements, setUiRequirements] = useState<RequirementTemplate[]>([
    { id: "ui-1", text: "The application should load the initial page within {0} seconds.", blanks: ["___"], values: ["2"], isSelected: true },
    { id: "ui-2", text: "The application should respond to user input (e.g., button clicks) within {0} milliseconds.", blanks: ["___"], values: [""], isSelected: false },
    { id: "ui-3", text: "The application should render a list of {0} items without any performance lag.", blanks: ["___"], values: [""], isSelected: false },
    { id: "ui-4", text: "The application should update the UI after a data change within {0} seconds.", blanks: ["___"], values: [""], isSelected: false },
    { id: "ui-5", text: "The application should display a complex form with {0} fields without any noticeable delay.", blanks: ["___"], values: [""], isSelected: false },
  ]);
  
  const [dataRetrievalRequirements, setDataRetrievalRequirements] = useState<RequirementTemplate[]>([
    { id: "dr-1", text: "Retrieve a single record from the database in under {0} milliseconds.", blanks: ["___"], values: ["100"], isSelected: true },
    { id: "dr-2", text: "Fetch a list of {0} records from the database within {1} seconds.", blanks: ["___", "___"], values: ["", ""], isSelected: false },
    { id: "dr-3", text: "The application should handle a search query and display results within {0} seconds.", blanks: ["___"], values: [""], isSelected: false },
    { id: "dr-4", text: "The application should retrieve data from an external API within {0} seconds.", blanks: ["___"], values: [""], isSelected: false },
    { id: "dr-5", text: "The application should cache frequently accessed data for a duration of {0} seconds.", blanks: ["___"], values: [""], isSelected: false },
  ]);
  
  const [dataProcessingRequirements, setDataProcessingRequirements] = useState<RequirementTemplate[]>([
    { id: "dp-1", text: "Process {0} records per second.", blanks: ["___"], values: [""], isSelected: false },
    { id: "dp-2", text: "Perform a complex calculation on {0} data points within {1} milliseconds.", blanks: ["___", "___"], values: ["", ""], isSelected: false },
    { id: "dp-3", text: "The application should encrypt data using {0} encryption algorithm.", blanks: ["___"], values: [""], isSelected: false },
    { id: "dp-4", text: "The application should compress {0} MB of data within {1} seconds.", blanks: ["___", "___"], values: ["", ""], isSelected: false },
    { id: "dp-5", text: "The application should validate {0} user inputs per second.", blanks: ["___"], values: [""], isSelected: false },
  ]);
  
  const [securityRequirements, setSecurityRequirements] = useState<RequirementTemplate[]>([
    { id: "sec-1", text: "The application should authenticate users within {0} seconds.", blanks: ["___"], values: [""], isSelected: false },
    { id: "sec-2", text: "The application should encrypt sensitive data using {0} encryption method.", blanks: ["___"], values: [""], isSelected: false },
    { id: "sec-3", text: "The application should prevent brute-force attacks by implementing a {0} mechanism.", blanks: ["___"], values: [""], isSelected: false },
    { id: "sec-4", text: "The application should log security events with a latency of {0} seconds.", blanks: ["___"], values: [""], isSelected: false },
    { id: "sec-5", text: "The application should implement {0} factor authentication.", blanks: ["___"], values: [""], isSelected: false },
  ]);
  
  const [scalabilityRequirements, setScalabilityRequirements] = useState<RequirementTemplate[]>([
    { id: "scal-1", text: "The application should handle {0} concurrent users without performance degradation.", blanks: ["___"], values: [""], isSelected: false },
    { id: "scal-2", text: "The application should scale to handle {0} requests per second.", blanks: ["___"], values: [""], isSelected: false },
    { id: "scal-3", text: "The application should be able to store {0} TB of data.", blanks: ["___"], values: [""], isSelected: false },
    { id: "scal-4", text: "The application should be able to deploy {0} instances of the application.", blanks: ["___"], values: [""], isSelected: false },
    { id: "scal-5", text: "The application should be able to handle a peak load of {0} requests per minute.", blanks: ["___"], values: [""], isSelected: false },
  ]);
  
  const handleInputChange = (category: string, id: string, index: number, value: string) => {
    if (category === "ui") {
      setUiRequirements(prevReqs => prevReqs.map(req => 
        req.id === id ? { ...req, values: req.values.map((val, i) => i === index ? value : val) } : req
      ));
    } else if (category === "data-retrieval") {
      setDataRetrievalRequirements(prevReqs => prevReqs.map(req => 
        req.id === id ? { ...req, values: req.values.map((val, i) => i === index ? value : val) } : req
      ));
    } else if (category === "data-processing") {
      setDataProcessingRequirements(prevReqs => prevReqs.map(req => 
        req.id === id ? { ...req, values: req.values.map((val, i) => i === index ? value : val) } : req
      ));
    } else if (category === "security") {
      setSecurityRequirements(prevReqs => prevReqs.map(req => 
        req.id === id ? { ...req, values: req.values.map((val, i) => i === index ? value : val) } : req
      ));
    } else if (category === "scalability") {
      setScalabilityRequirements(prevReqs => prevReqs.map(req => 
        req.id === id ? { ...req, values: req.values.map((val, i) => i === index ? value : val) } : req
      ));
    }
  };
  
  const handleCheckboxChange = (category: string, id: string, checked: boolean) => {
    if (category === "ui") {
      setUiRequirements(prevReqs => prevReqs.map(req => 
        req.id === id ? { ...req, isSelected: checked } : req
      ));
    } else if (category === "data-retrieval") {
      setDataRetrievalRequirements(prevReqs => prevReqs.map(req => 
        req.id === id ? { ...req, isSelected: checked } : req
      ));
    } else if (category === "data-processing") {
      setDataProcessingRequirements(prevReqs => prevReqs.map(req => 
        req.id === id ? { ...req, isSelected: checked } : req
      ));
    } else if (category === "security") {
      setSecurityRequirements(prevReqs => prevReqs.map(req => 
        req.id === id ? { ...req, isSelected: checked } : req
      ));
    } else if (category === "scalability") {
      setScalabilityRequirements(prevReqs => prevReqs.map(req => 
        req.id === id ? { ...req, isSelected: checked } : req
      ));
    }
  };
  
  const formatRequirement = (req: RequirementTemplate): string => {
    let result = req.text;
    req.values.forEach((value, index) => {
      result = result.replace(`{${index}}`, value);
    });
    return result;
  };
  
  const generateRequirementsText = (): string => {
    const allRequirements = [
      ...uiRequirements,
      ...dataRetrievalRequirements,
      ...dataProcessingRequirements,
      ...securityRequirements,
      ...scalabilityRequirements
    ].filter(req => req.isSelected);
    
    if (allRequirements.length === 0) {
      return "";
    }
    
    return allRequirements.map(req => formatRequirement(req)).join('\n');
  };
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const requirementsText = generateRequirementsText();
    if (requirementsText.trim()) {
      onSubmit(requirementsText);
    }
  };
  
  const renderRequirementInputs = (
    requirements: RequirementTemplate[],
    category: string,
    setRequirements: React.Dispatch<React.SetStateAction<RequirementTemplate[]>>
  ) => {
    return (
      <div className="space-y-4">
        {requirements.map((req) => (
          <div key={req.id} className="flex items-start space-x-2 p-2 border rounded-md">
            <Checkbox 
              id={req.id} 
              checked={req.isSelected}
              onCheckedChange={(checked) => handleCheckboxChange(category, req.id, checked as boolean)}
              className="mt-1"
            />
            <div className="flex-grow">
              <Label htmlFor={req.id} className="text-sm">
                {req.text.split(/\{[0-9]+\}/).map((part, index, array) => {
                  if (index === array.length - 1) {
                    return <span key={index}>{part}</span>;
                  }
                  return (
                    <React.Fragment key={index}>
                      {part}
                      <Input
                        type="text"
                        value={req.values[index] || ""}
                        onChange={(e) => handleInputChange(category, req.id, index, e.target.value)}
                        className="inline-block w-16 mx-1 p-1 h-7 text-center"
                        disabled={!req.isSelected}
                      />
                    </React.Fragment>
                  );
                })}
              </Label>
            </div>
          </div>
        ))}
      </div>
    );
  };
  
  return (
    <Card className="p-6 h-full flex flex-col">
      <h2 className="text-xl font-semibold mb-4">System Requirements</h2>
      <p className="text-sm text-muted-foreground mb-4">
        Select and complete the requirements that apply to your system.
      </p>
      
      <form onSubmit={handleSubmit} className="flex flex-col flex-grow">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-grow flex flex-col">
          <TabsList className="grid grid-cols-5 mb-4">
            <TabsTrigger value="ui">UI Performance</TabsTrigger>
            <TabsTrigger value="data-retrieval">Data Retrieval</TabsTrigger>
            <TabsTrigger value="data-processing">Data Processing</TabsTrigger>
            <TabsTrigger value="security">Security</TabsTrigger>
            <TabsTrigger value="scalability">Scalability</TabsTrigger>
          </TabsList>
          
          <div className="flex-grow overflow-auto mb-4">
            <TabsContent value="ui" className="mt-0 h-full">
              {renderRequirementInputs(uiRequirements, "ui", setUiRequirements)}
            </TabsContent>
            
            <TabsContent value="data-retrieval" className="mt-0 h-full">
              {renderRequirementInputs(dataRetrievalRequirements, "data-retrieval", setDataRetrievalRequirements)}
            </TabsContent>
            
            <TabsContent value="data-processing" className="mt-0 h-full">
              {renderRequirementInputs(dataProcessingRequirements, "data-processing", setDataProcessingRequirements)}
            </TabsContent>
            
            <TabsContent value="security" className="mt-0 h-full">
              {renderRequirementInputs(securityRequirements, "security", setSecurityRequirements)}
            </TabsContent>
            
            <TabsContent value="scalability" className="mt-0 h-full">
              {renderRequirementInputs(scalabilityRequirements, "scalability", setScalabilityRequirements)}
            </TabsContent>
          </div>
        </Tabs>
        
        <div className="flex justify-end">
          <Button 
            type="submit" 
            className="w-full sm:w-auto bg-[#a98467] text-white hover:bg-[#8a724f] disabled:bg-[#d1b493]" 
            disabled={isLoading || generateRequirementsText().trim() === ""}
          >
            {isLoading ? (
              <>
                <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                Adding requirements...
              </>
            ) : (
              "Refine Requirements"
            )}
          </Button>
        </div>
      </form>
    </Card>
  );
};

export default RequirementsInput;
