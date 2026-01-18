// Error message mapping utility
// Maps backend error messages to translation keys

export const errorMessageMap = {
  // Authentication errors
  'Invalid credentials': 'errorInvalidCredentials',
  'Incorrect username or password': 'errorInvalidCredentials',
  'User not found': 'errorUserNotFound',
  'Username already exists': 'errorUsernameExists',
  'Email already exists': 'errorEmailExists',
  
  // Permission errors
  'Not enough permissions': 'errorInsufficientPermissions',
  'Admin access required': 'errorAdminRequired',
  'Unauthorized': 'error401',
  
  // Validation errors
  'Invalid email format': 'errorInvalidEmail',
  'Password too short': 'errorPasswordTooShort',
  'Required field missing': 'errorRequiredField',
  'Invalid data format': 'errorInvalidFormat',
  
  // Medicine/Stock errors
  'Medicine not found': 'errorMedicineNotFound',
  'Insufficient stock': 'errorInsufficientStock',
  'Medicine already exists': 'errorMedicineExists',
  'Invalid quantity': 'errorInvalidQuantity',
  
  // Supplier errors
  'Supplier not found': 'errorSupplierNotFound',
  'Supplier already exists': 'errorSupplierExists',
  
  // Sale errors
  'Sale not found': 'errorSaleNotFound',
  'Invalid payment method': 'errorInvalidPayment',
  
  // Generic errors
  'Internal server error': 'error500',
  'Bad request': 'error400',
  'Forbidden': 'error403',
};

/**
 * Maps a backend error message to a translation key
 * @param {string} backendMessage - The error message from backend
 * @param {number} status - HTTP status code
 * @returns {string} - Translation key to use
 */
export const mapErrorToTranslationKey = (backendMessage, status) => {
  if (!backendMessage) {
    return `error${status}`;
  }

  // Try exact match first
  if (errorMessageMap[backendMessage]) {
    return errorMessageMap[backendMessage];
  }

  // Try partial match (case-insensitive)
  const lowerMessage = backendMessage.toLowerCase();
  for (const [key, value] of Object.entries(errorMessageMap)) {
    if (lowerMessage.includes(key.toLowerCase())) {
      return value;
    }
  }

  // Fallback to status-based generic message
  return `error${status}`;
};
