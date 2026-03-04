/**
 * API Service
 * Handles all backend API calls using AWS Amplify
 */

import { get, post } from 'aws-amplify/api';

const API_NAME = 'VyaparSaathiAPI';

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

/**
 * Upload sales data
 */
export async function uploadSalesData(file: File): Promise<ApiResponse<any>> {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await post({
      apiName: API_NAME,
      path: '/data/upload',
      options: {
        body: formData,
      },
    }).response;

    const data = await response.body.json();
    return { success: true, data };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Upload failed',
    };
  }
}

/**
 * Submit questionnaire data
 */
export async function submitQuestionnaire(data: any): Promise<ApiResponse<any>> {
  try {
    const response = await post({
      apiName: API_NAME,
      path: '/data/questionnaire',
      options: {
        body: data,
      },
    }).response;

    const result = await response.body.json();
    return { success: true, data: result };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Submission failed',
    };
  }
}

/**
 * Get forecast data
 */
export async function getForecast(params: {
  forecastHorizon?: number;
  targetFestivals?: string[];
}): Promise<ApiResponse<any>> {
  try {
    const queryParams = new URLSearchParams();
    if (params.forecastHorizon) {
      queryParams.append('horizon', params.forecastHorizon.toString());
    }
    if (params.targetFestivals) {
      queryParams.append('festivals', params.targetFestivals.join(','));
    }

    const response = await get({
      apiName: API_NAME,
      path: `/forecast?${queryParams.toString()}`,
    }).response;

    const data = await response.body.json();
    return { success: true, data };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to fetch forecast',
    };
  }
}

/**
 * Get risk assessment
 */
export async function getRiskAssessment(): Promise<ApiResponse<any>> {
  try {
    const response = await get({
      apiName: API_NAME,
      path: '/risk',
    }).response;

    const data = await response.body.json();
    return { success: true, data };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to fetch risk assessment',
    };
  }
}

/**
 * Ask AI copilot a question
 */
export async function askCopilot(query: string, context?: any): Promise<ApiResponse<any>> {
  try {
    const response = await post({
      apiName: API_NAME,
      path: '/copilot/query',
      options: {
        body: {
          query,
          context,
        },
      },
    }).response;

    const data = await response.body.json();
    return { success: true, data };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to get response',
    };
  }
}

/**
 * Get explanation for forecast or risk
 */
export async function getExplanation(
  type: 'forecast' | 'risk',
  data: any
): Promise<ApiResponse<any>> {
  try {
    const response = await post({
      apiName: API_NAME,
      path: '/explanation',
      options: {
        body: {
          context: type,
          data,
          complexity: 'simple',
        },
      },
    }).response;

    const result = await response.body.json();
    return { success: true, data: result };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to get explanation',
    };
  }
}
