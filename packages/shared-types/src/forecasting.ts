/**
 * Forecasting interfaces for VyaparSaathi
 * Handles demand prediction and forecast generation
 */

/**
 * Request for generating demand forecast
 */
export interface ForecastRequest {
  /** User identifier */
  userId: string;
  /** Forecast horizon in days (7-14) */
  forecastHorizon: number;
  /** Target festivals to consider */
  targetFestivals: string[];
  /** Data mode for forecasting */
  dataMode: 'structured' | 'low-data';
  /** Minimum confidence threshold (0-1) */
  confidence: number;
  /** Optional specific SKUs to forecast */
  skus?: string[];
  /** Optional categories to forecast */
  categories?: string[];
}

/**
 * Generated forecast result for a specific SKU/category
 */
export interface ForecastResult {
  /** Product SKU */
  sku: string;
  /** Product category */
  category: string;
  /** Daily predictions array */
  predictions: DailyPrediction[];
  /** Overall confidence score (0-1) */
  confidence: number;
  /** Forecasting methodology used */
  methodology: 'ml' | 'pattern' | 'hybrid';
  /** Key assumptions made in forecast */
  assumptions: string[];
  /** Forecast generation timestamp */
  generatedAt: string;
  /** Forecast expiry timestamp */
  expiresAt: string;
}

/**
 * Daily demand prediction
 */
export interface DailyPrediction {
  /** Date in ISO format (YYYY-MM-DD) */
  date: string;
  /** Predicted demand quantity */
  demandForecast: number;
  /** Lower bound of prediction interval */
  lowerBound: number;
  /** Upper bound of prediction interval */
  upperBound: number;
  /** Festival impact multiplier */
  festivalMultiplier: number;
  /** Day-specific confidence (0-1) */
  confidence: number;
  /** Contributing festivals for this day */
  festivals: string[];
}

/**
 * Forecast summary statistics
 */
export interface ForecastSummary {
  /** User identifier */
  userId: string;
  /** Total SKUs forecasted */
  totalSkus: number;
  /** Average confidence across all forecasts */
  averageConfidence: number;
  /** Peak demand day */
  peakDemandDay: string;
  /** Total predicted demand over horizon */
  totalDemand: number;
  /** Forecast generation metadata */
  metadata: {
    dataQuality: 'poor' | 'fair' | 'good';
    festivalCount: number;
    methodologyBreakdown: {
      ml: number;
      pattern: number;
      hybrid: number;
    };
  };
}