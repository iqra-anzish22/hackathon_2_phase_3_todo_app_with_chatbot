/**
 * Error type definitions for API error handling.
 * Defines the structure of error responses from the backend.
 */

export interface ApiError {
  error_code: string;
  message: string;
  details?: Array<{
    field: string;
    message: string;
  }>;
}

export interface ErrorDetail {
  field: string;
  message: string;
}
