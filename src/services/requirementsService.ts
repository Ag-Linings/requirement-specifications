
import { toast } from "sonner";

export type RequirementCategory = 
  | "functional" 
  | "non-functional" 
  | "constraints" 
  | "interface" 
  | "business"
  | "security"
  | "performance"
  | "unknown";

export interface Requirement {
  id: string;
  description: string;
  category: RequirementCategory;
}

export interface RequirementsResponse {
  requirements: Requirement[];
  summary?: string;
}

const API_URL = "/api/refine";

export async function refineRequirements(rawInput: string, apiKey?: string): Promise<RequirementsResponse> {
  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ 
        input: rawInput,
        api_key: apiKey 
      }),
    });

    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    toast.error("Failed to process requirements. Please try again.");
    console.error("Requirements API error:", error);
    throw error;
  }
}

// For development and testing without a backend
export async function mockRefineRequirements(rawInput: string, apiKey?: string): Promise<RequirementsResponse> {
  // If we have an API key, try to use the real API first
  if (apiKey && apiKey.trim()) {
    try {
      return await refineRequirements(rawInput, apiKey);
    } catch (error) {
      console.error("API failed, falling back to mock:", error);
      // Fall back to mock if the API fails
    }
  }

  return new Promise((resolve) => {
    // Simulate API call delay
    setTimeout(() => {
      const categories: RequirementCategory[] = [
        "functional", 
        "non-functional", 
        "constraints", 
        "interface", 
        "business",
        "security",
        "performance"
      ];

      // Create "refined" requirements by splitting the input into sentences
      const sentences = rawInput
        .split(/[.!?]/)
        .map(s => s.trim())
        .filter(s => s.length > 10);

      const requirements: Requirement[] = sentences.map((sentence, index) => ({
        id: `REQ-${index + 1}`,
        description: sentence,
        category: categories[Math.floor(Math.random() * categories.length)],
      }));

      // Try to extract a better summary by looking for key entities
      const entityPattern = /\b[A-Z][a-z]+s?\b/g;
      const potentialEntities = rawInput.match(entityPattern) || [];
      const entities = potentialEntities
        .filter(e => !["The", "A", "An", "This", "That", "These", "Those", "It"].includes(e))
        .slice(0, 5);

      let summary = "This system aims to provide a requirements management solution with clear categorization of different requirement types.";
      
      if (entities.length > 0) {
        summary = `A system for managing ${entities.join(", ")}.`;
      }

      resolve({
        requirements,
        summary
      });
    }, 1500);
  });
}
