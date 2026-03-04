/**
 * API Service
 * Handles all backend API calls using AWS Amplify
 */

import { get, post } from 'aws-amplify/api';
import { fetchAuthSession } from 'aws-amplify/auth';

const API_NAME = 'VyaparSaathiAPI';

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

/**
 * Get authenticated user ID from Cognito session
 */
async function getUserId(): Promise<string> {
  try {
    const session = await fetchAuthSession();
    return session.userSub || 'anonymous';
  } catch (error) {
    console.error('Failed to get user session:', error);
    return 'anonymous';
  }
}

/**
 * Upload sales data
 */
export async function uploadSalesData(file: File): Promise<ApiResponse<any>> {
  try {
    const userId = await getUserId();
    
    // Read file content
    const fileContent = await file.text();
    
    const response = await post({
      apiName: API_NAME,
      path: '/data/upload',
      options: {
        body: {
          userId,
          dataType: 'csv',
          fileContent,
          fileName: file.name,
        },
      },
    }).response;

    const data = await response.body.json();
    return { success: true, data };
  } catch (error) {
    console.error('Upload error:', error);
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
    const userId = await getUserId();
    
    const response = await post({
      apiName: API_NAME,
      path: '/data/upload',
      options: {
        body: {
          userId,
          dataType: 'questionnaire',
          questionnaireData: data,
        },
      },
    }).response;

    const result = await response.body.json();
    return { success: true, data: result };
  } catch (error) {
    console.error('Questionnaire submission error:', error);
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
    const userId = await getUserId();
    
    const response = await post({
      apiName: API_NAME,
      path: '/forecast',
      options: {
        body: {
          userId,
          forecastHorizon: params.forecastHorizon || 14,
          targetFestivals: params.targetFestivals || [],
        },
      },
    }).response;

    const data = await response.body.json();
    return { success: true, data };
  } catch (error) {
    console.error('Forecast fetch error:', error);
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
    const userId = await getUserId();
    
    const response = await post({
      apiName: API_NAME,
      path: '/risk',
      options: {
        body: {
          userId,
        },
      },
    }).response;

    const data = await response.body.json();
    return { success: true, data };
  } catch (error) {
    console.error('Risk assessment fetch error:', error);
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
    const userId = await getUserId();
    
    const response = await post({
      apiName: API_NAME,
      path: '/explanation',
      options: {
        body: {
          userId,
          query,
          context: context || {},
          complexity: 'simple',
        },
      },
    }).response;

    const data = await response.body.json();
    return { success: true, data };
  } catch (error) {
    console.error('Copilot query error:', error);
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
    const userId = await getUserId();
    
    const response = await post({
      apiName: API_NAME,
      path: '/explanation',
      options: {
        body: {
          userId,
          context: type,
          data,
          complexity: 'simple',
        },
      },
    }).response;

    const result = await response.body.json();
    return { success: true, data: result };
  } catch (error) {
    console.error('Explanation fetch error:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to get explanation',
    };
  }
}
