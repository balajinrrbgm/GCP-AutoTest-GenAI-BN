# Test suite initialization for Healthcare Test Case Generation System
"""
Test configuration and utilities for the Healthcare Test Case Generation System
"""

import pytest
import asyncio
import logging
from pathlib import Path
from unittest.mock import Mock
import tempfile
import os
import sys

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure test logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Test configuration
TEST_DATA_DIR = Path(__file__).parent / "data"
TEMP_DIR = Path(tempfile.gettempdir()) / "healthcare_testgen_tests"

# Create necessary directories
TEST_DATA_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_requirements():
    """Sample requirements for testing"""
    return [
        {
            "id": "REQ-001",
            "text": "The system shall authenticate users within 5 seconds using secure credentials",
            "priority": "HIGH",
            "category": "Authentication",
            "compliance_standards": ["IEC 62304", "ISO 27001"]
        },
        {
            "id": "REQ-002", 
            "text": "Patient data must be encrypted using AES-256 encryption at rest and in transit",
            "priority": "CRITICAL",
            "category": "Security",
            "compliance_standards": ["GDPR", "HIPAA", "ISO 27001"]
        },
        {
            "id": "REQ-003",
            "text": "The system shall generate audit logs for all user actions with timestamp and user ID",
            "priority": "MEDIUM",
            "category": "Auditing",
            "compliance_standards": ["FDA CFR 820", "ISO 9001"]
        }
    ]


@pytest.fixture
def sample_test_cases():
    """Sample test cases for testing"""
    return [
        {
            "id": "TC-001",
            "title": "Verify user authentication with valid credentials",
            "description": "Test that users can authenticate successfully with valid username and password",
            "requirement_id": "REQ-001",
            "priority": "HIGH",
            "steps": [
                "Navigate to login page",
                "Enter valid username",
                "Enter valid password", 
                "Click login button"
            ],
            "expected_result": "User is authenticated and redirected to dashboard within 5 seconds",
            "test_data": {"username": "testuser", "password": "TestPass123!"}
        },
        {
            "id": "TC-002",
            "title": "Verify data encryption at rest",
            "description": "Test that patient data is properly encrypted when stored in database",
            "requirement_id": "REQ-002",
            "priority": "CRITICAL",
            "steps": [
                "Create patient record with sensitive data",
                "Save record to database",
                "Inspect database storage directly",
                "Verify data is encrypted with AES-256"
            ],
            "expected_result": "Patient data is stored in encrypted format using AES-256",
            "test_data": {"patient_data": {"name": "John Doe", "ssn": "123-45-6789"}}
        }
    ]


@pytest.fixture
def mock_ai_service():
    """Mock AI service for testing"""
    mock = Mock()
    mock.generate_test_cases.return_value = {
        "test_cases": [
            {
                "title": "Generated test case",
                "description": "AI-generated test case description",
                "steps": ["Step 1", "Step 2", "Step 3"],
                "expected_result": "Expected outcome"
            }
        ]
    }
    return mock


@pytest.fixture
def temp_file():
    """Create a temporary file for testing"""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        yield Path(f.name)
    # Cleanup after test
    Path(f.name).unlink(missing_ok=True)


@pytest.fixture
def sample_documents():
    """Sample document content for testing"""
    return {
        "requirements_doc": """
# Healthcare Software Requirements

## Authentication Requirements
REQ-001: The system shall authenticate users within 5 seconds using secure credentials.
REQ-002: Failed login attempts shall be logged and limited to 3 attempts per hour.

## Security Requirements  
REQ-003: Patient data must be encrypted using AES-256 encryption at rest and in transit.
REQ-004: All data access shall be logged with user ID, timestamp, and action performed.

## Compliance Requirements
REQ-005: The system shall comply with FDA 21 CFR Part 820 quality system regulations.
REQ-006: All software components shall follow IEC 62304 medical device software lifecycle.
        """,
        
        "test_spec": """
# Test Specifications

## Test Case TC-001
**Title**: User Authentication Test
**Requirement**: REQ-001
**Priority**: High
**Description**: Verify user can authenticate with valid credentials
**Steps**:
1. Open login page
2. Enter valid username
3. Enter valid password
4. Click login
**Expected**: User authenticated within 5 seconds
        """
    }


# Test utilities
def create_mock_document(content: str, format: str = "txt") -> Path:
    """Create a mock document file for testing"""
    temp_file = TEMP_DIR / f"test_doc.{format}"
    temp_file.write_text(content, encoding='utf-8')
    return temp_file


def cleanup_test_files():
    """Clean up temporary test files"""
    import shutil
    if TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR)


# Pytest configuration
def pytest_configure(config):
    """Configure pytest"""
    # Add custom markers
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "ai_service: marks tests that require AI service"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )


def pytest_unconfigure(config):
    """Cleanup after all tests"""
    cleanup_test_files()


# Export test utilities
__all__ = [
    'TEST_DATA_DIR',
    'TEMP_DIR', 
    'create_mock_document',
    'cleanup_test_files'
]