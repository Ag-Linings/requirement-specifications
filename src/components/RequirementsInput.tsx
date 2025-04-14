
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { RefreshCw, Key } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";

interface RequirementsInputProps {
  onSubmit: (input: string, apiKey?: string) => void;
  isLoading: boolean;
}

const RequirementsInput = ({ onSubmit, isLoading }: RequirementsInputProps) => {
  const [input, setInput] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [showApiKey, setShowApiKey] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) {
      onSubmit(input, apiKey);
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
        
        <div className="flex flex-col md:flex-row gap-4 justify-end items-center mb-4">
          <Popover open={showApiKey} onOpenChange={setShowApiKey}>
            <PopoverTrigger asChild>
              <Button 
                type="button" 
                variant="outline" 
                className="w-full md:w-auto flex items-center gap-2"
                onClick={() => setShowApiKey(!showApiKey)}
              >
                <Key className="h-4 w-4" />
                {apiKey ? "API Key Added" : "Add API Key"}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-80">
              <div className="space-y-4">
                <h4 className="font-medium">Perplexity API Key</h4>
                <p className="text-sm text-muted-foreground">
                  Add your Perplexity AI API key for better results. If not provided, we'll use fallback methods.
                </p>
                <Input
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder="Enter your Perplexity API key"
                  className="w-full"
                />
                <div className="flex justify-end">
                  <Button 
                    type="button" 
                    size="sm"
                    onClick={() => setShowApiKey(false)}
                  >
                    Save
                  </Button>
                </div>
              </div>
            </PopoverContent>
          </Popover>
          
          <Button 
            type="submit" 
            className="w-full md:w-auto bg-[#a98467] text-white hover:bg-[#8a724f] disabled:bg-[#d1b493]" 
            disabled={isLoading || !input.trim()}
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
