"""
Custom exceptions for the Healthcare Test Case Generation System
"""

class HealthcareTestGenException(Exception):
    """Base exception class for the application"""
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class DocumentProcessingError(HealthcareTestGenException):
    """Exception raised when document processing fails"""
    pass


class UnsupportedFormatError(HealthcareTestGenException):
    """Exception raised when an unsupported file format is encountered"""
    pass


class RequirementExtractionError(HealthcareTestGenException):
    """Exception raised when requirement extraction fails"""
    pass


class AIProcessingError(HealthcareTestGenException):
    """Exception raised when AI processing fails"""
    pass


class ComplianceValidationError(HealthcareTestGenException):
    """Exception raised when compliance validation fails"""
    pass


class ALMIntegrationError(HealthcareTestGenException):
    """Exception raised when ALM integration fails"""
    pass


class AuthenticationError(HealthcareTestGenException):
    """Exception raised when authentication fails"""
    pass


class AuthorizationError(HealthcareTestGenException):
    """Exception raised when authorization fails"""
    pass


class ValidationError(HealthcareTestGenException):
    """Exception raised when data validation fails"""
    pass


class ConfigurationError(HealthcareTestGenException):
    """Exception raised when configuration is invalid"""
    pass