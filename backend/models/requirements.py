"""
Data models for requirements and documents in the Healthcare Test Case Generation System
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, Enum as SQLEnum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

Base = declarative_base()


class RequirementType(str, Enum):
    """Types of requirements"""
    FUNCTIONAL = "functional"
    NON_FUNCTIONAL = "non_functional"
    SECURITY = "security"
    PERFORMANCE = "performance"
    USABILITY = "usability"
    INTERFACE = "interface"
    DATA = "data"
    COMPLIANCE = "compliance"
    BUSINESS = "business"


class RequirementPriority(str, Enum):
    """Priority levels for requirements"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ComplianceStandard(str, Enum):
    """Supported compliance standards"""
    FDA_21_CFR_820 = "fda_21_cfr_820"
    IEC_62304 = "iec_62304"
    ISO_9001 = "iso_9001"
    ISO_13485 = "iso_13485"
    ISO_27001 = "iso_27001"
    GDPR = "gdpr"


class DocumentStatus(str, Enum):
    """Document processing status"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    ARCHIVED = "archived"


# SQLAlchemy Models (Database)
class RequirementDocumentDB(Base):
    """Database model for requirement documents"""
    __tablename__ = "requirement_documents"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String, nullable=False)
    checksum = Column(String, nullable=False)
    
    # Document metadata
    title = Column(String, nullable=True)
    author = Column(String, nullable=True)
    subject = Column(String, nullable=True)
    creation_date = Column(DateTime, nullable=True)
    modification_date = Column(DateTime, nullable=True)
    page_count = Column(Integer, nullable=True)
    
    # Processing information
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.UPLOADED)
    processed_at = Column(DateTime, nullable=True)
    processing_duration = Column(Integer, nullable=True)  # in seconds
    error_message = Column(Text, nullable=True)
    
    # Compliance and metadata
    compliance_standards = Column(JSON, nullable=True)  # List of applicable standards
    tags = Column(JSON, nullable=True)  # List of tags
    metadata = Column(JSON, nullable=True)  # Additional metadata
    
    # Audit fields
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    
    # Relationships
    requirements = relationship("RequirementDB", back_populates="document", cascade="all, delete-orphan")


class RequirementDB(Base):
    """Database model for individual requirements"""
    __tablename__ = "requirements"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    requirement_id = Column(String, nullable=False, unique=True)  # Human-readable ID like REQ_0001
    text = Column(Text, nullable=False)
    type = Column(SQLEnum(RequirementType), nullable=False)
    priority = Column(SQLEnum(RequirementPriority), default=RequirementPriority.MEDIUM)
    
    # Source information
    document_id = Column(String, ForeignKey("requirement_documents.id"), nullable=False)
    section = Column(String, nullable=True)
    page_number = Column(Integer, nullable=True)
    line_number = Column(Integer, nullable=True)
    source_location = Column(JSON, nullable=True)  # Detailed location info
    
    # Content analysis
    keywords = Column(JSON, nullable=True)  # Extracted keywords
    entities = Column(JSON, nullable=True)  # Named entities
    complexity_score = Column(Integer, nullable=True)  # 1-10 complexity rating
    
    # Compliance mapping
    compliance_standards = Column(JSON, nullable=True)  # Applicable standards
    regulatory_references = Column(JSON, nullable=True)  # References to regulations
    risk_level = Column(String, nullable=True)  # High, Medium, Low
    
    # Relationships and traceability
    parent_requirement_id = Column(String, ForeignKey("requirements.id"), nullable=True)
    derived_requirements = relationship("RequirementDB", backref="parent_requirement", remote_side=[id])
    
    # Status and validation
    is_active = Column(Boolean, default=True)
    validation_status = Column(String, nullable=True)  # Valid, Invalid, Pending
    validation_notes = Column(Text, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    
    # Relationships
    document = relationship("RequirementDocumentDB", back_populates="requirements")
    test_cases = relationship("TestCaseDB", back_populates="requirement")


class TestCaseDB(Base):
    """Database model for generated test cases"""
    __tablename__ = "test_cases"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    test_case_id = Column(String, nullable=False, unique=True)  # Human-readable ID like TC_0001
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    
    # Test case details
    preconditions = Column(Text, nullable=True)
    test_steps = Column(JSON, nullable=False)  # List of test steps
    expected_results = Column(JSON, nullable=False)  # Expected results per step
    test_data = Column(JSON, nullable=True)  # Test data requirements
    
    # Classification
    test_type = Column(String, nullable=False)  # Functional, Security, Performance, etc.
    priority = Column(SQLEnum(RequirementPriority), default=RequirementPriority.MEDIUM)
    complexity = Column(String, nullable=True)  # Simple, Medium, Complex
    
    # Execution information
    estimated_duration = Column(Integer, nullable=True)  # in minutes
    automation_feasible = Column(Boolean, default=False)
    automation_complexity = Column(String, nullable=True)
    
    # Compliance and traceability
    requirement_id = Column(String, ForeignKey("requirements.id"), nullable=False)
    compliance_standards = Column(JSON, nullable=True)
    regulatory_references = Column(JSON, nullable=True)
    risk_coverage = Column(String, nullable=True)
    
    # Generation metadata
    generation_method = Column(String, nullable=False)  # AI, Template, Manual
    ai_confidence_score = Column(Integer, nullable=True)  # 1-100
    generation_notes = Column(Text, nullable=True)
    
    # Status and validation
    status = Column(String, default="draft")  # draft, reviewed, approved, obsolete
    validation_status = Column(String, nullable=True)
    review_notes = Column(Text, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    
    # Relationships
    requirement = relationship("RequirementDB", back_populates="test_cases")


# Pydantic Models (API)
class DocumentMetadata(BaseModel):
    """Document metadata model"""
    filename: str
    original_filename: str
    file_size: int
    mime_type: str
    checksum: str
    title: Optional[str] = None
    author: Optional[str] = None
    subject: Optional[str] = None
    creation_date: Optional[datetime] = None
    modification_date: Optional[datetime] = None
    page_count: Optional[int] = None


class SourceLocation(BaseModel):
    """Source location information"""
    section: Optional[str] = None
    page_number: Optional[int] = None
    line_number: Optional[int] = None
    additional_info: Optional[Dict[str, Any]] = None


class Requirement(BaseModel):
    """Requirement model for API"""
    id: str
    requirement_id: str
    text: str
    type: RequirementType
    priority: RequirementPriority = RequirementPriority.MEDIUM
    
    # Source information
    document_id: str
    section: Optional[str] = None
    source_location: Optional[SourceLocation] = None
    
    # Analysis results
    keywords: Optional[List[str]] = None
    entities: Optional[List[Dict[str, Any]]] = None
    complexity_score: Optional[int] = None
    
    # Compliance
    compliance_standards: Optional[List[ComplianceStandard]] = None
    regulatory_references: Optional[List[str]] = None
    risk_level: Optional[str] = None
    
    # Relationships
    parent_requirement_id: Optional[str] = None
    
    # Status
    is_active: bool = True
    validation_status: Optional[str] = None
    validation_notes: Optional[str] = None
    
    # Audit
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        from_attributes = True


class RequirementDocument(BaseModel):
    """Requirement document model for API"""
    id: str
    filename: str
    original_filename: str
    file_path: str
    metadata: DocumentMetadata
    
    # Processing information
    status: DocumentStatus
    processed_at: Optional[datetime] = None
    processing_duration: Optional[int] = None
    error_message: Optional[str] = None
    
    # Content
    requirements: Optional[List[Requirement]] = None
    
    # Compliance
    compliance_standards: Optional[List[ComplianceStandard]] = None
    tags: Optional[List[str]] = None
    
    # Audit
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        from_attributes = True


class TestStep(BaseModel):
    """Individual test step"""
    step_number: int
    description: str
    expected_result: str
    test_data: Optional[Dict[str, Any]] = None


class TestCase(BaseModel):
    """Test case model for API"""
    id: str
    test_case_id: str
    title: str
    description: str
    
    # Test details
    preconditions: Optional[str] = None
    test_steps: List[TestStep]
    test_data: Optional[Dict[str, Any]] = None
    
    # Classification
    test_type: str
    priority: RequirementPriority = RequirementPriority.MEDIUM
    complexity: Optional[str] = None
    
    # Execution
    estimated_duration: Optional[int] = None
    automation_feasible: bool = False
    automation_complexity: Optional[str] = None
    
    # Traceability
    requirement_id: str
    compliance_standards: Optional[List[ComplianceStandard]] = None
    regulatory_references: Optional[List[str]] = None
    risk_coverage: Optional[str] = None
    
    # Generation
    generation_method: str
    ai_confidence_score: Optional[int] = None
    generation_notes: Optional[str] = None
    
    # Status
    status: str = "draft"
    validation_status: Optional[str] = None
    review_notes: Optional[str] = None
    
    # Audit
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        from_attributes = True


# Request/Response Models
class DocumentUploadRequest(BaseModel):
    """Request model for document upload"""
    compliance_standards: Optional[List[ComplianceStandard]] = None
    tags: Optional[List[str]] = None
    auto_process: bool = True


class DocumentUploadResponse(BaseModel):
    """Response model for document upload"""
    document_id: str
    filename: str
    status: DocumentStatus
    message: str


class RequirementExtractionRequest(BaseModel):
    """Request model for requirement extraction"""
    document_id: str
    extraction_settings: Optional[Dict[str, Any]] = None
    compliance_standards: Optional[List[ComplianceStandard]] = None


class RequirementExtractionResponse(BaseModel):
    """Response model for requirement extraction"""
    document_id: str
    requirements_count: int
    requirements: List[Requirement]
    processing_time: float
    extraction_notes: Optional[str] = None


class TestCaseGenerationRequest(BaseModel):
    """Request model for test case generation"""
    requirement_ids: List[str]
    generation_settings: Optional[Dict[str, Any]] = None
    test_types: Optional[List[str]] = None
    compliance_standards: Optional[List[ComplianceStandard]] = None


class TestCaseGenerationResponse(BaseModel):
    """Response model for test case generation"""
    requirement_ids: List[str]
    test_cases_count: int
    test_cases: List[TestCase]
    processing_time: float
    generation_notes: Optional[str] = None


# Error Models
class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    details: Optional[str] = None
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ValidationError(BaseModel):
    """Validation error details"""
    field: str
    message: str
    value: Optional[Any] = None


class ValidationErrorResponse(ErrorResponse):
    """Validation error response"""
    validation_errors: List[ValidationError]