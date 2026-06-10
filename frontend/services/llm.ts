/**
 * LLM Validation API Service
 *
 * Validates LLM chatbot responses to prevent hallucinations.
 * Endpoint: POST /api/llm/validate
 *
 * IMPORTANT: As per CLAUDE.md rules, NEVER let the LLM Chatbot
 * directly answer user questions without validating the output
 * through this service first.
 */
import { apiPost } from './api';
import type {
  LLMValidationRequest,
  LLMValidationResponse,
} from '@/types';

/**
 * Validate LLM chatbot response against evidence pack
 *
 * This function ensures the chatbot's answer is grounded in
 * the provided evidence and not hallucinated.
 *
 * @param message - The LLM-generated message to validate
 * @param llm_evidence_pack - Evidence from the recommendation API
 * @returns Validation result with confidence score
 */
export async function validateLLMResponse(
  message: string,
  llm_evidence_pack: LLMValidationRequest['llm_evidence_pack']
): Promise<LLMValidationResponse> {
  return apiPost<LLMValidationResponse>('/api/llm/validate', {
    message,
    llm_evidence_pack,
  });
}
