
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { RefreshCw } from "lucide-react";

interface RequirementsInputProps {
  onSubmit: (input: string) => void;
  isLoading: boolean;
}

const RequirementsInput = ({ onSubmit, isLoading }: RequirementsInputProps) => {
  const [input, setInput] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) {
      onSubmit(input);
    }
  };

  return (
    <Card className="p-6 h-full flex flex-col">
      <h2 className="text-xl font-semibold mb-4">System Requirements</h2>
      <p className="text-sm text-muted-foreground mb-4">
        Describe your system requirements in natural language. Our AI will help structure and categorize them.
      </p>
      
      <form onSubmit={handleSubmit} className="flex flex-col flex-grow">
        <Textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="e.g., The system should allow users to register with email and password. It must respond within 2 seconds and handle at least 1000 concurrent users. All data must be encrypted at rest."
          className="flex-grow min-h-[200px] mb-4 resize-none"
        />
        
        <div className="flex justify-end">
          <Button 
            type="submit" 
            className="w-full sm:w-auto bg-[#a98467] text-white hover:bg-[#8a724f] disabled:bg-[#d1b493]" 

            disabled={isLoading || !input.trim()}
          >
            {isLoading ? (
              <>
                <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                Processing...
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
