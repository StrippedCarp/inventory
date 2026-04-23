/**
 * Global error handler utility for API responses
 */

export const handleApiError = (error) => {
  // Network error (no connection)
  if (!error.response) {
    return 'Cannot connect to server, please check your connection';
  }

  // Extract error message from response
  const response = error.response;
  
  // Check for error message in response data
  if (response.data) {
    if (response.data.message) {
      return response.data.message;
    }
    if (response.data.error) {
      // If error is an object with message
      if (typeof response.data.error === 'object' && response.data.error.message) {
        return response.data.error.message;
      }
      // If error is a string
      if (typeof response.data.error === 'string') {
        return response.data.error;
      }
    }
  }

  // Fallback to status-based messages
  switch (response.status) {
    case 400:
      return 'Invalid request. Please check your input.';
    case 401:
      return 'Please login again';
    case 403:
      return "You don't have permission to do this";
    case 404:
      return 'The requested resource does not exist';
    case 409:
      return 'This resource already exists';
    case 500:
      return 'Something went wrong, please try again';
    default:
      return 'An unexpected error occurred';
  }
};

export const getErrorMessage = (error) => {
  return handleApiError(error);
};

export default handleApiError;
