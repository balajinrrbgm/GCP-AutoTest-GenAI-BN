"""
Compliance API router for regulatory compliance management
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import logging
from datetime import datetime

from backend.healthcare_domain import (
    validate_compliance, get_compliance_rules, RegulatoryStandard, domain_knowledge
)
from backend.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/standards")
async def list_compliance_standards():
    """
    List all supported compliance standards
    """
    try:
        standards = []
        for standard in RegulatoryStandard:
            rules = get_compliance_rules(standard)
            standards.append({
                "standard": standard.value,
                "name": standard.name,
                "rules_count": len(rules),
                "description": f"Compliance rules for {standard.value}"
            })
        
        return {
            "standards": standards,
            "total_count": len(standards)
        }
        
    except Exception as e:
        logger.error(f"Failed to list standards: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list standards: {str(e)}")


@router.get("/standards/{standard}/rules")
async def get_standard_rules(standard: str):
    """
    Get compliance rules for a specific standard
    """
    try:
        try:
            std = RegulatoryStandard(standard)
        except ValueError:
            raise HTTPException(status_code=404, detail=f"Standard {standard} not found")
        
        rules = get_compliance_rules(std)
        
        return {
            "standard": standard,
            "rules": [
                {
                    "id": rule.id,
                    "section": rule.section,
                    "title": rule.title,
                    "description": rule.description,
                    "requirements": rule.requirements,
                    "test_patterns": rule.test_patterns,
                    "risk_level": rule.risk_level.value,
                    "keywords": rule.keywords
                }
                for rule in rules
            ],
            "total_count": len(rules)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get standard rules: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get standard rules: {str(e)}")


@router.post("/validate")
async def validate_requirements_compliance(
    requirements: List[str],
    standards: List[str],
    db: Session = Depends(get_db)
):
    """
    Validate compliance coverage for a set of requirements
    """
    try:
        # Convert string standards to enum
        standard_enums = []
        for std in standards:
            try:
                standard_enums.append(RegulatoryStandard(std))
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid standard: {std}")
        
        # Validate compliance
        coverage_report = validate_compliance(requirements, standard_enums)
        
        return {
            "validation_timestamp": datetime.utcnow().isoformat(),
            "requirements_analyzed": len(requirements),
            "standards_checked": len(standard_enums),
            "coverage_report": coverage_report,
            "overall_compliance": {
                "status": "compliant" if all(
                    coverage["coverage_percentage"] >= 80 
                    for coverage in coverage_report["standards_coverage"].values()
                ) else "non_compliant",
                "average_coverage": sum(
                    coverage["coverage_percentage"] 
                    for coverage in coverage_report["standards_coverage"].values()
                ) / len(coverage_report["standards_coverage"]) if coverage_report["standards_coverage"] else 0
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Compliance validation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Compliance validation failed: {str(e)}")


@router.post("/analyze-requirement")
async def analyze_requirement_compliance(
    requirement_text: str,
    context: Dict[str, Any] = None
):
    """
    Analyze a single requirement for compliance implications
    """
    try:
        analysis = domain_knowledge.analyze_requirement(requirement_text, context)
        
        return {
            "requirement_text": requirement_text,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "compliance_analysis": {
                "applicable_standards": analysis.get("applicable_standards", []),
                "risk_level": analysis.get("risk_level"),
                "risk_indicators": analysis.get("risk_indicators", []),
                "domain_patterns": analysis.get("domain_patterns", []),
                "compliance_rules": analysis.get("compliance_rules", []),
                "test_recommendations": analysis.get("test_recommendations", [])
            }
        }
        
    except Exception as e:
        logger.error(f"Requirement analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Requirement analysis failed: {str(e)}")


@router.get("/reports/coverage")
async def get_compliance_coverage_report(
    project_id: str = None,
    standards: List[str] = None,
    db: Session = Depends(get_db)
):
    """
    Generate compliance coverage report for a project
    """
    try:
        # Mock implementation - in production, query actual project data
        report = {
            "project_id": project_id,
            "report_timestamp": datetime.utcnow().isoformat(),
            "standards_analyzed": standards or [],
            "overall_coverage": {
                "total_requirements": 150,
                "covered_requirements": 120,
                "coverage_percentage": 80.0,
                "compliance_status": "mostly_compliant"
            },
            "standards_coverage": {
                "fda_21_cfr_820": {
                    "total_rules": 25,
                    "covered_rules": 20,
                    "coverage_percentage": 80.0,
                    "gaps": [
                        {"rule_id": "FDA_820_75", "section": "820.75", "title": "Process Validation"}
                    ]
                },
                "iec_62304": {
                    "total_rules": 30,
                    "covered_rules": 25,
                    "coverage_percentage": 83.3,
                    "gaps": [
                        {"rule_id": "IEC_62304_5_7", "section": "5.7", "title": "Software Risk Management"}
                    ]
                }
            },
            "recommendations": [
                "Add requirements for process validation (FDA 820.75)",
                "Include software risk management procedures (IEC 62304 5.7)",
                "Review security requirements for ISO 27001 compliance"
            ]
        }
        
        return report
        
    except Exception as e:
        logger.error(f"Failed to generate coverage report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate coverage report: {str(e)}")


@router.get("/reports/audit-trail")
async def get_compliance_audit_trail(
    project_id: str = None,
    start_date: str = None,
    end_date: str = None,
    db: Session = Depends(get_db)
):
    """
    Get compliance audit trail for a project
    """
    try:
        # Mock implementation
        audit_trail = {
            "project_id": project_id,
            "report_timestamp": datetime.utcnow().isoformat(),
            "audit_period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "events": [
                {
                    "event_id": "audit_001",
                    "timestamp": "2024-01-01T10:00:00Z",
                    "event_type": "requirement_added",
                    "description": "New FDA compliance requirement added",
                    "user": "admin@healthcare.com",
                    "details": {
                        "requirement_id": "REQ_001",
                        "standard": "FDA_21_CFR_820",
                        "section": "820.30"
                    }
                },
                {
                    "event_id": "audit_002",
                    "timestamp": "2024-01-01T11:00:00Z",
                    "event_type": "test_case_generated",
                    "description": "Compliance test cases generated",
                    "user": "system",
                    "details": {
                        "test_cases_count": 5,
                        "requirement_id": "REQ_001",
                        "generation_method": "AI"
                    }
                }
            ],
            "summary": {
                "total_events": 2,
                "events_by_type": {
                    "requirement_added": 1,
                    "test_case_generated": 1
                }
            }
        }
        
        return audit_trail
        
    except Exception as e:
        logger.error(f"Failed to get audit trail: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get audit trail: {str(e)}")


@router.post("/gap-analysis")
async def perform_gap_analysis(
    current_requirements: List[str],
    target_standards: List[str],
    db: Session = Depends(get_db)
):
    """
    Perform gap analysis against target compliance standards
    """
    try:
        # Convert string standards to enum
        standard_enums = []
        for std in target_standards:
            try:
                standard_enums.append(RegulatoryStandard(std))
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid standard: {std}")
        
        # Perform gap analysis
        coverage_report = validate_compliance(current_requirements, standard_enums)
        
        # Extract gaps and recommendations
        gaps = coverage_report.get("gaps", [])
        recommendations = coverage_report.get("recommendations", [])
        
        gap_analysis = {
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "standards_analyzed": target_standards,
            "requirements_count": len(current_requirements),
            "identified_gaps": gaps,
            "recommendations": recommendations,
            "priority_gaps": [gap for gap in gaps if "critical" in gap.get("title", "").lower()],
            "implementation_plan": [
                {
                    "phase": 1,
                    "title": "Critical Gaps",
                    "items": [gap for gap in gaps if "critical" in gap.get("title", "").lower()],
                    "estimated_effort": "2-4 weeks"
                },
                {
                    "phase": 2,
                    "title": "High Priority Gaps",
                    "items": [gap for gap in gaps if "high" in gap.get("title", "").lower()],
                    "estimated_effort": "4-6 weeks"
                }
            ]
        }
        
        return gap_analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Gap analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Gap analysis failed: {str(e)}")