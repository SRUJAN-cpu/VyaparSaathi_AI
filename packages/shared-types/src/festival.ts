/**
 * Festival and seasonal event interfaces for VyaparSaathi
 */

/**
 * Festival event definition
 */
export interface FestivalEvent {
  /** Unique festival identifier */
  festivalId: string;
  /** Festival name */
  name: string;
  /** Festival date (ISO format) */
  date: string;
  /** Regions where festival is celebrated */
  region: string[];
  /** Festival category */
  category: FestivalCategory;
  /** Demand multipliers by product category */
  demandMultipliers: {
    [category: string]: number;
  };
  /** Festival duration in days */
  duration: number;
  /** Preparation lead time needed in days */
  preparationDays: number;
  /** Festival importance level */
  importance: 'major' | 'regional' | 'local';
  /** Historical impact data */
  historicalImpact: {
    /** Average sales increase percentage */
    averageIncrease: number;
    /** Peak demand day offset from festival date */
    peakDayOffset: number;
    /** Demand pattern (gradual, spike, sustained) */
    pattern: 'gradual' | 'spike' | 'sustained';
  };
  /** Festival metadata */
  metadata: {
    /** Festival description */
    description: string;
    /** Cultural significance */
    significance: string;
    /** Typical celebration activities */
    activities: string[];
    /** Associated product categories */
    associatedCategories: string[];
  };
}

/**
 * Festival categories
 */
export type FestivalCategory = 
  | 'religious' 
  | 'cultural' 
  | 'seasonal' 
  | 'national' 
  | 'regional' 
  | 'harvest' 
  | 'new_year' 
  | 'wedding_season';

/**
 * Festival calendar for a specific region and time period
 */
export interface FestivalCalendar {
  /** Region identifier */
  region: string;
  /** Calendar year */
  year: number;
  /** List of festivals in chronological order */
  festivals: FestivalEvent[];
  /** Regional preferences */
  regionalPreferences: {
    /** Most important festivals for this region */
    majorFestivals: string[];
    /** Regional demand patterns */
    regionalPatterns: {
      [category: string]: {
        baselineMultiplier: number;
        seasonalVariation: number;
      };
    };
  };
  /** Calendar metadata */
  metadata: {
    /** Calendar creation timestamp */
    createdAt: string;
    /** Last update timestamp */
    lastUpdated: string;
    /** Data source */
    source: string;
    /** Completeness score */
    completeness: number;
  };
}

/**
 * Festival impact analysis
 */
export interface FestivalImpact {
  /** Festival identifier */
  festivalId: string;
  /** Business type */
  businessType: string;
  /** Region */
  region: string;
  /** Impact analysis */
  impact: {
    /** Days before festival when impact starts */
    impactStartDays: number;
    /** Days after festival when impact ends */
    impactEndDays: number;
    /** Peak impact day relative to festival */
    peakImpactDay: number;
    /** Category-specific impacts */
    categoryImpacts: {
      [category: string]: {
        /** Demand multiplier */
        multiplier: number;
        /** Impact confidence (0-1) */
        confidence: number;
        /** Impact pattern */
        pattern: number[]; // Daily multipliers
      };
    };
  };
  /** Analysis metadata */
  metadata: {
    /** Analysis timestamp */
    analyzedAt: string;
    /** Data sources used */
    dataSources: string[];
    /** Sample size */
    sampleSize: number;
  };
}