/**
 * API-specific types and interfaces for VyaparSaathi
 * Defines request/response structures for all API endpoints
 */

import { 
  SalesRecord, 
  DataUpload, 
  ValidationResult, 
  QuestionnaireResponse 
} from './data';
import { 
  ForecastRequest, 
  ForecastResult, 
  ForecastSummary 
} from './forecasting';
import { 
  RiskAssessment, 
  RiskAlert, 
  RiskDashboard 
} from './risk';
import { 
  ExplanationRequest, 
  ExplanationResponse, 
  ConversationContext 
} from './explanation';
import { UserProfile } from './user';
import { FestivalCalendar } from './festival';
import { ApiResponse, PaginatedResponse, TimeRange } from './common';

/**
 * Data Upload API
 */
export namespace DataUploadAPI {
  export interface UploadRequest {
    file: File;
    format: 'csv' | 'excel';
    userId: string;
  }

  export interface UploadResponse extends ApiResponse<{
    uploadId: string;
    validation: ValidationResult;
    recordCount: number;
  }> {}

  export interface ProcessRequest {
    uploadId: string;
    userId: string;
    overrideValidation?: boolean;
  }

  export interface ProcessResponse extends ApiResponse<{
    processedRecords: number;
    dataQuality: 'poor' | 'fair' | 'good';
    summary: {
      dateRange: TimeRange;
      categories: string[];
      skus: string[];
    };
  }> {}
}

/**
 * Questionnaire API
 */
export namespace QuestionnaireAPI {
  export interface SubmitRequest extends QuestionnaireResponse {}

  export interface SubmitResponse extends ApiResponse<{
    profileUpdated: boolean;
    dataQualityScore: number;
    readyForForecasting: boolean;
  }> {}
}

/**
 * Forecasting API
 */
export namespace ForecastingAPI {
  export interface GenerateRequest extends ForecastRequest {}

  export interface GenerateResponse extends ApiResponse<{
    forecastId: string;
    results: ForecastResult[];
    summary: ForecastSummary;
  }> {}

  export interface GetForecastRequest {
    userId: string;
    forecastId?: string;
    sku?: string;
    category?: string;
    dateRange?: TimeRange;
  }

  export interface GetForecastResponse extends PaginatedResponse<ForecastResult> {}
}

/**
 * Risk Assessment API
 */
export namespace RiskAssessmentAPI {
  export interface AssessRequest {
    userId: string;
    forecastId: string;
    currentInventory: {
      sku: string;
      quantity: number;
    }[];
  }

  export interface AssessResponse extends ApiResponse<{
    assessmentId: string;
    risks: RiskAssessment[];
    dashboard: RiskDashboard;
    alerts: RiskAlert[];
  }> {}

  export interface GetRisksRequest {
    userId: string;
    severity?: 'low' | 'medium' | 'high' | 'critical';
    category?: string;
    urgency?: 'low' | 'medium' | 'high' | 'critical';
  }

  export interface GetRisksResponse extends PaginatedResponse<RiskAssessment> {}

  export interface GetAlertsRequest {
    userId: string;
    acknowledged?: boolean;
    severity?: 'low' | 'medium' | 'high' | 'critical';
  }

  export interface GetAlertsResponse extends PaginatedResponse<RiskAlert> {}
}

/**
 * AI Explanation API
 */
export namespace ExplanationAPI {
  export interface ExplainRequest extends ExplanationRequest {}

  export interface ExplainResponse extends ApiResponse<ExplanationResponse> {}

  export interface ChatRequest {
    userId: string;
    conversationId?: string;
    message: string;
    context?: {
      forecastId?: string;
      riskAssessmentId?: string;
    };
  }

  export interface ChatResponse extends ApiResponse<{
    conversationId: string;
    response: ExplanationResponse;
    context: ConversationContext;
  }> {}
}

/**
 * User Profile API
 */
export namespace UserProfileAPI {
  export interface GetProfileRequest {
    userId: string;
  }

  export interface GetProfileResponse extends ApiResponse<UserProfile> {}

  export interface UpdateProfileRequest {
    userId: string;
    updates: Partial<UserProfile>;
  }

  export interface UpdateProfileResponse extends ApiResponse<UserProfile> {}

  export interface DeleteProfileRequest {
    userId: string;
    confirmDeletion: boolean;
  }

  export interface DeleteProfileResponse extends ApiResponse<{
    deleted: boolean;
    deletedAt: string;
  }> {}
}

/**
 * Festival Calendar API
 */
export namespace FestivalAPI {
  export interface GetCalendarRequest {
    region: string;
    year: number;
    category?: string;
  }

  export interface GetCalendarResponse extends ApiResponse<FestivalCalendar> {}

  export interface GetUpcomingRequest {
    region: string;
    days: number; // Next N days
    importance?: 'major' | 'regional' | 'local';
  }

  export interface GetUpcomingResponse extends ApiResponse<{
    festivals: Array<{
      festivalId: string;
      name: string;
      date: string;
      daysUntil: number;
      importance: string;
      categories: string[];
    }>;
  }> {}
}

/**
 * Analytics API
 */
export namespace AnalyticsAPI {
  export interface GetDashboardRequest {
    userId: string;
    timeRange?: TimeRange;
  }

  export interface GetDashboardResponse extends ApiResponse<{
    forecasts: {
      total: number;
      accuracy: number;
      confidence: number;
    };
    risks: {
      high: number;
      medium: number;
      low: number;
    };
    recommendations: {
      pending: number;
      implemented: number;
      savings: number;
    };
    trends: {
      demandTrend: 'increasing' | 'decreasing' | 'stable';
      riskTrend: 'improving' | 'worsening' | 'stable';
    };
  }> {}

  export interface GetInsightsRequest {
    userId: string;
    type: 'performance' | 'trends' | 'opportunities';
    timeRange?: TimeRange;
  }

  export interface GetInsightsResponse extends ApiResponse<{
    insights: Array<{
      type: string;
      title: string;
      description: string;
      impact: 'high' | 'medium' | 'low';
      actionable: boolean;
      recommendations: string[];
    }>;
  }> {}
}

/**
 * System API
 */
export namespace SystemAPI {
  export interface HealthCheckResponse extends ApiResponse<{
    status: 'healthy' | 'unhealthy' | 'degraded';
    services: {
      [serviceName: string]: {
        status: 'healthy' | 'unhealthy';
        responseTime: number;
        message?: string;
      };
    };
    timestamp: string;
  }> {}

  export interface GetStatusRequest {
    userId?: string;
  }

  export interface GetStatusResponse extends ApiResponse<{
    systemStatus: 'operational' | 'maintenance' | 'degraded' | 'outage';
    userStatus?: {
      dataProcessing: 'idle' | 'processing' | 'error';
      forecastGeneration: 'idle' | 'processing' | 'error';
      riskAssessment: 'idle' | 'processing' | 'error';
    };
    lastUpdated: string;
  }> {}
}