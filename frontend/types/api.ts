/**
 * API Types
 *
 * Type definitions for API requests and responses.
 * Based on CLAUDE.md requirements for backend integration.
 */

// Recommendation Request/Response Types
export interface RecommendationRequest {
  query?: string;
  preferences?: UserPreferences;
  location?: string;
}

export interface UserPreferences {
  budget?: string;
  interests?: string[];
  travelStyle?: string;
}

export interface RecommendationResponse {
  destinations: DestinationRecommendation[];
  packages: PackageRecommendation[];
  llm_evidence_pack?: LLMEvidencePack;
}

export interface DestinationRecommendation {
  id: string;
  name: string;
  description: string;
  category: string;
  price: string;
  rating: number;
  location: string;
  imageUrl?: string;
}

export interface PackageRecommendation {
  id: string;
  name: string;
  destinations: string[];
  totalPrice: string;
  duration: string;
  description: string;
}

// LLM Evidence Pack (for RAG validation)
export interface LLMEvidencePack {
  sources: string[];
  context: string;
  timestamp: string;
}

// Oleh-Oleh (Souvenirs) Types
export interface OlehOlehRequest {
  query?: string;
  category?: string;
  priceRange?: string;
}

export interface OlehOlehResponse {
  products: OlehOlehProduct[];
  llm_evidence_pack?: LLMEvidencePack;
}

export interface OlehOlehProduct {
  id: string;
  name: string;
  description: string;
  category: string;
  price: string;
  imageUrl?: string;
  seller?: string;
}

// LLM Validation Types
export interface LLMValidationRequest {
  message: string;
  llm_evidence_pack: LLMEvidencePack;
}

export interface LLMValidationResponse {
  isValid: boolean;
  validatedMessage: string;
  confidence: number;
  warnings?: string[];
}

// Generic API Error Response
export interface APIError {
  error: string;
  message: string;
  statusCode: number;
}
