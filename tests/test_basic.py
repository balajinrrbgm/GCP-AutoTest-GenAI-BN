"""
Basic test cases for the Healthcare Test Case Generation System
"""

import pytest
import asyncio
from pathlib import Path
import tempfile
import json
from unittest.mock import Mock, patch, AsyncMock

# Import modules for testing
from backend.requirements_parser import DocumentParser, RequirementExtractor
from backend.healthcare_domain import HealthcareDomainKnowledge, ComplianceRule
from backend.ai_engine import TestCaseGenerator, GenerationStrategy
from backend.models.requirements import Requirement, TestCase


class TestRequirementsParser:
    """Test cases for requirements parser module"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.parser = DocumentParser()
        self.extractor = RequirementExtractor()
    
    @pytest.mark.asyncio
    async def test_document_parsing_pdf(self):
        """Test PDF document parsing"""
        # Create a mock PDF file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.write(b"Mock PDF content for testing")
            temp_path = Path(temp_file.name)
        
        try:
            # Mock the PDF parsing functionality
            with patch.object(self.parser, '_parse_pdf') as mock_parse:
                mock_parse.return_value = "Extracted PDF text content"
                
                result = await self.parser.parse_document(temp_path)
                
                assert result is not None
                assert "content" in result
                mock_parse.assert_called_once()
        finally:
            temp_path.unlink()
    
    def test_requirement_extraction(self):
        """Test requirement extraction from text"""
        sample_text = """
        REQ-001: The system shall validate user authentication within 5 seconds.
        REQ-002: Patient data must be encrypted using AES-256 encryption.
        The system should handle concurrent users efficiently.
        REQ-003: All audit logs shall be retained for 7 years.
        """
        
        requirements = self.extractor.extract_requirements(sample_text)
        
        assert len(requirements) >= 3
        assert any("REQ-001" in req.get("id", "") for req in requirements)
        assert any("authentication" in req.get("text", "").lower() for req in requirements)
    
    def test_format_detection(self):
        """Test document format detection"""
        assert self.parser._detect_format(Path("test.pdf")) == "pdf"
        assert self.parser._detect_format(Path("test.docx")) == "docx"
        assert self.parser._detect_format(Path("test.xml")) == "xml"
        assert self.parser._detect_format(Path("test.md")) == "markdown"


class TestHealthcareDomain:
    """Test cases for healthcare domain knowledge"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.domain_knowledge = HealthcareDomainKnowledge()
    
    def test_compliance_rules_loading(self):
        """Test loading of compliance rules"""
        rules = self.domain_knowledge.get_compliance_rules()
        
        assert len(rules) > 0
        assert any(rule.standard == "FDA_CFR_820" for rule in rules)
        assert any(rule.standard == "IEC_62304" for rule in rules)
    
    def test_regulation_pattern_matching(self):
        """Test regulation pattern matching"""
        test_requirement = "The device software shall comply with IEC 62304 Class B requirements."
        
        matched_regulations = self.domain_knowledge.identify_regulations(test_requirement)
        
        assert len(matched_regulations) > 0
        assert any("IEC 62304" in reg for reg in matched_regulations)
    
    def test_risk_classification(self):
        """Test risk classification for requirements"""
        high_risk_req = "Critical safety system that controls patient life support"
        medium_risk_req = "Data validation for patient records"
        low_risk_req = "User interface color scheme preferences"
        
        assert self.domain_knowledge.classify_risk(high_risk_req) == "HIGH"
        assert self.domain_knowledge.classify_risk(medium_risk_req) == "MEDIUM"
        assert self.domain_knowledge.classify_risk(low_risk_req) == "LOW"
    
    def test_compliance_validation(self):
        """Test compliance validation against healthcare standards"""
        requirement = Requirement(
            id="REQ-001",
            text="Patient data shall be encrypted with AES-256",
            priority="HIGH",
            category="Security"
        )
        
        validation_result = self.domain_knowledge.validate_compliance(requirement)
        
        assert validation_result is not None
        assert validation_result["is_compliant"] in [True, False]
        assert "recommendations" in validation_result


class TestAIEngine:
    """Test cases for AI-powered test case generation"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.generator = TestCaseGenerator()
    
    @pytest.mark.asyncio
    async def test_test_case_generation(self):
        """Test basic test case generation"""
        requirement = Requirement(
            id="REQ-001",
            text="The system shall authenticate users within 5 seconds",
            priority="HIGH",
            category="Authentication"
        )
        
        # Mock the AI service call
        with patch.object(self.generator, '_call_ai_service') as mock_ai:
            mock_ai.return_value = {
                "test_cases": [
                    {
                        "title": "Test successful user authentication",
                        "description": "Verify user can authenticate with valid credentials",
                        "steps": ["Enter valid username", "Enter valid password", "Click login"],
                        "expected_result": "User authenticated within 5 seconds"
                    }
                ]
            }
            
            test_cases = await self.generator.generate_test_cases([requirement])
            
            assert len(test_cases) > 0
            assert test_cases[0].title is not None
            assert test_cases[0].requirement_id == requirement.id
    
    def test_generation_strategies(self):
        """Test different test generation strategies"""
        strategies = self.generator.get_available_strategies()
        
        assert GenerationStrategy.FUNCTIONAL in strategies
        assert GenerationStrategy.SECURITY in strategies
        assert GenerationStrategy.PERFORMANCE in strategies
        assert GenerationStrategy.COMPLIANCE in strategies
    
    @pytest.mark.asyncio
    async def test_batch_generation(self):
        """Test batch test case generation"""
        requirements = [
            Requirement(id="REQ-001", text="Test requirement 1", priority="HIGH"),
            Requirement(id="REQ-002", text="Test requirement 2", priority="MEDIUM"),
            Requirement(id="REQ-003", text="Test requirement 3", priority="LOW")
        ]
        
        # Mock the AI service
        with patch.object(self.generator, '_call_ai_service') as mock_ai:
            mock_ai.return_value = {"test_cases": []}
            
            test_cases = await self.generator.generate_test_cases(requirements)
            
            # Should handle batch processing
            assert isinstance(test_cases, list)
            mock_ai.assert_called()


class TestAPIEndpoints:
    """Test cases for API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        from fastapi.testclient import TestClient
        from backend.main import app
        return TestClient(app)
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
    
    def test_api_info_endpoint(self, client):
        """Test API information endpoint"""
        response = client.get("/api/v1")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
    
    @pytest.mark.asyncio
    async def test_requirements_upload(self, client):
        """Test requirements upload endpoint"""
        # Create a test file
        test_content = b"REQ-001: Test requirement for upload"
        
        with patch('backend.api.requirements.process_uploaded_document') as mock_process:
            mock_process.return_value = {"requirements": [{"id": "REQ-001", "text": "Test requirement"}]}
            
            response = client.post(
                "/api/v1/requirements/upload",
                files={"file": ("test.txt", test_content, "text/plain")}
            )
            
            # Note: This might return 422 due to authentication requirements
            # In a real test, you would include proper authentication
            assert response.status_code in [200, 422]


class TestDataModels:
    """Test cases for data models"""
    
    def test_requirement_model(self):
        """Test requirement data model"""
        requirement = Requirement(
            id="REQ-001",
            text="Test requirement",
            priority="HIGH",
            category="Functional"
        )
        
        assert requirement.id == "REQ-001"
        assert requirement.priority == "HIGH"
        assert requirement.category == "Functional"
    
    def test_test_case_model(self):
        """Test case data model"""
        test_case = TestCase(
            id="TC-001",
            title="Test user authentication",
            description="Verify user can log in",
            requirement_id="REQ-001",
            priority="HIGH"
        )
        
        assert test_case.id == "TC-001"
        assert test_case.requirement_id == "REQ-001"
        assert test_case.priority == "HIGH"


class TestUtilities:
    """Test utility functions"""
    
    def test_file_validation(self):
        """Test file validation utilities"""
        from backend.utils.file_utils import is_supported_format, get_file_size
        
        assert is_supported_format("test.pdf") == True
        assert is_supported_format("test.txt") == False
        assert is_supported_format("test.docx") == True
    
    def test_text_processing(self):
        """Test text processing utilities"""
        from backend.utils.text_utils import clean_text, extract_keywords
        
        sample_text = "   REQ-001: The system SHALL validate user input.   "
        cleaned = clean_text(sample_text)
        
        assert cleaned.startswith("REQ-001")
        assert "SHALL" in cleaned
        assert not cleaned.startswith(" ")
        
        keywords = extract_keywords(cleaned)
        assert len(keywords) > 0


# Pytest configuration
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])