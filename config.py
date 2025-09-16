# AI-Powered Healthcare Test Case Generation System
# Main configuration and project setup

import os
from pathlib import Path

# Project structure
PROJECT_ROOT = Path(__file__).parent
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"
DOCS_DIR = PROJECT_ROOT / "docs"
TESTS_DIR = PROJECT_ROOT / "tests"
CONFIG_DIR = PROJECT_ROOT / "config"

# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "healthcare-testgen-ai")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Vertex AI Configuration
VERTEX_AI_LOCATION = os.getenv("VERTEX_AI_LOCATION", "us-central1")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost:5432/healthcare_testgen")
FIREBASE_CONFIG = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.getenv("FIREBASE_APP_ID")
}

# API Configuration
API_HOST = os.getenv("API_HOST", "localhost")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_VERSION = "v1"
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# Security Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ALM Integration Configuration
JIRA_CONFIG = {
    "base_url": os.getenv("JIRA_BASE_URL"),
    "username": os.getenv("JIRA_USERNAME"),
    "api_token": os.getenv("JIRA_API_TOKEN")
}

POLARION_CONFIG = {
    "base_url": os.getenv("POLARION_BASE_URL"),
    "username": os.getenv("POLARION_USERNAME"),
    "password": os.getenv("POLARION_PASSWORD")
}

AZURE_DEVOPS_CONFIG = {
    "organization": os.getenv("AZURE_DEVOPS_ORG"),
    "project": os.getenv("AZURE_DEVOPS_PROJECT"),
    "pat": os.getenv("AZURE_DEVOPS_PAT")
}

# Healthcare Compliance Standards
SUPPORTED_STANDARDS = [
    "FDA_21_CFR_PART_820",
    "IEC_62304",
    "ISO_9001",
    "ISO_13485",
    "ISO_27001",
    "GDPR"
]

# Document Processing Configuration
SUPPORTED_FORMATS = [
    ".pdf",
    ".docx",
    ".doc",
    ".xml",
    ".md",
    ".txt",
    ".html"
]

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
MAX_PAGES_PER_DOCUMENT = 500

# AI Processing Configuration
AI_CONFIG = {
    "max_tokens": 8192,
    "temperature": 0.1,
    "top_p": 0.8,
    "safety_settings": [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        }
    ]
}

# Logging Configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "default"
        },
        "file": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "default",
            "filename": "logs/app.log"
        }
    },
    "loggers": {
        "": {
            "level": "INFO",
            "handlers": ["console", "file"]
        }
    }
}

# Test Case Generation Templates
TEST_CASE_TEMPLATES = {
    "functional": {
        "fields": ["test_id", "title", "description", "preconditions", "steps", "expected_result", "priority"],
        "compliance_fields": ["regulatory_reference", "risk_level", "traceability_id"]
    },
    "security": {
        "fields": ["test_id", "title", "description", "security_aspect", "threat_model", "steps", "expected_result"],
        "compliance_fields": ["iso_27001_reference", "gdpr_compliance", "data_classification"]
    },
    "performance": {
        "fields": ["test_id", "title", "description", "performance_criteria", "load_conditions", "steps", "acceptance_criteria"],
        "compliance_fields": ["regulatory_reference", "performance_standard"]
    }
}