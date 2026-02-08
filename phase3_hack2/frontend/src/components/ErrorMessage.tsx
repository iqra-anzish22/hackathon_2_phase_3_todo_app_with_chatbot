/**
 * Reusable error message display component.
 * Shows user-friendly error messages with optional retry functionality.
 */

import { ApiError } from '@/types/errors';
import { getErrorMessage } from '@/lib/errors';

interface ErrorMessageProps {
  error: ApiError;
  onRetry?: () => void;
}

export default function ErrorMessage({ error, onRetry }: ErrorMessageProps) {
  const message = getErrorMessage(error);

  return (
    <div style={{
      padding: '16px',
      marginBottom: '16px',
      backgroundColor: '#fee',
      border: '1px solid #fcc',
      borderRadius: '4px',
      color: '#c33',
    }}>
      <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>
        Error
      </div>
      <div style={{ marginBottom: error.details ? '12px' : '0' }}>
        {message}
      </div>

      {/* Display field-level validation errors if present */}
      {error.details && error.details.length > 0 && (
        <ul style={{ margin: '8px 0 0 20px', padding: 0 }}>
          {error.details.map((detail, index) => (
            <li key={index} style={{ marginBottom: '4px' }}>
              <strong>{detail.field}:</strong> {detail.message}
            </li>
          ))}
        </ul>
      )}

      {/* Show retry button if onRetry callback provided */}
      {onRetry && (
        <button
          onClick={onRetry}
          style={{
            marginTop: '12px',
            padding: '8px 16px',
            backgroundColor: '#c33',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '14px',
          }}
        >
          Retry
        </button>
      )}
    </div>
  );
}
