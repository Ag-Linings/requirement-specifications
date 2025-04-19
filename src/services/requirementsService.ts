
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

const API_URL = "http://localhost:8000/refine";

export async function refineRequirements(rawInput: string): Promise<RequirementsResponse> {
  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ 
        input: rawInput,
        user_id: "default-user" // Add a default user ID
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
export async function mockRefineRequirements(rawInput: string): Promise<RequirementsResponse> {
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

      resolve({
        requirements,
        summary: "This system aims to provide a requirements management solution with clear categorization of different requirement types."
      });
    }, 1500);
  });
}
