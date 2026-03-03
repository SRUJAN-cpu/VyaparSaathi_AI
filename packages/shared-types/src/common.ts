/**
 * Common utility types and enums for VyaparSaathi
 */

/**
 * Generic API response wrapper
 */
export interface ApiResponse<T> {
  /** Response success status */
  success: boolean;
  /** Response data */
  data?: T;
  /** Error message if failed */
  error?: string;
  /** Detailed error information */
  errorDetails?: {
    code: string;
    message: string;
    field?: string;
    details?: any;
  };
  /** Response metadata */
  metadata?: {
    timestamp: string;
    requestId: string;
    version: string;
  };
}

/**
 * Pagination information
 */
export interface PaginationInfo {
  /** Current page number */
  page: number;
  /** Items per page */
  limit: number;
  /** Total number of items */
  total: number;
  /** Total number of pages */
  totalPages: number;
  /** Whether there's a next page */
  hasNext: boolean;
  /** Whether there's a previous page */
  hasPrev: boolean;
}

/**
 * Paginated response wrapper
 */
export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  /** Pagination information */
  pagination: PaginationInfo;
}

/**
 * Time range specification
 */
export interface TimeRange {
  /** Start date (ISO format) */
  startDate: string;
  /** End date (ISO format) */
  endDate: string;
  /** Time zone */
  timezone?: string;
}

/**
 * Geographic location
 */
export interface Location {
  /** City name */
  city: string;
  /** State/province */
  state: string;
  /** Country */
  country: string;
  /** Region identifier */
  region: string;
  /** Timezone */
  timezone: string;
  /** Optional coordinates */
  coordinates?: {
    latitude: number;
    longitude: number;
  };
}

/**
 * Confidence levels
 */
export type ConfidenceLevel = 'very_low' | 'low' | 'medium' | 'high' | 'very_high';

/**
 * Data quality levels
 */
export type DataQuality = 'poor' | 'fair' | 'good' | 'excellent';

/**
 * Alert severity levels
 */
export type AlertSeverity = 'info' | 'warning' | 'error' | 'critical';

/**
 * System status
 */
export type SystemStatus = 'active' | 'inactive' | 'maintenance' | 'error';

/**
 * Processing status
 */
export type ProcessingStatus = 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';

/**
 * Currency information
 */
export interface Currency {
  /** Currency code (ISO 4217) */
  code: string;
  /** Currency symbol */
  symbol: string;
  /** Currency name */
  name: string;
}

/**
 * Money amount with currency
 */
export interface MoneyAmount {
  /** Amount value */
  amount: number;
  /** Currency information */
  currency: Currency;
}

/**
 * File information
 */
export interface FileInfo {
  /** File name */
  name: string;
  /** File size in bytes */
  size: number;
  /** MIME type */
  mimeType: string;
  /** Upload timestamp */
  uploadedAt: string;
  /** File URL or path */
  url?: string;
}

/**
 * Audit trail entry
 */
export interface AuditEntry {
  /** Entry identifier */
  id: string;
  /** User who performed the action */
  userId: string;
  /** Action performed */
  action: string;
  /** Resource affected */
  resource: string;
  /** Resource identifier */
  resourceId: string;
  /** Timestamp of action */
  timestamp: string;
  /** Additional details */
  details?: any;
  /** IP address */
  ipAddress?: string;
  /** User agent */
  userAgent?: string;
}

/**
 * Health check response
 */
export interface HealthCheck {
  /** Service status */
  status: 'healthy' | 'unhealthy' | 'degraded';
  /** Timestamp of check */
  timestamp: string;
  /** Service version */
  version: string;
  /** Component statuses */
  components: {
    [componentName: string]: {
      status: 'healthy' | 'unhealthy';
      message?: string;
      responseTime?: number;
    };
  };
  /** Overall response time */
  responseTime: number;
}