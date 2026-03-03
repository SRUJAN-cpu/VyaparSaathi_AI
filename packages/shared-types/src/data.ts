/**
 * Core data interfaces for VyaparSaathi
 * Handles data input, validation, and processing
 */

/**
 * Individual sales record from historical data
 */
export interface SalesRecord {
  /** ISO date format (YYYY-MM-DD) */
  date: string;
  /** Product identifier/Stock Keeping Unit */
  sku: string;
  /** Units sold */
  quantity: number;
  /** Optional product category */
  category?: string;
  /** Optional unit price */
  price?: number;
}

/**
 * Data upload request with file and metadata
 */
export interface DataUpload {
  /** User identifier */
  userId: string;
  /** Uploaded file (CSV or Excel) */
  file: File;
  /** File format type */
  format: 'csv' | 'excel';
  /** Validation results */
  validation: ValidationResult;
}

/**
 * Result of data validation process
 */
export interface ValidationResult {
  /** Whether validation passed */
  success: boolean;
  /** Number of records successfully parsed */
  parsedRecords: number;
  /** Number of records with errors */
  errorRecords: number;
  /** Detailed error messages */
  errorMessages: string[];
  /** Warnings for data quality issues */
  warnings: string[];
  /** Data quality score (0-1) */
  qualityScore: number;
  /** Missing required fields */
  missingFields: string[];
  /** Detected data format issues */
  formatIssues: string[];
}

/**
 * Low-data mode questionnaire response
 */
export interface QuestionnaireResponse {
  /** User identifier */
  userId: string;
  /** Type of business */
  businessType: 'grocery' | 'apparel' | 'electronics' | 'general';
  /** Store size category */
  storeSize: 'small' | 'medium' | 'large';
  /** Performance data from last festival */
  lastFestivalPerformance: {
    festival: string;
    salesIncrease: number; // Percentage increase
    topCategories: string[];
    stockoutItems: string[];
  };
  /** Current inventory estimates */
  currentInventory: InventoryEstimate[];
  /** Target festivals for forecasting */
  targetFestivals: string[];
}

/**
 * Inventory estimate for low-data mode
 */
export interface InventoryEstimate {
  /** Product category */
  category: string;
  /** Current stock level */
  currentStock: number;
  /** Average daily sales estimate */
  averageDailySales: number;
  /** Confidence in the estimate */
  confidence: 'low' | 'medium' | 'high';
}