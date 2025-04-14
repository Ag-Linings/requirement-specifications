
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

export async function refineRequirements(rawInput: string): Promise<RequirementsResponse> {
  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ input: rawInput }),
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

      // Create "refined" requirements by splitting the input into lines
      const lines = rawInput
        .split('\n')
        .map(line => line.trim())
        .filter(line => line.length > 0);

      const requirements: Requirement[] = lines.map((line, index) => {
        // Try to determine category based on keywords
        let category: RequirementCategory = "performance";
        
        if (line.includes("authenticate") || line.includes("encrypt") || line.includes("security")) {
          category = "security";
        } else if (line.includes("display") || line.includes("render") || line.includes("UI")) {
          category = "interface";
        } else if (line.includes("store") || line.includes("compress")) {
          category = "non-functional";
        } else if (line.includes("validate") || line.includes("search")) {
          category = "functional";
        } else if (line.includes("instances") || line.includes("limit")) {
          category = "constraints";
        } else if (line.includes("business") || line.includes("organization")) {
          category = "business";
        }
        
        return {
          id: `REQ-${index + 1}`,
          description: line,
          category: category,
        };
      });

      resolve({
        requirements,
      });
    }, 1500);
  });
}
