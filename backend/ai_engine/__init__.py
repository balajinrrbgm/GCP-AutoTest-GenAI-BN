"""
AI-Powered Test Case Generation Engine using Google Gemini and Vertex AI

This module provides the core AI functionality for generating comprehensive,
compliant test cases from healthcare requirements.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import re
from enum import Enum

# Google AI imports
import vertexai
from vertexai.language_models import TextGenerationModel
from vertexai.preview.generative_models import GenerativeModel, Part
import google.generativeai as genai
from google.cloud import aiplatform

# Internal imports
from backend.models.requirements import (
    Requirement, TestCase, TestStep, RequirementType, 
    RequirementPriority, RegulatoryStandard
)
from backend.healthcare_domain import (
    analyze_healthcare_requirement, RiskLevel, DeviceClass
)
from backend.utils.exceptions import AIProcessingError
from config import (
    GOOGLE_CLOUD_PROJECT, VERTEX_AI_LOCATION, GEMINI_MODEL, AI_CONFIG
)

logger = logging.getLogger(__name__)


class TestCaseType(str, Enum):
    """Types of test cases that can be generated"""
    FUNCTIONAL = "functional"
    SECURITY = "security"
    PERFORMANCE = "performance"
    USABILITY = "usability"
    INTEGRATION = "integration"
    COMPLIANCE = "compliance"
    REGRESSION = "regression"
    ACCESSIBILITY = "accessibility"


class GenerationStrategy(str, Enum):
    """Test case generation strategies"""
    COMPREHENSIVE = "comprehensive"  # Generate all possible test cases
    RISK_BASED = "risk_based"       # Focus on high-risk scenarios
    COMPLIANCE_FOCUSED = "compliance_focused"  # Focus on regulatory compliance
    MINIMAL_VIABLE = "minimal_viable"  # Generate minimum required test cases


@dataclass
class GenerationSettings:
    """Settings for test case generation"""
    strategy: GenerationStrategy = GenerationStrategy.COMPREHENSIVE
    test_types: List[TestCaseType] = field(default_factory=lambda: [TestCaseType.FUNCTIONAL])
    compliance_standards: List[RegulatoryStandard] = field(default_factory=list)
    device_class: Optional[DeviceClass] = None
    max_test_cases_per_requirement: int = 5
    include_negative_tests: bool = True
    include_boundary_tests: bool = True
    include_security_tests: bool = True
    automation_preference: bool = False
    risk_threshold: RiskLevel = RiskLevel.MEDIUM
    custom_templates: Dict[str, str] = field(default_factory=dict)


@dataclass
class GenerationContext:
    """Context for test case generation"""
    requirement: Requirement
    domain_analysis: Dict[str, Any]
    related_requirements: List[Requirement] = field(default_factory=list)
    system_context: Optional[str] = None
    user_stories: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)


class TestCaseGenerator:
    """AI-powered test case generator"""
    
    def __init__(self, project_id: str = None, location: str = None):
        """
        Initialize the test case generator
        
        Args:
            project_id: Google Cloud project ID
            location: Vertex AI location
        """
        self.project_id = project_id or GOOGLE_CLOUD_PROJECT
        self.location = location or VERTEX_AI_LOCATION
        
        # Initialize AI models
        self.gemini_model = None
        self.text_generation_model = None
        
        # Test case templates
        self.templates = self._load_test_case_templates()
        
        # Prompt templates for different scenarios
        self.prompts = self._load_prompt_templates()
    
    async def initialize(self):
        """Initialize AI models and services"""
        try:
            # Initialize Vertex AI
            vertexai.init(project=self.project_id, location=self.location)
            
            # Initialize Gemini model
            self.gemini_model = GenerativeModel(GEMINI_MODEL)
            
            # Initialize text generation model (for fallback)
            self.text_generation_model = TextGenerationModel.from_pretrained("text-bison@latest")
            
            logger.info("AI models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI models: {str(e)}")
            raise AIProcessingError(f"AI initialization failed: {str(e)}")
    
    async def generate_test_cases(self, 
                                requirement: Requirement,
                                settings: GenerationSettings = None,
                                context: GenerationContext = None) -> List[TestCase]:
        """
        Generate test cases for a given requirement
        
        Args:
            requirement: The requirement to generate test cases for
            settings: Generation settings
            context: Additional context for generation
            
        Returns:
            List of generated test cases
        """
        if not self.gemini_model:
            await self.initialize()
        
        settings = settings or GenerationSettings()
        context = context or GenerationContext(requirement=requirement, domain_analysis={})
        
        try:
            # Perform domain analysis if not provided
            if not context.domain_analysis:
                context.domain_analysis = analyze_healthcare_requirement(requirement.text)
            
            # Generate test cases based on strategy
            test_cases = []
            
            if settings.strategy == GenerationStrategy.COMPREHENSIVE:
                test_cases = await self._generate_comprehensive_test_cases(requirement, settings, context)
            elif settings.strategy == GenerationStrategy.RISK_BASED:
                test_cases = await self._generate_risk_based_test_cases(requirement, settings, context)
            elif settings.strategy == GenerationStrategy.COMPLIANCE_FOCUSED:
                test_cases = await self._generate_compliance_test_cases(requirement, settings, context)
            else:
                test_cases = await self._generate_minimal_test_cases(requirement, settings, context)
            
            # Post-process and validate test cases
            validated_test_cases = await self._validate_and_refine_test_cases(test_cases, requirement, settings)
            
            logger.info(f"Generated {len(validated_test_cases)} test cases for requirement {requirement.requirement_id}")
            return validated_test_cases
            
        except Exception as e:
            logger.error(f"Error generating test cases: {str(e)}")
            raise AIProcessingError(f"Test case generation failed: {str(e)}")
    
    async def _generate_comprehensive_test_cases(self, 
                                               requirement: Requirement,
                                               settings: GenerationSettings,
                                               context: GenerationContext) -> List[TestCase]:
        """Generate comprehensive test cases covering all aspects"""
        test_cases = []
        
        # Generate functional test cases
        if TestCaseType.FUNCTIONAL in settings.test_types:
            functional_tests = await self._generate_functional_test_cases(requirement, settings, context)
            test_cases.extend(functional_tests)
        
        # Generate security test cases
        if TestCaseType.SECURITY in settings.test_types or settings.include_security_tests:
            security_tests = await self._generate_security_test_cases(requirement, settings, context)
            test_cases.extend(security_tests)
        
        # Generate performance test cases
        if TestCaseType.PERFORMANCE in settings.test_types:
            performance_tests = await self._generate_performance_test_cases(requirement, settings, context)
            test_cases.extend(performance_tests)
        
        # Generate compliance test cases
        if TestCaseType.COMPLIANCE in settings.test_types or settings.compliance_standards:
            compliance_tests = await self._generate_compliance_test_cases(requirement, settings, context)
            test_cases.extend(compliance_tests)
        
        # Generate negative test cases
        if settings.include_negative_tests:
            negative_tests = await self._generate_negative_test_cases(requirement, settings, context)
            test_cases.extend(negative_tests)
        
        # Generate boundary test cases
        if settings.include_boundary_tests:
            boundary_tests = await self._generate_boundary_test_cases(requirement, settings, context)
            test_cases.extend(boundary_tests)
        
        return test_cases
    
    async def _generate_functional_test_cases(self, 
                                            requirement: Requirement,
                                            settings: GenerationSettings,
                                            context: GenerationContext) -> List[TestCase]:
        """Generate functional test cases"""
        
        prompt = self._build_functional_test_prompt(requirement, settings, context)
        
        try:
            response = await self._call_gemini_model(prompt)
            test_cases = self._parse_test_cases_from_response(response, TestCaseType.FUNCTIONAL, requirement)
            return test_cases
            
        except Exception as e:
            logger.warning(f"Gemini model failed for functional tests: {str(e)}. Using fallback.")
            return await self._generate_fallback_functional_tests(requirement, settings, context)
    
    async def _generate_security_test_cases(self, 
                                          requirement: Requirement,
                                          settings: GenerationSettings,
                                          context: GenerationContext) -> List[TestCase]:
        """Generate security test cases"""
        
        # Only generate security tests if requirement has security implications
        domain_analysis = context.domain_analysis
        has_security_implications = (
            'AUTHENTICATION' in [p['pattern_id'] for p in domain_analysis.get('domain_patterns', [])] or
            any('security' in indicator.lower() for indicator in domain_analysis.get('risk_indicators', [])) or
            requirement.type == RequirementType.SECURITY
        )
        
        if not has_security_implications:
            return []
        
        prompt = self._build_security_test_prompt(requirement, settings, context)
        
        try:
            response = await self._call_gemini_model(prompt)
            test_cases = self._parse_test_cases_from_response(response, TestCaseType.SECURITY, requirement)
            return test_cases
            
        except Exception as e:
            logger.warning(f"Security test generation failed: {str(e)}")
            return []
    
    async def _generate_compliance_test_cases(self, 
                                            requirement: Requirement,
                                            settings: GenerationSettings,
                                            context: GenerationContext) -> List[TestCase]:
        """Generate compliance-specific test cases"""
        
        domain_analysis = context.domain_analysis
        applicable_standards = domain_analysis.get('applicable_standards', [])
        compliance_rules = domain_analysis.get('compliance_rules', [])
        
        if not applicable_standards and not settings.compliance_standards:
            return []
        
        prompt = self._build_compliance_test_prompt(requirement, settings, context, applicable_standards, compliance_rules)
        
        try:
            response = await self._call_gemini_model(prompt)
            test_cases = self._parse_test_cases_from_response(response, TestCaseType.COMPLIANCE, requirement)
            return test_cases
            
        except Exception as e:
            logger.warning(f"Compliance test generation failed: {str(e)}")
            return []
    
    async def _generate_performance_test_cases(self, 
                                             requirement: Requirement,
                                             settings: GenerationSettings,
                                             context: GenerationContext) -> List[TestCase]:
        """Generate performance test cases"""
        
        # Check if requirement has performance implications
        has_performance_implications = (
            requirement.type == RequirementType.PERFORMANCE or
            any(keyword in requirement.text.lower() for keyword in 
                ['performance', 'speed', 'time', 'response', 'latency', 'throughput'])
        )
        
        if not has_performance_implications:
            return []
        
        prompt = self._build_performance_test_prompt(requirement, settings, context)
        
        try:
            response = await self._call_gemini_model(prompt)
            test_cases = self._parse_test_cases_from_response(response, TestCaseType.PERFORMANCE, requirement)
            return test_cases
            
        except Exception as e:
            logger.warning(f"Performance test generation failed: {str(e)}")
            return []
    
    async def _generate_negative_test_cases(self, 
                                          requirement: Requirement,
                                          settings: GenerationSettings,
                                          context: GenerationContext) -> List[TestCase]:
        """Generate negative test cases"""
        
        prompt = self._build_negative_test_prompt(requirement, settings, context)
        
        try:
            response = await self._call_gemini_model(prompt)
            test_cases = self._parse_test_cases_from_response(response, TestCaseType.FUNCTIONAL, requirement)
            
            # Mark as negative tests
            for test_case in test_cases:
                test_case.description += " (Negative Test)"
                test_case.test_type = "negative_functional"
            
            return test_cases
            
        except Exception as e:
            logger.warning(f"Negative test generation failed: {str(e)}")
            return []
    
    async def _generate_boundary_test_cases(self, 
                                          requirement: Requirement,
                                          settings: GenerationSettings,
                                          context: GenerationContext) -> List[TestCase]:
        """Generate boundary test cases"""
        
        # Extract boundary values from requirement text
        boundary_patterns = [
            r'(\d+)\s*(?:to|through|-)\s*(\d+)',
            r'(?:maximum|max|minimum|min)\s*(?:of\s*)?(\d+)',
            r'(?:at least|at most)\s*(\d+)',
            r'(?:between|from)\s*(\d+)\s*(?:and|to)\s*(\d+)'
        ]
        
        has_boundaries = any(re.search(pattern, requirement.text, re.IGNORECASE) 
                           for pattern in boundary_patterns)
        
        if not has_boundaries:
            return []
        
        prompt = self._build_boundary_test_prompt(requirement, settings, context)
        
        try:
            response = await self._call_gemini_model(prompt)
            test_cases = self._parse_test_cases_from_response(response, TestCaseType.FUNCTIONAL, requirement)
            
            # Mark as boundary tests
            for test_case in test_cases:
                test_case.description += " (Boundary Test)"
                test_case.test_type = "boundary_functional"
            
            return test_cases
            
        except Exception as e:
            logger.warning(f"Boundary test generation failed: {str(e)}")
            return []
    
    async def _generate_risk_based_test_cases(self, 
                                            requirement: Requirement,
                                            settings: GenerationSettings,
                                            context: GenerationContext) -> List[TestCase]:
        """Generate test cases based on risk assessment"""
        
        domain_analysis = context.domain_analysis
        risk_level = domain_analysis.get('risk_level', RiskLevel.MEDIUM)
        
        # Focus on high-risk scenarios
        if risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
            # Generate comprehensive tests for high-risk requirements
            settings.test_types = [TestCaseType.FUNCTIONAL, TestCaseType.SECURITY, TestCaseType.COMPLIANCE]
            settings.include_negative_tests = True
            settings.include_boundary_tests = True
            return await self._generate_comprehensive_test_cases(requirement, settings, context)
        else:
            # Generate minimal tests for low-risk requirements
            return await self._generate_minimal_test_cases(requirement, settings, context)
    
    async def _generate_minimal_test_cases(self, 
                                         requirement: Requirement,
                                         settings: GenerationSettings,
                                         context: GenerationContext) -> List[TestCase]:
        """Generate minimal viable test cases"""
        
        # Generate only essential functional tests
        prompt = self._build_minimal_test_prompt(requirement, settings, context)
        
        try:
            response = await self._call_gemini_model(prompt)
            test_cases = self._parse_test_cases_from_response(response, TestCaseType.FUNCTIONAL, requirement)
            
            # Limit to maximum 2 test cases
            return test_cases[:2]
            
        except Exception as e:
            logger.warning(f"Minimal test generation failed: {str(e)}")
            return await self._generate_fallback_functional_tests(requirement, settings, context)
    
    async def _call_gemini_model(self, prompt: str) -> str:
        """Call Gemini model with the given prompt"""
        try:
            response = await self.gemini_model.generate_content_async(
                prompt,
                generation_config={
                    "max_output_tokens": AI_CONFIG.get("max_tokens", 8192),
                    "temperature": AI_CONFIG.get("temperature", 0.1),
                    "top_p": AI_CONFIG.get("top_p", 0.8),
                },
                safety_settings=AI_CONFIG.get("safety_settings", [])
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini model call failed: {str(e)}")
            # Fallback to text generation model
            try:
                response = self.text_generation_model.predict(
                    prompt,
                    max_output_tokens=AI_CONFIG.get("max_tokens", 2048),
                    temperature=AI_CONFIG.get("temperature", 0.1)
                )
                return response.text
            except Exception as fallback_e:
                logger.error(f"Fallback model also failed: {str(fallback_e)}")
                raise AIProcessingError(f"All AI models failed: {str(e)}")
    
    def _parse_test_cases_from_response(self, 
                                      response: str, 
                                      test_type: TestCaseType,
                                      requirement: Requirement) -> List[TestCase]:
        """Parse test cases from AI model response"""
        test_cases = []
        
        try:
            # Try to parse as JSON first
            if response.strip().startswith('{') or response.strip().startswith('['):
                json_data = json.loads(response)
                if isinstance(json_data, list):
                    for item in json_data:
                        test_case = self._create_test_case_from_dict(item, test_type, requirement)
                        if test_case:
                            test_cases.append(test_case)
                elif isinstance(json_data, dict) and 'test_cases' in json_data:
                    for item in json_data['test_cases']:
                        test_case = self._create_test_case_from_dict(item, test_type, requirement)
                        if test_case:
                            test_cases.append(test_case)
            else:
                # Parse structured text response
                test_cases = self._parse_structured_text_response(response, test_type, requirement)
        
        except json.JSONDecodeError:
            # Parse as structured text
            test_cases = self._parse_structured_text_response(response, test_type, requirement)
        
        except Exception as e:
            logger.warning(f"Error parsing test cases: {str(e)}")
            # Create a basic test case as fallback
            test_cases = [self._create_basic_test_case(requirement, test_type)]
        
        return test_cases
    
    def _create_test_case_from_dict(self, 
                                  data: Dict[str, Any], 
                                  test_type: TestCaseType,
                                  requirement: Requirement) -> Optional[TestCase]:
        """Create a TestCase object from dictionary data"""
        try:
            # Extract test steps
            test_steps = []
            steps_data = data.get('test_steps', data.get('steps', []))
            
            if isinstance(steps_data, list):
                for i, step in enumerate(steps_data):
                    if isinstance(step, dict):
                        test_steps.append(TestStep(
                            step_number=i + 1,
                            description=step.get('description', step.get('action', '')),
                            expected_result=step.get('expected_result', step.get('expected', ''))
                        ))
                    else:
                        test_steps.append(TestStep(
                            step_number=i + 1,
                            description=str(step),
                            expected_result="As specified in requirement"
                        ))
            
            # Create test case
            test_case = TestCase(
                id=f"TC_{requirement.requirement_id}_{len(test_steps)}",
                test_case_id=f"TC_{requirement.requirement_id}_{test_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                title=data.get('title', f"Test {requirement.requirement_id}"),
                description=data.get('description', f"Test case for {requirement.requirement_id}"),
                preconditions=data.get('preconditions'),
                test_steps=test_steps,
                test_type=test_type.value,
                requirement_id=requirement.id,
                generation_method="AI_Generated",
                ai_confidence_score=data.get('confidence_score', 80),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            return test_case
            
        except Exception as e:
            logger.warning(f"Error creating test case from dict: {str(e)}")
            return None
    
    def _parse_structured_text_response(self, 
                                      response: str, 
                                      test_type: TestCaseType,
                                      requirement: Requirement) -> List[TestCase]:
        """Parse structured text response into test cases"""
        test_cases = []
        
        # Split response into test case sections
        test_case_sections = re.split(r'(?:^|\n)(?:Test Case \d+|TC\d+|Test \d+):', response, flags=re.MULTILINE)
        
        for i, section in enumerate(test_case_sections[1:], 1):  # Skip first empty section
            try:
                # Extract title
                title_match = re.search(r'^([^\n]+)', section.strip())
                title = title_match.group(1).strip() if title_match else f"Test Case {i}"
                
                # Extract description
                desc_match = re.search(r'(?:Description|Summary):\s*([^\n]+)', section, re.IGNORECASE)
                description = desc_match.group(1).strip() if desc_match else title
                
                # Extract preconditions
                precond_match = re.search(r'(?:Preconditions|Prerequisites):\s*([^\n]+)', section, re.IGNORECASE)
                preconditions = precond_match.group(1).strip() if precond_match else None
                
                # Extract test steps
                steps_section = re.search(r'(?:Steps|Test Steps):\s*(.*?)(?=(?:Expected|Result|$))', section, re.IGNORECASE | re.DOTALL)
                test_steps = []
                
                if steps_section:
                    steps_text = steps_section.group(1)
                    step_lines = [line.strip() for line in steps_text.split('\n') if line.strip()]
                    
                    for j, step_line in enumerate(step_lines):
                        # Remove numbering if present
                        step_line = re.sub(r'^\d+\.\s*', '', step_line)
                        if step_line:
                            test_steps.append(TestStep(
                                step_number=j + 1,
                                description=step_line,
                                expected_result="As specified in requirement"
                            ))
                
                # Create test case
                if test_steps:  # Only create if we have steps
                    test_case = TestCase(
                        id=f"TC_{requirement.requirement_id}_{i}",
                        test_case_id=f"TC_{requirement.requirement_id}_{test_type.value}_{i}",
                        title=title,
                        description=description,
                        preconditions=preconditions,
                        test_steps=test_steps,
                        test_type=test_type.value,
                        requirement_id=requirement.id,
                        generation_method="AI_Generated",
                        ai_confidence_score=75,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    test_cases.append(test_case)
            
            except Exception as e:
                logger.warning(f"Error parsing test case section {i}: {str(e)}")
                continue
        
        return test_cases
    
    def _create_basic_test_case(self, 
                              requirement: Requirement, 
                              test_type: TestCaseType) -> TestCase:
        """Create a basic test case as fallback"""
        
        basic_steps = [
            TestStep(
                step_number=1,
                description=f"Verify that the system implements: {requirement.text[:100]}...",
                expected_result="System behaves according to requirement specification"
            )
        ]
        
        return TestCase(
            id=f"TC_{requirement.requirement_id}_basic",
            test_case_id=f"TC_{requirement.requirement_id}_{test_type.value}_basic",
            title=f"Basic Test for {requirement.requirement_id}",
            description=f"Basic test case generated for requirement {requirement.requirement_id}",
            test_steps=basic_steps,
            test_type=test_type.value,
            requirement_id=requirement.id,
            generation_method="Fallback_Generated",
            ai_confidence_score=50,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    
    async def _generate_fallback_functional_tests(self, 
                                                requirement: Requirement,
                                                settings: GenerationSettings,
                                                context: GenerationContext) -> List[TestCase]:
        """Generate fallback functional test cases using templates"""
        
        test_cases = []
        
        # Use basic template-based generation
        if requirement.type == RequirementType.FUNCTIONAL:
            template = self.templates.get('functional_basic', self.templates['default'])
        else:
            template = self.templates.get(requirement.type.value, self.templates['default'])
        
        # Create test case using template
        test_case = self._apply_template(template, requirement, TestCaseType.FUNCTIONAL)
        test_cases.append(test_case)
        
        return test_cases
    
    def _apply_template(self, 
                       template: Dict[str, Any], 
                       requirement: Requirement,
                       test_type: TestCaseType) -> TestCase:
        """Apply a test case template to generate a test case"""
        
        # Replace placeholders in template
        title = template['title'].replace('{requirement_id}', requirement.requirement_id)
        description = template['description'].replace('{requirement_text}', requirement.text[:200])
        
        # Create test steps from template
        test_steps = []
        for i, step_template in enumerate(template['steps']):
            step_desc = step_template['description'].replace('{requirement_text}', requirement.text)
            step_expected = step_template['expected_result']
            
            test_steps.append(TestStep(
                step_number=i + 1,
                description=step_desc,
                expected_result=step_expected
            ))
        
        return TestCase(
            id=f"TC_{requirement.requirement_id}_template",
            test_case_id=f"TC_{requirement.requirement_id}_{test_type.value}_template",
            title=title,
            description=description,
            test_steps=test_steps,
            test_type=test_type.value,
            requirement_id=requirement.id,
            generation_method="Template_Generated",
            ai_confidence_score=60,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    
    async def _validate_and_refine_test_cases(self, 
                                            test_cases: List[TestCase],
                                            requirement: Requirement,
                                            settings: GenerationSettings) -> List[TestCase]:
        """Validate and refine generated test cases"""
        
        validated_cases = []
        
        for test_case in test_cases:
            # Basic validation
            if self._validate_test_case(test_case, requirement):
                # Refine test case
                refined_case = await self._refine_test_case(test_case, requirement, settings)
                validated_cases.append(refined_case)
        
        # Limit number of test cases if specified
        if settings.max_test_cases_per_requirement > 0:
            validated_cases = validated_cases[:settings.max_test_cases_per_requirement]
        
        return validated_cases
    
    def _validate_test_case(self, test_case: TestCase, requirement: Requirement) -> bool:
        """Validate a test case"""
        
        # Check required fields
        if not test_case.title or not test_case.description:
            return False
        
        # Check test steps
        if not test_case.test_steps or len(test_case.test_steps) == 0:
            return False
        
        # Check that steps have descriptions and expected results
        for step in test_case.test_steps:
            if not step.description or not step.expected_result:
                return False
        
        return True
    
    async def _refine_test_case(self, 
                              test_case: TestCase,
                              requirement: Requirement,
                              settings: GenerationSettings) -> TestCase:
        """Refine and enhance a test case"""
        
        # Add compliance information if applicable
        if settings.compliance_standards:
            test_case.compliance_standards = settings.compliance_standards
        
        # Set automation feasibility
        test_case.automation_feasible = self._assess_automation_feasibility(test_case)
        
        # Estimate duration
        test_case.estimated_duration = self._estimate_test_duration(test_case)
        
        # Set priority based on requirement priority
        test_case.priority = requirement.priority
        
        return test_case
    
    def _assess_automation_feasibility(self, test_case: TestCase) -> bool:
        """Assess if a test case can be automated"""
        
        # Simple heuristics for automation feasibility
        manual_indicators = [
            'manually', 'visual', 'observe', 'check appearance', 
            'verify display', 'user experience', 'usability'
        ]
        
        test_text = f"{test_case.description} {' '.join([step.description for step in test_case.test_steps])}"
        test_text_lower = test_text.lower()
        
        # If contains manual indicators, likely not automatable
        if any(indicator in test_text_lower for indicator in manual_indicators):
            return False
        
        # If contains API, data, or system interaction terms, likely automatable
        automation_indicators = [
            'api', 'database', 'system', 'calculate', 'process', 
            'validate', 'verify data', 'check result'
        ]
        
        if any(indicator in test_text_lower for indicator in automation_indicators):
            return True
        
        # Default to potentially automatable
        return True
    
    def _estimate_test_duration(self, test_case: TestCase) -> int:
        """Estimate test execution duration in minutes"""
        
        # Base duration
        duration = 5  # 5 minutes base
        
        # Add time per test step
        duration += len(test_case.test_steps) * 2
        
        # Add time for complex operations
        complex_keywords = ['setup', 'configuration', 'installation', 'complex', 'integration']
        test_text = f"{test_case.description} {' '.join([step.description for step in test_case.test_steps])}"
        
        complexity_count = sum(1 for keyword in complex_keywords if keyword in test_text.lower())
        duration += complexity_count * 5
        
        # Cap at reasonable maximum
        return min(duration, 60)
    
    def _load_test_case_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load test case templates"""
        
        return {
            'default': {
                'title': 'Test Case for {requirement_id}',
                'description': 'Verify requirement: {requirement_text}',
                'steps': [
                    {
                        'description': 'Execute the functionality described in: {requirement_text}',
                        'expected_result': 'System behaves according to requirement'
                    }
                ]
            },
            'functional_basic': {
                'title': 'Functional Test for {requirement_id}',
                'description': 'Verify functional behavior: {requirement_text}',
                'steps': [
                    {
                        'description': 'Prepare test environment and data',
                        'expected_result': 'Test environment is ready'
                    },
                    {
                        'description': 'Execute the required functionality',
                        'expected_result': 'Function executes successfully'
                    },
                    {
                        'description': 'Verify the expected outcome',
                        'expected_result': 'Results match requirement specification'
                    }
                ]
            }
        }
    
    def _load_prompt_templates(self) -> Dict[str, str]:
        """Load prompt templates for different test case types"""
        
        return {
            'functional': """
Generate comprehensive functional test cases for the following healthcare software requirement:

Requirement: {requirement_text}
Requirement Type: {requirement_type}
Priority: {priority}

Domain Analysis:
{domain_analysis}

Generate test cases that:
1. Verify the core functionality described in the requirement
2. Include positive test scenarios
3. Cover edge cases and boundary conditions
4. Ensure healthcare compliance where applicable
5. Include clear, step-by-step test procedures

Return the response in JSON format with the following structure:
{{
  "test_cases": [
    {{
      "title": "Test case title",
      "description": "Test case description",
      "preconditions": "Any prerequisites",
      "test_steps": [
        {{
          "description": "Step description",
          "expected_result": "Expected outcome"
        }}
      ],
      "confidence_score": 85
    }}
  ]
}}
""",
            
            'security': """
Generate security test cases for the following healthcare software requirement:

Requirement: {requirement_text}
Security Implications: {security_analysis}

Focus on:
1. Authentication and authorization tests
2. Data protection and privacy tests
3. Access control verification
4. Security boundary testing
5. HIPAA/GDPR compliance where applicable

Generate detailed test cases in JSON format.
""",
            
            'compliance': """
Generate compliance test cases for the following healthcare requirement:

Requirement: {requirement_text}
Applicable Standards: {compliance_standards}
Compliance Rules: {compliance_rules}

Generate test cases that verify:
1. Regulatory compliance requirements
2. Standard-specific validation points
3. Audit trail requirements
4. Documentation compliance
5. Traceability verification

Return detailed test cases in JSON format.
""",
            
            'minimal': """
Generate the most essential test case for the following requirement:

Requirement: {requirement_text}

Generate ONE comprehensive test case that covers the core functionality.
Keep it simple but complete. Return in JSON format.
"""
        }
    
    def _build_functional_test_prompt(self, 
                                    requirement: Requirement,
                                    settings: GenerationSettings,
                                    context: GenerationContext) -> str:
        """Build prompt for functional test generation"""
        
        template = self.prompts['functional']
        
        return template.format(
            requirement_text=requirement.text,
            requirement_type=requirement.type.value,
            priority=requirement.priority.value,
            domain_analysis=json.dumps(context.domain_analysis, indent=2)
        )
    
    def _build_security_test_prompt(self, 
                                  requirement: Requirement,
                                  settings: GenerationSettings,
                                  context: GenerationContext) -> str:
        """Build prompt for security test generation"""
        
        template = self.prompts['security']
        
        security_analysis = {
            'risk_level': context.domain_analysis.get('risk_level'),
            'risk_indicators': context.domain_analysis.get('risk_indicators', []),
            'security_patterns': [p for p in context.domain_analysis.get('domain_patterns', []) 
                                if 'security' in p.get('name', '').lower()]
        }
        
        return template.format(
            requirement_text=requirement.text,
            security_analysis=json.dumps(security_analysis, indent=2)
        )
    
    def _build_compliance_test_prompt(self, 
                                    requirement: Requirement,
                                    settings: GenerationSettings,
                                    context: GenerationContext,
                                    applicable_standards: List[str],
                                    compliance_rules: List[Dict]) -> str:
        """Build prompt for compliance test generation"""
        
        template = self.prompts['compliance']
        
        return template.format(
            requirement_text=requirement.text,
            compliance_standards=', '.join(applicable_standards),
            compliance_rules=json.dumps(compliance_rules, indent=2)
        )
    
    def _build_performance_test_prompt(self, 
                                     requirement: Requirement,
                                     settings: GenerationSettings,
                                     context: GenerationContext) -> str:
        """Build prompt for performance test generation"""
        
        return f"""
Generate performance test cases for: {requirement.text}

Focus on:
1. Response time requirements
2. Throughput testing
3. Load testing scenarios
4. Stress testing conditions
5. Performance benchmarks

Return detailed test cases in JSON format.
"""
    
    def _build_negative_test_prompt(self, 
                                  requirement: Requirement,
                                  settings: GenerationSettings,
                                  context: GenerationContext) -> str:
        """Build prompt for negative test generation"""
        
        return f"""
Generate negative test cases for: {requirement.text}

Focus on:
1. Invalid input scenarios
2. Error condition testing
3. Boundary violation tests
4. Exception handling verification
5. Failure mode testing

Return detailed test cases in JSON format.
"""
    
    def _build_boundary_test_prompt(self, 
                                  requirement: Requirement,
                                  settings: GenerationSettings,
                                  context: GenerationContext) -> str:
        """Build prompt for boundary test generation"""
        
        return f"""
Generate boundary test cases for: {requirement.text}

Focus on:
1. Minimum and maximum value testing
2. Edge case scenarios
3. Boundary condition verification
4. Limit testing
5. Range validation

Return detailed test cases in JSON format.
"""
    
    def _build_minimal_test_prompt(self, 
                                 requirement: Requirement,
                                 settings: GenerationSettings,
                                 context: GenerationContext) -> str:
        """Build prompt for minimal test generation"""
        
        template = self.prompts['minimal']
        
        return template.format(
            requirement_text=requirement.text
        )


# Initialize global test case generator
test_case_generator = TestCaseGenerator()


async def generate_test_cases_for_requirement(requirement: Requirement,
                                            settings: GenerationSettings = None) -> List[TestCase]:
    """
    Generate test cases for a requirement
    
    Args:
        requirement: The requirement to generate test cases for
        settings: Generation settings
        
    Returns:
        List of generated test cases
    """
    return await test_case_generator.generate_test_cases(requirement, settings)


async def init_ai_services():
    """Initialize AI services"""
    await test_case_generator.initialize()


async def cleanup_ai_services():
    """Cleanup AI services"""
    # Cleanup if needed
    pass


# Export main components
__all__ = [
    'TestCaseGenerator',
    'TestCaseType',
    'GenerationStrategy',
    'GenerationSettings',
    'GenerationContext',
    'generate_test_cases_for_requirement',
    'init_ai_services',
    'cleanup_ai_services'
]