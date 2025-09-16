// API configuration and constants
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
export const API_VERSION = 'v1';
export const API_ENDPOINTS = {
  auth: {
    login: `/api/${API_VERSION}/auth/login`,
    refresh: `/api/${API_VERSION}/auth/refresh`,
    logout: `/api/${API_VERSION}/auth/logout`,
    validate: `/api/${API_VERSION}/auth/validate`,
  },
  requirements: {
    base: `/api/${API_VERSION}/requirements`,
    upload: `/api/${API_VERSION}/requirements/upload`,
    parse: `/api/${API_VERSION}/requirements/parse`,
  },
  testCases: {
    base: `/api/${API_VERSION}/test-cases`,
    generate: `/api/${API_VERSION}/test-cases/generate`,
    export: `/api/${API_VERSION}/test-cases/export`,
  },
  compliance: {
    base: `/api/${API_VERSION}/compliance`,
    validate: `/api/${API_VERSION}/compliance/validate`,
    rules: `/api/${API_VERSION}/compliance/rules`,
  },
  alm: {
    base: `/api/${API_VERSION}/alm`,
    platforms: `/api/${API_VERSION}/alm/platforms`,
    sync: `/api/${API_VERSION}/alm/sync`,
  },
  health: `/api/${API_VERSION}/health`,
};

// HTTP Status codes
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  INTERNAL_SERVER_ERROR: 500,
};

// Application constants
export const APP_CONFIG = {
  name: 'Healthcare Test Case Generator',
  version: '1.0.0',
  description: 'AI-powered healthcare test case generation system',
  supportedFormats: ['pdf', 'docx', 'xml', 'md', 'txt'],
  maxFileSize: 10 * 1024 * 1024, // 10MB
  maxFiles: 5,
};

// Healthcare compliance standards
export const COMPLIANCE_STANDARDS = {
  'FDA_CFR_820': 'FDA 21 CFR Part 820',
  'IEC_62304': 'IEC 62304',
  'ISO_9001': 'ISO 9001',
  'ISO_13485': 'ISO 13485',
  'ISO_27001': 'ISO 27001',
  'GDPR': 'GDPR',
  'HIPAA': 'HIPAA',
};

// Test case priorities
export const TEST_PRIORITIES = {
  CRITICAL: 'Critical',
  HIGH: 'High', 
  MEDIUM: 'Medium',
  LOW: 'Low',
};

// Test case statuses
export const TEST_STATUSES = {
  DRAFT: 'Draft',
  REVIEW: 'Under Review',
  APPROVED: 'Approved',
  REJECTED: 'Rejected',
  EXECUTED: 'Executed',
  PASSED: 'Passed',
  FAILED: 'Failed',
};

// Requirement categories
export const REQUIREMENT_CATEGORIES = {
  FUNCTIONAL: 'Functional',
  SECURITY: 'Security',
  PERFORMANCE: 'Performance',
  USABILITY: 'Usability',
  COMPLIANCE: 'Compliance',
  INTERFACE: 'Interface',
  DATA: 'Data Management',
};

// ALM platforms
export const ALM_PLATFORMS = {
  JIRA: 'Jira',
  POLARION: 'Polarion',
  AZURE_DEVOPS: 'Azure DevOps',
  TESTLINK: 'TestLink',
  XRAY: 'Xray',
};

// Error messages
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network error. Please check your connection.',
  AUTH_FAILED: 'Authentication failed. Please check your credentials.',
  INVALID_FILE: 'Invalid file format. Please upload a supported file type.',
  FILE_TOO_LARGE: 'File is too large. Maximum size is 10MB.',
  GENERIC_ERROR: 'An error occurred. Please try again.',
  SESSION_EXPIRED: 'Session expired. Please log in again.',
};

// Success messages
export const SUCCESS_MESSAGES = {
  LOGIN_SUCCESS: 'Successfully logged in',
  LOGOUT_SUCCESS: 'Successfully logged out',
  FILE_UPLOADED: 'File uploaded successfully',
  TEST_CASES_GENERATED: 'Test cases generated successfully',
  SETTINGS_SAVED: 'Settings saved successfully',
  SYNC_COMPLETED: 'ALM synchronization completed',
};

// Local storage keys
export const STORAGE_KEYS = {
  AUTH_TOKEN: 'auth_token',
  USER_PREFERENCES: 'user_preferences',
  THEME: 'theme_preference',
  LANGUAGE: 'language_preference',
};

// Theme configuration
export const THEME_CONFIG = {
  light: {
    primary: '#1976d2',
    secondary: '#dc004e',
    background: '#ffffff',
    surface: '#f5f5f5',
    text: '#333333',
  },
  dark: {
    primary: '#90caf9',
    secondary: '#f48fb1',
    background: '#121212',
    surface: '#1e1e1e',
    text: '#ffffff',
  },
};