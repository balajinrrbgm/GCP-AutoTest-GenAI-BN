# Healthcare AI Test Case Generation System

A comprehensive AI-powered system for automatically generating healthcare-compliant test cases from software requirements documentation.

## 🚀 Features

- **Multi-format Document Parsing**: Support for PDF, Word, XML, and Markdown requirement documents
- **AI-Powered Test Generation**: Uses Google Gemini for intelligent test case creation
- **Healthcare Compliance**: Built-in validation for FDA, IEC 62304, and ISO standards
- **ALM Integration**: Seamless integration with Jira, Polarion, and Azure DevOps
- **Full Traceability**: Complete requirement-to-test case traceability matrix
- **GDPR Compliant**: Privacy-first data processing and storage

## 🏗️ Architecture

### Backend (Python/FastAPI)
- **Requirements Parser**: Multi-format document processing with Google Document AI
- **Healthcare Domain Knowledge**: Specialized compliance rules and regulations
- **AI Engine**: Google Gemini-powered test case generation
- **API Layer**: RESTful APIs for all system functionality
- **Database**: PostgreSQL with SQLAlchemy ORM

### Frontend (React/TypeScript)
- **Modern UI**: Material-UI components for professional interface
- **Real-time Updates**: WebSocket integration for live test generation
- **Document Management**: Drag-and-drop file uploads with preview
- **Dashboard**: Comprehensive analytics and progress tracking

## 🛠️ Technology Stack

### Core Technologies
- **Backend**: Python 3.9+, FastAPI, SQLAlchemy, Pydantic
- **Frontend**: React 18+, TypeScript, Material-UI, Axios
- **Database**: PostgreSQL, Redis (caching)
- **AI/ML**: Google Gemini, Vertex AI, Document AI

### Cloud Services
- **Google Cloud Platform**: Primary cloud provider
- **BigQuery**: Data warehouse for analytics
- **Firebase**: Real-time features and authentication
- **Cloud Storage**: Document and media storage

### Development Tools
- **Testing**: pytest, Jest, React Testing Library
- **Code Quality**: Black, isort, ESLint, Prettier
- **Containerization**: Docker, Docker Compose
- **Documentation**: OpenAPI/Swagger, Sphinx

## � Prerequisites

- Python 3.9 or higher
- Node.js 16+ and npm
- PostgreSQL 12+
- Google Cloud Platform account
- Docker (optional, for containerized deployment)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Automating-Test-Case-Generation-with-AI
```

### 2. Environment Setup
```bash
# Set up the complete development environment
python run.py setup
```

### 3. Configuration
Create a `.env` file in the project root:
```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/healthcare_testgen

# Google Cloud
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true

# Security
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# AI Services
GEMINI_API_KEY=your-gemini-api-key
VERTEX_AI_PROJECT=your-vertex-ai-project
VERTEX_AI_LOCATION=us-central1
```

### 4. Run the Application

#### Backend Server
```bash
python run.py backend
```
The API will be available at `http://localhost:8000`

#### Frontend Development Server
```bash
python run.py frontend
```
The web application will be available at `http://localhost:3000`

## 📊 API Documentation

Once the backend is running, access the interactive API documentation:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Main API Endpoints

#### Requirements Management
- `POST /api/v1/requirements/upload` - Upload requirement documents
- `GET /api/v1/requirements/` - List all requirements
- `GET /api/v1/requirements/{id}` - Get specific requirement

#### Test Case Generation
- `POST /api/v1/test-cases/generate` - Generate test cases from requirements
- `GET /api/v1/test-cases/` - List all test cases
- `PUT /api/v1/test-cases/{id}` - Update test case

#### Compliance Validation
- `POST /api/v1/compliance/validate` - Validate against healthcare standards
- `GET /api/v1/compliance/rules` - Get available compliance rules

#### ALM Integration
- `POST /api/v1/alm/sync` - Sync with external ALM tools
- `GET /api/v1/alm/platforms` - List supported platforms

## 🧪 Testing

Run the complete test suite:
```bash
python run.py test
```

### Test Coverage
- Unit tests for all backend modules
- Integration tests for API endpoints
- Frontend component tests
- End-to-end testing scenarios

## 🏭 Production Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build
```

### Cloud Deployment
The system is designed for deployment on Google Cloud Platform:

1. **Cloud Run**: Containerized backend API
2. **Cloud Storage**: Document and media files
3. **Cloud SQL**: PostgreSQL database
4. **Firebase Hosting**: Frontend web application

## 📈 Healthcare Compliance

The system supports the following healthcare standards:

### Regulatory Standards
- **FDA 21 CFR Part 820**: Quality System Regulation
- **IEC 62304**: Medical device software lifecycle processes
- **ISO 9001**: Quality management systems
- **ISO 13485**: Medical devices quality management
- **ISO 27001**: Information security management

### Data Privacy
- **GDPR**: General Data Protection Regulation compliance
- **HIPAA**: Healthcare data privacy (US)
- **Data encryption**: At rest and in transit
- **Access controls**: Role-based permissions

## 🔧 Development

### Project Structure
```
├── backend/                 # Python/FastAPI backend
│   ├── api/                # API routers and endpoints
│   ├── models/             # Database models
│   ├── requirements_parser/ # Document parsing engine
│   ├── healthcare_domain/  # Healthcare knowledge base
│   ├── ai_engine/          # AI test generation
│   └── main.py            # Application entry point
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/    # Reusable components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API services
│   │   └── utils/         # Utility functions
│   └── package.json
├── docs/                   # Documentation
├── tests/                  # Test suites
├── docker-compose.yml      # Docker configuration
├── requirements.txt        # Python dependencies
└── run.py                 # Development scripts
```

## 📞 Support

For support and questions:
- **Documentation**: Check the `/docs` directory for detailed guides
- **Issues**: Create GitHub issues for bugs and feature requests
- **API Help**: Use the interactive documentation at `/docs` endpoint

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Note**: This system is designed for healthcare software development and should be used in compliance with relevant regulatory requirements and organizational policies.