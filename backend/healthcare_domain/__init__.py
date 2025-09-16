"""
Healthcare Domain Knowledge Engine for Test Case Generation System

This module contains specialized knowledge about healthcare regulations, standards,
and domain-specific patterns to guide AI-powered test case generation.
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re
from pathlib import Path

logger = logging.getLogger(__name__)


class RegulatoryStandard(str, Enum):
    """Supported regulatory standards"""
    FDA_21_CFR_820 = "fda_21_cfr_820"
    IEC_62304 = "iec_62304"
    ISO_9001 = "iso_9001"
    ISO_13485 = "iso_13485"
    ISO_27001 = "iso_27001"
    GDPR = "gdpr"
    HIPAA = "hipaa"
    MDR = "mdr"  # Medical Device Regulation (EU)


class RiskLevel(str, Enum):
    """Risk levels for healthcare requirements"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class DeviceClass(str, Enum):
    """Medical device classification"""
    CLASS_I = "class_i"
    CLASS_II = "class_ii"
    CLASS_III = "class_iii"
    IVD = "ivd"  # In Vitro Diagnostic


@dataclass
class ComplianceRule:
    """Individual compliance rule"""
    id: str
    standard: RegulatoryStandard
    section: str
    title: str
    description: str
    requirements: List[str]
    test_patterns: List[str] = field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.MEDIUM
    applicable_device_classes: List[DeviceClass] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)


@dataclass
class DomainPattern:
    """Healthcare domain-specific pattern"""
    pattern_id: str
    name: str
    description: str
    regex_patterns: List[str]
    test_case_templates: List[str]
    risk_indicators: List[str] = field(default_factory=list)
    compliance_mapping: Dict[RegulatoryStandard, List[str]] = field(default_factory=dict)


class HealthcareDomainKnowledge:
    """Healthcare domain knowledge engine"""
    
    def __init__(self):
        self.compliance_rules: Dict[RegulatoryStandard, List[ComplianceRule]] = {}
        self.domain_patterns: Dict[str, DomainPattern] = {}
        self.risk_keywords: Dict[RiskLevel, List[str]] = {}
        self.device_specific_rules: Dict[DeviceClass, List[str]] = {}
        
        # Initialize knowledge base
        self._initialize_compliance_rules()
        self._initialize_domain_patterns()
        self._initialize_risk_assessment()
        self._initialize_device_classifications()
    
    def _initialize_compliance_rules(self):
        """Initialize compliance rules for healthcare standards"""
        
        # FDA 21 CFR Part 820 - Quality System Regulation
        fda_rules = [
            ComplianceRule(
                id="FDA_820_70",
                standard=RegulatoryStandard.FDA_21_CFR_820,
                section="820.70",
                title="Production and Process Controls",
                description="Production and process controls for medical devices",
                requirements=[
                    "Each manufacturer shall develop, conduct, control, and monitor production processes",
                    "Production processes shall be validated where the results cannot be verified by inspection and test",
                    "Process validation shall include qualification of production equipment"
                ],
                test_patterns=[
                    "Verify production process validation",
                    "Test equipment qualification procedures",
                    "Validate process monitoring controls"
                ],
                risk_level=RiskLevel.HIGH,
                keywords=["production", "process", "validation", "equipment", "qualification"]
            ),
            ComplianceRule(
                id="FDA_820_30",
                standard=RegulatoryStandard.FDA_21_CFR_820,
                section="820.30",
                title="Design Controls",
                description="Design controls for medical device development",
                requirements=[
                    "Design and development planning shall be documented",
                    "Design input requirements shall be documented and reviewed",
                    "Design output shall be documented and reviewed"
                ],
                test_patterns=[
                    "Verify design planning documentation",
                    "Test design input requirements",
                    "Validate design output specifications"
                ],
                risk_level=RiskLevel.CRITICAL,
                keywords=["design", "development", "planning", "input", "output"]
            )
        ]
        
        # IEC 62304 - Medical Device Software Life Cycle Processes
        iec_62304_rules = [
            ComplianceRule(
                id="IEC_62304_5_1",
                standard=RegulatoryStandard.IEC_62304,
                section="5.1",
                title="Software Development Planning",
                description="Software development planning process",
                requirements=[
                    "Software development plan shall be documented",
                    "Plan shall describe software life cycle activities",
                    "Plan shall identify standards, methods and tools"
                ],
                test_patterns=[
                    "Verify software development plan completeness",
                    "Test life cycle activity documentation",
                    "Validate standards compliance"
                ],
                risk_level=RiskLevel.HIGH,
                keywords=["software", "development", "planning", "life cycle", "documentation"]
            ),
            ComplianceRule(
                id="IEC_62304_5_5",
                standard=RegulatoryStandard.IEC_62304,
                section="5.5",
                title="Software Integration and Testing",
                description="Software integration and integration testing",
                requirements=[
                    "Integration tests shall be conducted",
                    "Test procedures shall be documented",
                    "Test results shall be documented and evaluated"
                ],
                test_patterns=[
                    "Execute integration test procedures",
                    "Verify test documentation completeness",
                    "Validate test results evaluation"
                ],
                risk_level=RiskLevel.CRITICAL,
                keywords=["integration", "testing", "procedures", "documentation", "results"]
            )
        ]
        
        # ISO 13485 - Medical Device Quality Management
        iso_13485_rules = [
            ComplianceRule(
                id="ISO_13485_7_3",
                standard=RegulatoryStandard.ISO_13485,
                section="7.3",
                title="Design and Development",
                description="Design and development requirements",
                requirements=[
                    "Design and development shall be planned and controlled",
                    "Design inputs shall be determined and documented",
                    "Design outputs shall be documented and verified"
                ],
                test_patterns=[
                    "Verify design control processes",
                    "Test design input documentation",
                    "Validate design output verification"
                ],
                risk_level=RiskLevel.HIGH,
                keywords=["design", "development", "planning", "control", "verification"]
            )
        ]
        
        # ISO 27001 - Information Security Management
        iso_27001_rules = [
            ComplianceRule(
                id="ISO_27001_A_9_1",
                standard=RegulatoryStandard.ISO_27001,
                section="A.9.1",
                title="Access Control Policy",
                description="Access control and user access management",
                requirements=[
                    "Access control policy shall be documented",
                    "User access shall be managed and reviewed",
                    "Privileged access rights shall be controlled"
                ],
                test_patterns=[
                    "Verify access control policy implementation",
                    "Test user access management procedures",
                    "Validate privileged access controls"
                ],
                risk_level=RiskLevel.CRITICAL,
                keywords=["access", "control", "policy", "user", "privileges"]
            )
        ]
        
        # GDPR - Data Protection
        gdpr_rules = [
            ComplianceRule(
                id="GDPR_ART_25",
                standard=RegulatoryStandard.GDPR,
                section="Article 25",
                title="Data Protection by Design and by Default",
                description="Privacy by design requirements",
                requirements=[
                    "Data protection shall be implemented by design",
                    "Only necessary personal data shall be processed",
                    "Data protection measures shall be integrated into processing"
                ],
                test_patterns=[
                    "Verify privacy by design implementation",
                    "Test data minimization controls",
                    "Validate data protection integration"
                ],
                risk_level=RiskLevel.CRITICAL,
                keywords=["privacy", "design", "data protection", "personal data", "minimization"]
            )
        ]
        
        # Store rules by standard
        self.compliance_rules[RegulatoryStandard.FDA_21_CFR_820] = fda_rules
        self.compliance_rules[RegulatoryStandard.IEC_62304] = iec_62304_rules
        self.compliance_rules[RegulatoryStandard.ISO_13485] = iso_13485_rules
        self.compliance_rules[RegulatoryStandard.ISO_27001] = iso_27001_rules
        self.compliance_rules[RegulatoryStandard.GDPR] = gdpr_rules
    
    def _initialize_domain_patterns(self):
        """Initialize healthcare domain-specific patterns"""
        
        # Patient Safety Pattern
        patient_safety = DomainPattern(
            pattern_id="PATIENT_SAFETY",
            name="Patient Safety Requirements",
            description="Patterns for patient safety-related requirements",
            regex_patterns=[
                r"patient\s+safety",
                r"harm\s+to\s+patient",
                r"adverse\s+event",
                r"risk\s+to\s+patient",
                r"clinical\s+safety"
            ],
            test_case_templates=[
                "Verify patient safety monitoring mechanisms",
                "Test adverse event detection and reporting",
                "Validate safety alarm functionality",
                "Verify risk mitigation controls"
            ],
            risk_indicators=["critical", "safety", "alarm", "emergency"],
            compliance_mapping={
                RegulatoryStandard.FDA_21_CFR_820: ["820.30", "820.70"],
                RegulatoryStandard.IEC_62304: ["5.5", "6.1"],
                RegulatoryStandard.ISO_13485: ["7.3", "8.2"]
            }
        )
        
        # Data Integrity Pattern
        data_integrity = DomainPattern(
            pattern_id="DATA_INTEGRITY",
            name="Data Integrity Requirements",
            description="Patterns for data integrity and validation",
            regex_patterns=[
                r"data\s+integrity",
                r"data\s+validation",
                r"data\s+accuracy",
                r"data\s+consistency",
                r"audit\s+trail"
            ],
            test_case_templates=[
                "Verify data validation mechanisms",
                "Test data integrity checks",
                "Validate audit trail completeness",
                "Verify data consistency across systems"
            ],
            risk_indicators=["integrity", "validation", "audit", "consistency"],
            compliance_mapping={
                RegulatoryStandard.FDA_21_CFR_820: ["820.180", "820.186"],
                RegulatoryStandard.GDPR: ["Article 5", "Article 25"],
                RegulatoryStandard.ISO_27001: ["A.12.2", "A.12.3"]
            }
        )
        
        # Authentication and Authorization Pattern
        auth_pattern = DomainPattern(
            pattern_id="AUTHENTICATION",
            name="Authentication and Authorization",
            description="Patterns for user authentication and access control",
            regex_patterns=[
                r"authentication",
                r"authorization",
                r"access\s+control",
                r"user\s+login",
                r"role-based\s+access"
            ],
            test_case_templates=[
                "Verify user authentication mechanisms",
                "Test role-based access controls",
                "Validate session management",
                "Verify unauthorized access prevention"
            ],
            risk_indicators=["security", "access", "unauthorized", "breach"],
            compliance_mapping={
                RegulatoryStandard.ISO_27001: ["A.9.1", "A.9.2"],
                RegulatoryStandard.GDPR: ["Article 32"],
                RegulatoryStandard.HIPAA: ["164.308", "164.312"]
            }
        )
        
        # Medical Device Performance Pattern
        device_performance = DomainPattern(
            pattern_id="DEVICE_PERFORMANCE",
            name="Medical Device Performance",
            description="Patterns for device performance and reliability",
            regex_patterns=[
                r"device\s+performance",
                r"measurement\s+accuracy",
                r"calibration",
                r"precision",
                r"response\s+time"
            ],
            test_case_templates=[
                "Verify measurement accuracy requirements",
                "Test device calibration procedures",
                "Validate performance specifications",
                "Verify response time requirements"
            ],
            risk_indicators=["accuracy", "precision", "calibration", "performance"],
            compliance_mapping={
                RegulatoryStandard.FDA_21_CFR_820: ["820.72"],
                RegulatoryStandard.IEC_62304: ["5.6"],
                RegulatoryStandard.ISO_13485: ["7.6"]
            }
        )
        
        # Store patterns
        self.domain_patterns["PATIENT_SAFETY"] = patient_safety
        self.domain_patterns["DATA_INTEGRITY"] = data_integrity
        self.domain_patterns["AUTHENTICATION"] = auth_pattern
        self.domain_patterns["DEVICE_PERFORMANCE"] = device_performance
    
    def _initialize_risk_assessment(self):
        """Initialize risk assessment keywords and patterns"""
        
        self.risk_keywords = {
            RiskLevel.CRITICAL: [
                "death", "serious injury", "life threatening", "critical failure",
                "patient safety", "clinical safety", "emergency", "alarm",
                "security breach", "data loss", "unauthorized access"
            ],
            RiskLevel.HIGH: [
                "injury", "harm", "failure", "malfunction", "error",
                "performance degradation", "data corruption", "privacy violation",
                "compliance violation", "regulatory risk"
            ],
            RiskLevel.MEDIUM: [
                "inconvenience", "delay", "minor error", "usability issue",
                "performance impact", "data quality", "process deviation"
            ],
            RiskLevel.LOW: [
                "cosmetic issue", "minor inconvenience", "documentation error",
                "training issue", "minor performance impact"
            ]
        }
    
    def _initialize_device_classifications(self):
        """Initialize device-specific testing requirements"""
        
        self.device_specific_rules = {
            DeviceClass.CLASS_III: [
                "Extensive clinical testing required",
                "Pre-market approval (PMA) testing",
                "Risk analysis documentation",
                "Software life cycle documentation",
                "Cybersecurity testing"
            ],
            DeviceClass.CLASS_II: [
                "510(k) predicate device comparison",
                "Special controls compliance",
                "Software validation testing",
                "Electromagnetic compatibility testing",
                "Biocompatibility testing"
            ],
            DeviceClass.CLASS_I: [
                "General controls compliance",
                "Basic safety testing",
                "Labeling requirements",
                "Quality system requirements"
            ],
            DeviceClass.IVD: [
                "Analytical performance testing",
                "Clinical performance validation",
                "Software verification and validation",
                "Quality control testing",
                "Stability testing"
            ]
        }
    
    def analyze_requirement(self, requirement_text: str, 
                          context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze a requirement and provide domain-specific insights
        
        Args:
            requirement_text: The requirement text to analyze
            context: Additional context information
            
        Returns:
            Analysis results with compliance mapping, risk assessment, and test recommendations
        """
        analysis = {
            "requirement_text": requirement_text,
            "applicable_standards": [],
            "risk_level": RiskLevel.MEDIUM,
            "domain_patterns": [],
            "compliance_rules": [],
            "test_recommendations": [],
            "risk_indicators": [],
            "device_class_specific": []
        }
        
        # Analyze against domain patterns
        for pattern_id, pattern in self.domain_patterns.items():
            if self._matches_pattern(requirement_text, pattern):
                analysis["domain_patterns"].append({
                    "pattern_id": pattern_id,
                    "name": pattern.name,
                    "test_templates": pattern.test_case_templates,
                    "compliance_mapping": pattern.compliance_mapping
                })
                
                # Add applicable standards
                for standard in pattern.compliance_mapping.keys():
                    if standard not in analysis["applicable_standards"]:
                        analysis["applicable_standards"].append(standard)
        
        # Risk assessment
        analysis["risk_level"] = self._assess_risk(requirement_text)
        analysis["risk_indicators"] = self._extract_risk_indicators(requirement_text)
        
        # Find applicable compliance rules
        for standard in analysis["applicable_standards"]:
            if standard in self.compliance_rules:
                for rule in self.compliance_rules[standard]:
                    if self._requirement_matches_rule(requirement_text, rule):
                        analysis["compliance_rules"].append({
                            "rule_id": rule.id,
                            "standard": rule.standard,
                            "section": rule.section,
                            "title": rule.title,
                            "test_patterns": rule.test_patterns
                        })
        
        # Generate test recommendations
        analysis["test_recommendations"] = self._generate_test_recommendations(
            requirement_text, analysis
        )
        
        return analysis
    
    def _matches_pattern(self, text: str, pattern: DomainPattern) -> bool:
        """Check if text matches a domain pattern"""
        text_lower = text.lower()
        
        for regex_pattern in pattern.regex_patterns:
            if re.search(regex_pattern, text_lower):
                return True
        
        return False
    
    def _assess_risk(self, requirement_text: str) -> RiskLevel:
        """Assess risk level of a requirement"""
        text_lower = requirement_text.lower()
        
        # Check for critical risk indicators
        for keyword in self.risk_keywords[RiskLevel.CRITICAL]:
            if keyword in text_lower:
                return RiskLevel.CRITICAL
        
        # Check for high risk indicators
        for keyword in self.risk_keywords[RiskLevel.HIGH]:
            if keyword in text_lower:
                return RiskLevel.HIGH
        
        # Check for medium risk indicators
        for keyword in self.risk_keywords[RiskLevel.MEDIUM]:
            if keyword in text_lower:
                return RiskLevel.MEDIUM
        
        # Default to low risk
        return RiskLevel.LOW
    
    def _extract_risk_indicators(self, requirement_text: str) -> List[str]:
        """Extract risk indicators from requirement text"""
        indicators = []
        text_lower = requirement_text.lower()
        
        for risk_level, keywords in self.risk_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    indicators.append(f"{risk_level.value}: {keyword}")
        
        return indicators
    
    def _requirement_matches_rule(self, requirement_text: str, rule: ComplianceRule) -> bool:
        """Check if a requirement matches a compliance rule"""
        text_lower = requirement_text.lower()
        
        # Check if any rule keywords are present
        for keyword in rule.keywords:
            if keyword in text_lower:
                return True
        
        return False
    
    def _generate_test_recommendations(self, requirement_text: str, 
                                     analysis: Dict[str, Any]) -> List[str]:
        """Generate test case recommendations based on analysis"""
        recommendations = []
        
        # Add pattern-based recommendations
        for pattern_info in analysis["domain_patterns"]:
            recommendations.extend(pattern_info["test_templates"])
        
        # Add compliance-based recommendations
        for rule_info in analysis["compliance_rules"]:
            recommendations.extend(rule_info["test_patterns"])
        
        # Add risk-based recommendations
        risk_level = analysis["risk_level"]
        if risk_level == RiskLevel.CRITICAL:
            recommendations.extend([
                "Perform extensive safety testing",
                "Conduct failure mode analysis",
                "Verify emergency response procedures"
            ])
        elif risk_level == RiskLevel.HIGH:
            recommendations.extend([
                "Perform thorough functional testing",
                "Conduct risk scenario testing",
                "Verify error handling mechanisms"
            ])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recommendations.append(rec)
        
        return unique_recommendations
    
    def get_compliance_requirements(self, standard: RegulatoryStandard) -> List[ComplianceRule]:
        """Get all compliance rules for a specific standard"""
        return self.compliance_rules.get(standard, [])
    
    def get_device_specific_requirements(self, device_class: DeviceClass) -> List[str]:
        """Get device class specific testing requirements"""
        return self.device_specific_rules.get(device_class, [])
    
    def validate_compliance_coverage(self, requirements: List[str], 
                                   standards: List[RegulatoryStandard]) -> Dict[str, Any]:
        """Validate compliance coverage across requirements"""
        coverage_report = {
            "total_requirements": len(requirements),
            "standards_coverage": {},
            "gaps": [],
            "recommendations": []
        }
        
        for standard in standards:
            rules = self.get_compliance_requirements(standard)
            covered_rules = []
            uncovered_rules = []
            
            for rule in rules:
                rule_covered = False
                for req_text in requirements:
                    if self._requirement_matches_rule(req_text, rule):
                        rule_covered = True
                        break
                
                if rule_covered:
                    covered_rules.append(rule.id)
                else:
                    uncovered_rules.append(rule.id)
            
            coverage_report["standards_coverage"][standard.value] = {
                "total_rules": len(rules),
                "covered_rules": len(covered_rules),
                "coverage_percentage": (len(covered_rules) / len(rules)) * 100 if rules else 0,
                "covered_rule_ids": covered_rules,
                "uncovered_rule_ids": uncovered_rules
            }
            
            # Add gaps and recommendations for uncovered rules
            for rule_id in uncovered_rules:
                rule = next((r for r in rules if r.id == rule_id), None)
                if rule:
                    coverage_report["gaps"].append({
                        "standard": standard.value,
                        "rule_id": rule_id,
                        "section": rule.section,
                        "title": rule.title
                    })
                    
                    coverage_report["recommendations"].extend([
                        f"Add requirement for {rule.title} ({rule.section})",
                        f"Ensure coverage of {standard.value} section {rule.section}"
                    ])
        
        return coverage_report


# Initialize global domain knowledge instance
domain_knowledge = HealthcareDomainKnowledge()


def analyze_healthcare_requirement(requirement_text: str, 
                                 context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Analyze a healthcare requirement using domain knowledge
    
    Args:
        requirement_text: The requirement text to analyze
        context: Additional context information
        
    Returns:
        Domain analysis results
    """
    return domain_knowledge.analyze_requirement(requirement_text, context)


def get_compliance_rules(standard: RegulatoryStandard) -> List[ComplianceRule]:
    """Get compliance rules for a specific standard"""
    return domain_knowledge.get_compliance_requirements(standard)


def validate_compliance(requirements: List[str], 
                       standards: List[RegulatoryStandard]) -> Dict[str, Any]:
    """Validate compliance coverage"""
    return domain_knowledge.validate_compliance_coverage(requirements, standards)


# Export main components
__all__ = [
    'HealthcareDomainKnowledge',
    'RegulatoryStandard',
    'RiskLevel',
    'DeviceClass',
    'ComplianceRule',
    'DomainPattern',
    'analyze_healthcare_requirement',
    'get_compliance_rules',
    'validate_compliance',
    'domain_knowledge'
]