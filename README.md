# Middle Office Trading Portal

A comprehensive middle office trading system built with modern web technologies, featuring real-time trade validation, reconciliation, lifecycle management, and document handling for both Equity and Forex instruments.

## 🏗️ Architecture Overview

The Middle Office Portal implements a microservices architecture with the following key components:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (React/HTML)  │◄──►│   Services      │◄──►│   Firebase      │
│   Port 3000     │    │   (FastAPI)     │    │   Firestore     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └──────────────►│   Validation    │◄─────────────┘
                        │   Services      │
                        │   Port 8011     │
                        └─────────────────┘
```

### Core Components

1. **Frontend Portal** - Modern web interface with real-time updates
2. **Trade Capture Services** - Handle trade data ingestion and processing
3. **Validation Services** - Validate trades against termsheets and business rules
4. **Reconciliation Services** - Compare data across multiple systems
5. **Lifecycle Management** - Track trade status and events
6. **Document Management** - Store and retrieve termsheets and trade documents
7. **Firebase Integration** - Cloud-based data storage and real-time synchronization

## 🚀 Features

### Trade Management
- **Multi-Instrument Support**: Equity and Forex trade processing
- **Real-time Validation**: Instant trade validation against termsheets
- **Document Integration**: Termsheet upload and retrieval
- **Status Tracking**: Complete trade lifecycle management

### Data Reconciliation
- **System Comparison**: FOFO (Front Office to Front Office) and FOBO (Front Office to Back Office) reconciliation
- **Discrepancy Detection**: Automated identification of data mismatches
- **Action Tracking**: Resolution workflow management

### User Interface
- **Modern Dashboard**: Real-time KPIs and metrics
- **Responsive Design**: Works on desktop and mobile devices
- **Interactive Tables**: Sortable, filterable data views
- **Document Viewer**: Professional termsheet display

### Analytics & Reporting
- **Trade Analytics**: Comprehensive trade statistics
- **Validation Reports**: Detailed validation results and failure reasons
- **Reconciliation Reports**: System comparison summaries
- **Lifecycle Tracking**: Complete audit trail

## 🛠️ Technology Stack

### Frontend
- **HTML5/CSS3** - Semantic markup and modern styling
- **JavaScript (ES6+)** - Dynamic functionality and API integration
- **Tailwind CSS** - Utility-first CSS framework
- **Papa Parse** - CSV file parsing and processing

### Backend Services
- **Python 3.11+** - Core programming language
- **FastAPI** - Modern, fast web framework for APIs
- **Uvicorn** - ASGI server for FastAPI applications
- **Firebase Admin SDK** - Google Firebase integration

### Database & Storage
- **Firebase Firestore** - NoSQL cloud database
- **Collections**:
  - `fx_capture` - Forex trade data
  - `fx_termsheet` - Forex termsheets
  - `fx_validation` - Forex validation results
  - `fx_reconciliation` - Forex reconciliation data
  - `eq_termsheets` - Equity termsheets
  - `eq_validation` - Equity validation results

### Development Tools
- **Git** - Version control
- **VS Code** - Development environment

## 🔧 Service Architecture

### Service Ports
- **Frontend**: `http://localhost:8080`
- **Equity Trade Capture**: `http://localhost:8008`
- **Equity Termsheet Capture**: `http://localhost:8013`
- **Equity Trade Validation**: `http://localhost:8011`
- **Forex Trade Capture**: `http://localhost:8009`
- **Forex Termsheet Capture**: `http://localhost:8012`
- **Forex Trade Validation**: `http://localhost:8010`
- **Reconciliation Service**: `http://localhost:8022`

### Service Responsibilities

#### Trade Capture Services
- **Equity Trade Capture** (Port 8008)
  - Processes equity trade data
  - Stores trades in Firebase `fx_capture` collection
  - Handles CSV file uploads
  - Validates trade data format

- **Forex Trade Capture** (Port 8009)
  - Processes forex trade data
  - Stores trades in Firebase `fx_capture` collection
  - Handles CSV file uploads
  - Validates trade data format

#### Termsheet Services
- **Equity Termsheet Capture** (Port 8013)
  - Uploads and stores equity termsheets
  - Stores in Firebase `eq_termsheets` collection
  - Uses Trade ID as document name
  - Handles field normalization

- **Forex Termsheet Capture** (Port 8012)
  - Uploads and stores forex termsheets
  - Stores in Firebase `fx_termsheet` collection
  - Handles field normalization

#### Validation Services
- **Equity Trade Validation** (Port 8011)
  - Validates equity trades against termsheets
  - Stores results in Firebase `eq_validation` collection
  - Assigns departments based on validation failures
  - Provides detailed failure reasons

- **Forex Trade Validation** (Port 8010)
  - Validates forex trades against termsheets
  - Stores results in Firebase `fx_validation` collection
  - Provides detailed failure reasons

#### Reconciliation Service
- **Reconciliation Service** (Port 8022)
  - Compares data across multiple systems
  - Handles FOFO and FOBO reconciliation
  - Stores results in Firebase `fx_reconciliation` collection
  - Provides discrepancy analysis

## 🔒 Security Features

### Data Protection
- **Firebase Security Rules** - Database access control
- **Input Validation** - Server-side data validation
- **CSV Sanitization** - File upload security
- **Error Handling** - Secure error messages

### Authentication & Authorization
- **Service-to-Service Authentication** - Internal service communication
- **API Key Management** - Firebase service account keys
- **CORS Configuration** - Cross-origin request handling

### Data Privacy
- **Encrypted Storage** - Firebase Firestore encryption
- **Audit Logging** - Complete data access logs
- **Data Retention** - Configurable data retention policies

## 📊 Data Flow

### Trade Processing Flow
```
1. Trade Data Upload → Trade Capture Service → Firebase Storage
2. Termsheet Upload → Termsheet Service → Firebase Storage
3. Validation Request → Validation Service → Termsheet Retrieval → Validation → Results Storage
4. Reconciliation Request → Reconciliation Service → Multi-System Comparison → Results Storage
5. Frontend Display → Real-time Data Retrieval → User Interface
```

### Validation Process
```
Trade Data → Field Normalization → Termsheet Retrieval → Field Comparison → 
Validation Result → Department Assignment → Firebase Storage → Frontend Display
```

## 🚀 Getting Started

### Prerequisites
- **Python 3.11+**
- **Node.js 16+** (for Tailwind CSS)
- **Docker & Docker Compose**
- **Firebase Project** with Firestore enabled
- **Firebase Service Account Key**

### Installation

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd middle_office
   ```

2. **Set Up Firebase**
   - Create a Firebase project
   - Enable Firestore database
   - Download service account key as `firebase_key.json`
   - Place in project root

3. **Install Dependencies**
   ```bash
   # Backend dependencies
   pip install -r requirements.txt
   
   # Frontend dependencies (if using npm)
   cd Frontend
   npm install
   ```

4. **Configure Environment**
   ```bash
   # Set Firebase credentials
   export GOOGLE_APPLICATION_CREDENTIALS="./firebase_key.json"
   ```

5. **Start Services**
   ```bash
   # Start all services
   python run_services.py
   
   # Or start individually
   cd services/equity_trade_capture
   python main.py
   ```

6. **Access the Portal**
   - Frontend: `http://localhost:8080`
   - API Documentation: `http://localhost:8008/docs`

## 📁 Project Structure

```
middle_office/
├── Frontend/                    # Frontend application
│   ├── public/                 # Static files
│   │   ├── index.html         # Main HTML file
│   │   ├── scripts/           # JavaScript files
│   │   └── styles/            # CSS files
│   └── src/                   # Source files
├── services/                   # Backend services
│   ├── equity_trade_capture/   # Equity trade processing
│   ├── equity_termsheet_capture/ # Equity termsheet handling
│   ├── equity_trade_validation/  # Equity validation
│   ├── forex_trade_capture/    # Forex trade processing
│   ├── forex_termsheet_capture/ # Forex termsheet handling
│   ├── forex_trade_validation/ # Forex validation
│   └── reconciliation/         # Reconciliation service
├── shared/                     # Shared utilities
├── data/                       # Sample data files
├── firebase_key.json          # Firebase credentials
├── requirements.txt           # Python dependencies
├── run_services.py           # Service orchestration
└── README.md                 # This file
```

## 🔧 Configuration

### Firebase Configuration
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "your-private-key-id",
  "private_key": "your-private-key",
  "client_email": "your-client-email",
  "client_id": "your-client-id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "your-cert-url"
}
```

### Service Configuration
Each service can be configured via environment variables:
- `PORT` - Service port number
- `FIREBASE_PROJECT_ID` - Firebase project ID
- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)

## 🧪 Testing

### Service Health Checks
```bash
# Check service health
curl http://localhost:8008/health
curl http://localhost:8011/health
curl http://localhost:8022/health
```

### API Testing
```bash
# Test trade capture
curl -X POST "http://localhost:8008/trades" \
  -H "Content-Type: application/json" \
  -d @sample_trade.json

# Test validation
curl "http://localhost:8011/validation-results"
```

### Frontend Testing
- Open browser developer tools
- Check console for errors
- Test CSV file uploads
- Verify real-time updates

## 📈 Monitoring & Observability

### Logging
- **Structured Logging** - JSON format logs
- **Correlation IDs** - Request tracing
- **Error Tracking** - Detailed error information

### Metrics
- **Service Health** - Uptime monitoring
- **Performance** - Response time tracking
- **Data Quality** - Validation success rates

### Alerting
- **Service Failures** - Automatic notifications
- **Data Issues** - Validation failure alerts
- **System Health** - Resource monitoring

## 🔄 Deployment

### Development
```bash
# Local development
python run_services.py
```

### Production
```bash
# Using Docker
docker-compose up -d

# Manual deployment
# 1. Set up production Firebase project
# 2. Configure production environment variables
# 3. Deploy services to production servers
# 4. Set up reverse proxy (nginx)
# 5. Configure SSL certificates
```

### Environment Variables
```bash
# Production configuration
export NODE_ENV=production
export FIREBASE_PROJECT_ID=your-production-project
export LOG_LEVEL=INFO
export PORT=8080
```

## 🤝 Contributing

### Development Workflow
1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Test thoroughly**
5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: description"
   ```
6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Create a pull request**

### Code Standards
- **Python**: Follow PEP 8 style guide
- **JavaScript**: Use ES6+ features, consistent formatting
- **HTML/CSS**: Semantic markup, responsive design
- **Documentation**: Update README and inline comments

### Testing Requirements
- **Unit Tests**: For all new functionality
- **Integration Tests**: For service interactions
- **Frontend Tests**: For UI components
- **Performance Tests**: For critical paths

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### License Terms
- **Commercial Use**: Allowed
- **Modification**: Allowed
- **Distribution**: Allowed
- **Private Use**: Allowed
- **Liability**: Limited
- **Warranty**: None

## 🔗 Version Control & Git Setup

### Git Configuration
```bash
# Initialize Git repository
git init

# Configure Git user
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Add remote repository
git remote add origin https://gitlab.com/yourusername/middle-office.git
```

### Git Workflow
```bash
# Check status
git status

# Add changes
git add .

# Commit changes
git commit -m "Descriptive commit message"

# Push to remote
git push origin main

# Create branch
git checkout -b feature/new-feature

# Merge changes
git checkout main
git merge feature/new-feature
```

### GitLab Integration
1. **Create GitLab Project**
   - Go to GitLab.com
   - Create new project
   - Choose blank project template

2. **Push Code**
   ```bash
   git push -u origin main
   ```

3. **Set Up CI/CD** (Optional)
   - Create `.gitlab-ci.yml` file
   - Configure automated testing
   - Set up deployment pipelines

### Security Considerations
- **Never commit secrets** - Use environment variables
- **Use .gitignore** - Exclude sensitive files
- **Review changes** - Code review process
- **Branch protection** - Protect main branch

## 📞 Support

### Documentation
- **API Documentation**: Available at `/docs` endpoints
- **Code Comments**: Inline documentation
- **README**: This comprehensive guide

### Contact
- **Issues**: Create GitHub/GitLab issues
- **Discussions**: Use project discussions
- **Email**: Contact project maintainers

### Community
- **Contributors**: List of project contributors
- **Changelog**: Version history and updates
- **Roadmap**: Future development plans

---

**Note**: This Middle Office Portal is designed for financial institutions and should be used in compliance with relevant financial regulations and security requirements. 