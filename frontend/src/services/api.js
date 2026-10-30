/**
 * API service for communicating with Member 2's FastAPI Scoring Service.
 * 
 * Uses VITE_API_BASE_URL from environment with fallback to http://localhost:8000.
 */

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/+$/, '');

export class ApiError extends Error {
  constructor(message, status, details = null) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.details = details;
  }
}

/**
 * Submits an applicant feature payload to the backend POST /score endpoint.
 *
 * @param {Object} scoreRequest - Must match Member 2's ScoreRequest schema:
 * {
 *   applicant_id: string,
 *   analysis_period_months: number,
 *   features: {
 *     active_months_ratio: number,
 *     income_cv: number,
 *     source_diversity: number,
 *     positive_cashflow_months_ratio: number,
 *     expense_to_income_ratio: number,
 *     income_trend: number,
 *     emergency_buffer_days: number | null
 *   },
 *   data_quality?: Object | null
 * }
 * @returns {Promise<Object>} API response including score, band, confidence, factors, risk_flags, etc.
 */
export async function scoreApplicant(scoreRequest) {
  const url = `${API_BASE_URL}/score`;

  let response;
  try {
    response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(scoreRequest),
    });
  } catch (networkErr) {
    throw new ApiError(
      `Network connection failed. Unable to reach scoring service at ${url}. Ensure the backend service is running.`,
      0,
      networkErr
    );
  }

  const responseText = await response.text();
  let responseData = null;
  if (responseText) {
    try {
      responseData = JSON.parse(responseText);
    } catch {
      responseData = responseText;
    }
  }

  if (!response.ok) {
    let errorMessage = `Scoring service error (${response.status})`;
    if (responseData && typeof responseData === 'object' && responseData.detail) {
      if (Array.isArray(responseData.detail)) {
        // FastAPI / Pydantic validation error list
        const messages = responseData.detail.map((err) => {
          const loc = Array.isArray(err.loc) ? err.loc.join('.') : '';
          return `${loc ? `[${loc}]: ` : ''}${err.msg || 'Invalid field'}`;
        });
        errorMessage = `Validation error: ${messages.join('; ')}`;
      } else {
        errorMessage = String(responseData.detail);
      }
    }
    throw new ApiError(errorMessage, response.status, responseData);
  }

  return responseData;
}


/**
 * Upload a transaction CSV for automatic EarnScore assessment.
 * The backend handles cleaning, feature extraction and scoring.
 */
export async function scoreUploadedCsv(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/score/upload-csv`, {
    method: 'POST',
    body: formData,
  });

  const data = await response.json();

  if (!response.ok) {
    throw new ApiError(
      typeof data.detail === 'string'
        ? data.detail
        : `CSV scoring failed (${response.status})`,
      response.status,
      data
    );
  }

  return data;
}
