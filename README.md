# Sec-Vote: Secure Microservice Polling Platform

A comprehensive, secure polling platform built with microservices architecture. This project demonstrates enterprise-level software security and design principles with distributed systems.

## 🏗️ Architecture

Sec-Vote is built using a microservices architecture with the following components:

### Services

1. **Authentication Service** (Port 5001)
   - User registration and login
   - JWT token generation and validation
   - Password hashing with bcrypt
   - Session management

2. **Poll Service** (Port 5002)
   - Create, read, update, and delete polls
   - Poll options management
   - Poll access control (creator permissions)
   - Poll expiration handling

3. **Vote Service** (Port 5003)
   - Cast votes (authenticated and anonymous)
   - Prevent duplicate voting
   - IP-based rate limiting for anonymous votes
   - Vote validation and tracking

4. **Results Service** (Port 5004)
   - Real-time vote aggregation
   - Results visualization data
   - Detailed results for poll creators
   - Export functionality (CSV)
   - Trending polls tracking

5. **API Gateway** (Port 8080)
   - Single entry point for all client requests
   - Request routing to appropriate services
   - Rate limiting
   - Service health monitoring

### Infrastructure

- **PostgreSQL Database**: Persistent data storage
- **Redis Cache**: Session management and result caching
- **Docker**: Containerization of all services
- **Docker Compose**: Orchestration and deployment

## 🔐 Security Features

1. **Authentication & Authorization**
   - JWT-based authentication
   - Secure password hashing (bcrypt)
   - Token expiration and validation
   - Protected endpoints with decorators

2. **Input Validation**
   - Email format validation
   - Username constraints (3-20 alphanumeric)
   - Password strength requirements (min 8 chars, letters + numbers)
   - Text input sanitization (XSS prevention)
   - Maximum length constraints

3. **Rate Limiting**
   - Per-endpoint rate limiting
   - IP-based rate limiting for anonymous votes
   - Configurable time windows and request limits

4. **Database Security**
   - SQL injection prevention (SQLAlchemy ORM)
   - Indexed queries for performance
   - Proper foreign key constraints

5. **Vote Integrity**
   - Duplicate vote prevention (user-based)
   - IP tracking for anonymous votes
   - Redis caching for fast duplicate checks

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- Git

### Installation & Deployment

1. **Clone the repository**
   ```bash
   git clone https://github.com/AbdullahMaqbool22/Sec-Vote-SSD.git
   cd Sec-Vote-SSD
   ```

2. **Start all services with Docker Compose**
   ```bash
   docker-compose up --build
   ```

3. **Access the API Gateway**
   ```
   http://localhost:8080
   ```

### Individual Service URLs

- API Gateway: `http://localhost:8080`
- Auth Service: `http://localhost:5001`
- Poll Service: `http://localhost:5002`
- Vote Service: `http://localhost:5003`
- Results Service: `http://localhost:5004`

## 📚 API Documentation

### Authentication Endpoints

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

Response:
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com"
  },
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "johndoe",
  "password": "SecurePass123"
}
```

### Poll Endpoints

#### Create Poll
```http
POST /api/polls
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Favorite Programming Language?",
  "description": "Vote for your favorite language",
  "options": ["Python", "JavaScript", "Java", "Go"],
  "allow_multiple_votes": false,
  "is_anonymous": false
}
```

#### Get All Polls
```http
GET /api/polls?page=1&per_page=10
```

#### Get Poll Details
```http
GET /api/polls/{poll_id}
```

#### Close Poll
```http
POST /api/polls/{poll_id}/close
Authorization: Bearer <token>
```

#### Delete Poll
```http
DELETE /api/polls/{poll_id}
Authorization: Bearer <token>
```

### Vote Endpoints

#### Cast Vote (Authenticated)
```http
POST /api/vote
Authorization: Bearer <token>
Content-Type: application/json

{
  "poll_id": 1,
  "option_id": 2
}
```

#### Cast Anonymous Vote
```http
POST /api/vote/anonymous
Content-Type: application/json

{
  "poll_id": 1,
  "option_id": 3
}
```

#### Check Vote Status
```http
GET /api/vote/check/{poll_id}
Authorization: Bearer <token>
```

#### Get User's Votes
```http
GET /api/vote/user?page=1&per_page=10
Authorization: Bearer <token>
```

### Results Endpoints

#### Get Poll Results
```http
GET /api/results/{poll_id}
```

Response:
```json
{
  "poll_id": 1,
  "total_votes": 42,
  "results": [
    {
      "option_id": 2,
      "votes": 18,
      "percentage": 42.86
    },
    {
      "option_id": 1,
      "votes": 15,
      "percentage": 35.71
    }
  ]
}
```

#### Get Detailed Results (Creator Only)
```http
GET /api/results/{poll_id}/detailed
Authorization: Bearer <token>
```

#### Export Results
```http
GET /api/results/{poll_id}/export
Authorization: Bearer <token>
```

#### Get Statistics
```http
GET /api/results/stats
```

#### Get Trending Polls
```http
GET /api/results/trending
```

## 🧪 Testing

### Running Tests Locally

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run tests**
   ```bash
   pytest tests/ -v --cov
   ```

### Manual Testing with curl

1. **Register a user**
   ```bash
   curl -X POST http://localhost:8080/api/auth/register \
     -H "Content-Type: application/json" \
     -d '{"username":"testuser","email":"test@example.com","password":"Test1234"}'
   ```

2. **Create a poll**
   ```bash
   curl -X POST http://localhost:8080/api/polls \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"title":"Test Poll","options":["Option 1","Option 2"]}'
   ```

3. **Cast a vote**
   ```bash
   curl -X POST http://localhost:8080/api/vote \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"poll_id":1,"option_id":1}'
   ```

4. **Get results**
   ```bash
   curl http://localhost:8080/api/results/1
   ```

## 🛠️ Development

### Local Development Setup

1. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**
   ```bash
   export DATABASE_URL="postgresql://secvote:secvote_pass@localhost:5432/secvote_db"
   export REDIS_URL="redis://localhost:6379/0"
   export JWT_SECRET_KEY="your-secret-key"
   ```

4. **Run individual services**
   ```bash
   # Auth Service
   python services/auth/app.py

   # Poll Service
   python services/poll/app.py

   # Vote Service
   python services/vote/app.py

   # Results Service
   python services/results/app.py

   # Gateway
   python gateway/app.py
   ```

### Project Structure

```
Sec-Vote-SSD/
├── services/
│   ├── auth/           # Authentication service
│   ├── poll/           # Poll management service
│   ├── vote/           # Voting service
│   └── results/        # Results aggregation service
├── gateway/            # API Gateway
├── shared/             # Shared utilities
│   ├── auth_utils.py   # JWT utilities
│   ├── database.py     # Database initialization
│   └── validators.py   # Input validation
├── tests/              # Test suites
├── docs/               # Additional documentation
├── docker-compose.yml  # Docker orchestration
└── requirements.txt    # Python dependencies
```

## 🔧 Configuration

### Environment Variables

Each service can be configured using environment variables:

- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `JWT_SECRET_KEY`: Secret key for JWT token signing
- `FLASK_ENV`: Development or production mode

### Docker Compose Configuration

Edit `docker-compose.yml` to customize:
- Port mappings
- Database credentials
- Service scaling
- Volume mounts

## 📊 Monitoring & Health Checks

Check service health:
```bash
curl http://localhost:8080/health
```

Response:
```json
{
  "status": "healthy",
  "services": {
    "auth": "healthy",
    "poll": "healthy",
    "vote": "healthy",
    "results": "healthy"
  }
}
```

## 🔒 Security Best Practices

1. **Change default credentials**: Update JWT_SECRET_KEY and database passwords in production
2. **Use HTTPS**: Deploy behind a reverse proxy with SSL/TLS
3. **Enable CORS properly**: Configure CORS for your specific frontend domain
4. **Rate limiting**: Adjust rate limits based on your traffic patterns
5. **Database backups**: Regular backups of PostgreSQL data
6. **Monitoring**: Set up logging and monitoring for production
7. **Input validation**: All user inputs are validated and sanitized
8. **Token expiration**: JWT tokens expire after 24 hours

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- Abdullah Maqbool - Initial work

## 🙏 Acknowledgments

- Flask and Flask-CORS for the web framework
- SQLAlchemy for ORM
- PyJWT for authentication
- Docker for containerization
- PostgreSQL and Redis for data storage

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Note**: This is a demonstration project for educational purposes. Additional security hardening is recommended for production use.