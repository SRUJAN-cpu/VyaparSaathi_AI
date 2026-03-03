/**
 * Synthetic data generation interfaces for VyaparSaathi
 * Used for demo mode and low-data scenarios
 */

import { BusinessType } from './user';

/**
 * Synthetic pattern definition for generating realistic data
 */
export interface SyntheticPattern {
  /** Business type this pattern applies to */
  businessType: BusinessType;
  /** Geographic region */
  region: string;
  /** Target festival */
  festival: string;
  /** Baseline demand patterns */
  baselinePatterns: {
    /** Product category */
    category: string;
    /** Normal daily demand */
    normalDemand: number;
    /** Festival demand multiplier */
    festivalMultiplier: number;
    /** Peak demand days (relative to festival) */
    peakDays: number[];
    /** Demand variance/noise level */
    variance: number;
    /** Seasonal trend factor */
    seasonalTrend: number;
  }[];
  /** Seasonal adjustment factors */
  seasonalFactors: {
    /** Month (1-12) */
    month: number;
    /** Seasonal adjustment factor */
    factor: number;
  }[];
  /** Weekly patterns */
  weeklyPatterns: {
    /** Day of week (0=Sunday, 6=Saturday) */
    dayOfWeek: number;
    /** Weekly adjustment factor */
    factor: number;
  }[];
  /** Pattern metadata */
  metadata: {
    /** Pattern creation timestamp */
    createdAt: string;
    /** Data sources used to create pattern */
    dataSources: string[];
    /** Pattern confidence score */
    confidence: number;
    /** Sample size used */
    sampleSize: number;
  };
}

/**
 * Synthetic data generation configuration
 */
export interface SyntheticDataConfig {
  /** Business context */
  businessContext: {
    businessType: BusinessType;
    region: string;
    storeSize: 'small' | 'medium' | 'large';
    categories: string[];
  };
  /** Time period for data generation */
  timePeriod: {
    /** Start date (ISO format) */
    startDate: string;
    /** End date (ISO format) */
    endDate: string;
    /** Data frequency */
    frequency: 'daily' | 'weekly';
  };
  /** Data characteristics */
  dataCharacteristics: {
    /** Number of SKUs to generate */
    skuCount: number;
    /** Average daily sales volume */
    averageDailySales: number;
    /** Data noise level (0-1) */
    noiseLevel: number;
    /** Include seasonal trends */
    includeSeasonality: boolean;
    /** Include festival impacts */
    includeFestivals: boolean;
  };
  /** Quality settings */
  qualitySettings: {
    /** Missing data percentage */
    missingDataRate: number;
    /** Data error rate */
    errorRate: number;
    /** Outlier frequency */
    outlierRate: number;
  };
}

/**
 * Generated synthetic dataset
 */
export interface SyntheticDataset {
  /** Dataset identifier */
  datasetId: string;
  /** Generation configuration used */
  config: SyntheticDataConfig;
  /** Generated sales records */
  salesData: {
    date: string;
    sku: string;
    category: string;
    quantity: number;
    price: number;
    isSynthetic: true; // Always true for synthetic data
  }[];
  /** Dataset statistics */
  statistics: {
    /** Total records generated */
    totalRecords: number;
    /** Date range covered */
    dateRange: {
      start: string;
      end: string;
    };
    /** Categories included */
    categories: string[];
    /** SKUs generated */
    skus: string[];
    /** Average daily volume */
    averageDailyVolume: number;
  };
  /** Generation metadata */
  metadata: {
    /** Generation timestamp */
    generatedAt: string;
    /** Generation duration in seconds */
    generationTime: number;
    /** Patterns used */
    patternsUsed: string[];
    /** Quality indicators */
    qualityIndicators: {
      realism: number; // 0-1 score
      consistency: number; // 0-1 score
      completeness: number; // 0-1 score
    };
  };
}

/**
 * Demo scenario definition
 */
export interface DemoScenario {
  /** Scenario identifier */
  scenarioId: string;
  /** Scenario name */
  name: string;
  /** Scenario description */
  description: string;
  /** Business context for scenario */
  businessContext: {
    businessType: BusinessType;
    businessName: string;
    location: string;
    storeSize: 'small' | 'medium' | 'large';
  };
  /** Pre-generated data */
  syntheticData: SyntheticDataset;
  /** Scenario narrative */
  narrative: {
    /** Background story */
    background: string;
    /** Current situation */
    currentSituation: string;
    /** Challenges faced */
    challenges: string[];
    /** Expected outcomes */
    expectedOutcomes: string[];
  };
  /** Learning objectives */
  learningObjectives: string[];
  /** Scenario metadata */
  metadata: {
    /** Difficulty level */
    difficulty: 'beginner' | 'intermediate' | 'advanced';
    /** Estimated completion time */
    estimatedTime: number; // minutes
    /** Tags for categorization */
    tags: string[];
  };
}