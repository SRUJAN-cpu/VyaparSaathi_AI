/**
 * User profile and business context interfaces for VyaparSaathi
 */

/**
 * Comprehensive user profile
 */
export interface UserProfile {
  /** Unique user identifier */
  userId: string;
  /** Business information */
  businessInfo: {
    /** Business name */
    name: string;
    /** Business type */
    type: BusinessType;
    /** Business location */
    location: {
      city: string;
      state: string;
      region: string;
      country: string;
      timezone: string;
    };
    /** Store size category */
    size: StoreSize;
    /** Years in business */
    yearsInBusiness: number;
    /** Primary product categories */
    primaryCategories: string[];
  };
  /** Data capabilities and quality */
  dataCapabilities: {
    /** Whether user has historical sales data */
    hasHistoricalData: boolean;
    /** Data quality assessment */
    dataQuality: 'poor' | 'fair' | 'good';
    /** Last data update timestamp */
    lastUpdated: string;
    /** Data completeness score (0-1) */
    completenessScore: number;
    /** Available data period in months */
    dataHistoryMonths: number;
  };
  /** User preferences */
  preferences: {
    /** Preferred forecast horizon in days */
    forecastHorizon: number;
    /** Risk tolerance level */
    riskTolerance: 'conservative' | 'moderate' | 'aggressive';
    /** Notification settings */
    notificationSettings: NotificationSettings;
    /** Preferred explanation complexity */
    explanationComplexity: 'simple' | 'detailed';
    /** Dashboard customization */
    dashboardPreferences: DashboardPreferences;
  };
  /** Account metadata */
  metadata: {
    /** Account creation timestamp */
    createdAt: string;
    /** Last login timestamp */
    lastLogin: string;
    /** Account status */
    status: 'active' | 'inactive' | 'suspended';
    /** Subscription tier */
    tier: 'free' | 'basic' | 'premium';
  };
}

/**
 * Business type enumeration
 */
export type BusinessType = 
  | 'grocery' 
  | 'apparel' 
  | 'electronics' 
  | 'general' 
  | 'pharmacy' 
  | 'jewelry' 
  | 'books' 
  | 'toys' 
  | 'home_goods' 
  | 'sports' 
  | 'automotive';

/**
 * Store size categories
 */
export type StoreSize = 'small' | 'medium' | 'large' | 'chain';

/**
 * Notification preferences
 */
export interface NotificationSettings {
  /** Email notifications enabled */
  email: boolean;
  /** SMS notifications enabled */
  sms: boolean;
  /** Push notifications enabled */
  push: boolean;
  /** Notification frequency */
  frequency: 'immediate' | 'daily' | 'weekly';
  /** Risk alert thresholds */
  riskAlerts: {
    /** Stockout risk threshold */
    stockoutThreshold: number;
    /** Overstock risk threshold */
    overstockThreshold: number;
    /** Festival preparation alerts */
    festivalAlerts: boolean;
  };
}

/**
 * Dashboard customization preferences
 */
export interface DashboardPreferences {
  /** Default view */
  defaultView: 'overview' | 'forecasts' | 'risks' | 'recommendations';
  /** Visible widgets */
  visibleWidgets: string[];
  /** Chart preferences */
  chartPreferences: {
    /** Chart type for forecasts */
    forecastChartType: 'line' | 'bar' | 'area';
    /** Time range for default view */
    defaultTimeRange: '7d' | '14d' | '30d';
    /** Show confidence intervals */
    showConfidenceIntervals: boolean;
  };
  /** Color theme */
  theme: 'light' | 'dark' | 'auto';
}