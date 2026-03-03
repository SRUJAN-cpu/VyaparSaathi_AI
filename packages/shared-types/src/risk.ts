/**
 * Risk assessment interfaces for VyaparSaathi
 * Handles inventory risk calculation and reorder recommendations
 */

/**
 * Comprehensive risk assessment for a SKU/category
 */
export interface RiskAssessment {
  /** Product SKU */
  sku: string;
  /** Product category */
  category: string;
  /** Current inventory level */
  currentStock: number;
  /** Stockout risk analysis */
  stockoutRisk: {
    /** Probability of stockout (0-1) */
    probability: number;
    /** Days until stockout occurs */
    daysUntilStockout: number;
    /** Potential lost sales value */
    potentialLostSales: number;
    /** Peak risk day */
    peakRiskDay: string;
  };
  /** Overstock risk analysis */
  overstockRisk: {
    /** Probability of overstock (0-1) */
    probability: number;
    /** Excess units after forecast period */
    excessUnits: number;
    /** Estimated carrying cost */
    carryingCost: number;
    /** Days of excess inventory */
    excessDays: number;
  };
  /** Reorder recommendation */
  recommendation: ReorderRecommendation;
  /** Risk assessment timestamp */
  assessedAt: string;
  /** Assessment confidence (0-1) */
  confidence: number;
}

/**
 * Reorder recommendation with specific actions
 */
export interface ReorderRecommendation {
  /** Recommended action */
  action: 'reorder' | 'reduce' | 'maintain' | 'urgent_reorder';
  /** Suggested quantity to order */
  suggestedQuantity: number;
  /** Urgency level */
  urgency: 'low' | 'medium' | 'high' | 'critical';
  /** Reasoning for recommendation */
  reasoning: string[];
  /** Confidence in recommendation (0-1) */
  confidence: number;
  /** Optimal reorder timing */
  optimalTiming: {
    /** Days from now to place order */
    daysFromNow: number;
    /** Recommended order date */
    orderDate: string;
    /** Expected delivery date */
    expectedDelivery: string;
  };
  /** Financial impact */
  financialImpact: {
    /** Cost of recommended action */
    orderCost: number;
    /** Potential savings from avoiding stockout */
    stockoutSavings: number;
    /** Potential savings from avoiding overstock */
    overstockSavings: number;
    /** Net financial benefit */
    netBenefit: number;
  };
}

/**
 * Risk alert for high-risk situations
 */
export interface RiskAlert {
  /** Alert identifier */
  alertId: string;
  /** User identifier */
  userId: string;
  /** Product SKU */
  sku: string;
  /** Alert type */
  type: 'stockout_warning' | 'overstock_warning' | 'urgent_reorder' | 'festival_preparation';
  /** Alert severity */
  severity: 'low' | 'medium' | 'high' | 'critical';
  /** Alert message */
  message: string;
  /** Detailed description */
  description: string;
  /** Recommended actions */
  actions: string[];
  /** Alert creation timestamp */
  createdAt: string;
  /** Alert expiry timestamp */
  expiresAt: string;
  /** Whether alert has been acknowledged */
  acknowledged: boolean;
}

/**
 * Risk dashboard summary
 */
export interface RiskDashboard {
  /** User identifier */
  userId: string;
  /** Overall risk score (0-1) */
  overallRiskScore: number;
  /** Risk breakdown by category */
  riskBreakdown: {
    /** High-risk SKUs count */
    highRisk: number;
    /** Medium-risk SKUs count */
    mediumRisk: number;
    /** Low-risk SKUs count */
    lowRisk: number;
  };
  /** Active alerts count */
  activeAlerts: number;
  /** Urgent actions needed */
  urgentActions: number;
  /** Total potential lost sales */
  totalPotentialLoss: number;
  /** Total carrying cost risk */
  totalCarryingCost: number;
  /** Dashboard generation timestamp */
  generatedAt: string;
}