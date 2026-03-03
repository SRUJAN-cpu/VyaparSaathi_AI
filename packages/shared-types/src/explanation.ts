/**
 * AI explanation interfaces for VyaparSaathi
 * Handles natural language explanations using Amazon Bedrock
 */

import { ForecastResult } from './forecasting';
import { RiskAssessment } from './risk';

/**
 * Request for AI-generated explanation
 */
export interface ExplanationRequest {
  /** User identifier */
  userId: string;
  /** Context for explanation */
  context: 'forecast' | 'risk' | 'recommendation' | 'general';
  /** Data to explain (forecast or risk assessment) */
  data: ForecastResult | RiskAssessment | any;
  /** Optional user query for specific questions */
  userQuery?: string;
  /** Explanation complexity level */
  complexity: 'simple' | 'detailed' | 'technical';
  /** User's business context */
  businessContext?: {
    businessType: string;
    experience: 'beginner' | 'intermediate' | 'advanced';
    preferredLanguage: string;
  };
}

/**
 * AI-generated explanation response
 */
export interface ExplanationResponse {
  /** Main explanation text */
  explanation: string;
  /** Key insights highlighted */
  keyInsights: string[];
  /** Assumptions made in analysis */
  assumptions: string[];
  /** Limitations of the analysis */
  limitations: string[];
  /** Confidence level description */
  confidence: string;
  /** Recommended next steps */
  nextSteps: string[];
  /** Related questions user might ask */
  relatedQuestions: string[];
  /** Explanation metadata */
  metadata: {
    /** AI model used */
    model: string;
    /** Generation timestamp */
    generatedAt: string;
    /** Token usage for cost tracking */
    tokenUsage: number;
    /** Response quality score */
    qualityScore: number;
  };
}

/**
 * Conversational AI context for multi-turn dialogues
 */
export interface ConversationContext {
  /** Conversation identifier */
  conversationId: string;
  /** User identifier */
  userId: string;
  /** Conversation history */
  history: ConversationTurn[];
  /** Current user context */
  userContext: {
    /** Current forecasts */
    activeForecast?: ForecastResult[];
    /** Current risk assessments */
    activeRisks?: RiskAssessment[];
    /** User preferences */
    preferences: {
      explanationStyle: 'simple' | 'detailed';
      focusAreas: string[];
    };
  };
  /** Conversation metadata */
  metadata: {
    /** Conversation start time */
    startedAt: string;
    /** Last activity time */
    lastActivity: string;
    /** Total turns in conversation */
    turnCount: number;
  };
}

/**
 * Individual turn in conversation
 */
export interface ConversationTurn {
  /** Turn identifier */
  turnId: string;
  /** Turn type */
  type: 'user_query' | 'ai_response';
  /** Turn content */
  content: string;
  /** Turn timestamp */
  timestamp: string;
  /** Associated data context */
  dataContext?: {
    forecastData?: ForecastResult;
    riskData?: RiskAssessment;
    queryType?: string;
  };
}

/**
 * Explanation template for consistent responses
 */
export interface ExplanationTemplate {
  /** Template identifier */
  templateId: string;
  /** Template name */
  name: string;
  /** Context this template applies to */
  context: 'forecast' | 'risk' | 'recommendation';
  /** Template structure */
  structure: {
    /** Introduction pattern */
    introduction: string;
    /** Main content pattern */
    mainContent: string;
    /** Conclusion pattern */
    conclusion: string;
    /** Required data fields */
    requiredFields: string[];
  };
  /** Template complexity level */
  complexity: 'simple' | 'detailed' | 'technical';
}