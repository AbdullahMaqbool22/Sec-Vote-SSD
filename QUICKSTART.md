# Quick Start Guide

## Installation (5 minutes)

### Prerequisites
- Docker and Docker Compose installed
- Git installed

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/AbdullahMaqbool22/Sec-Vote-SSD.git
   cd Sec-Vote-SSD
   ```

2. **Run the setup script**
   ```bash
   ./setup.sh
   ```
   
   OR manually:
   ```bash
   docker-compose up --build -d
   ```

3. **Verify services are running**
   ```bash
   curl http://localhost:8080/health
   ```

## Common Commands

### Using Makefile
```bash
make build      # Build containers
make up         # Start services
make down       # Stop services
make logs       # View logs
make test       # Run tests
make clean      # Clean everything
```

### Using Docker Compose
```bash
docker-compose up -d                    # Start in background
docker-compose down                     # Stop all services
docker-compose logs -f                  # Follow logs
docker-compose ps                       # List services
docker-compose restart vote-service     # Restart specific service
```

## Quick API Examples

### 1. Register a User
```bash
curl -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "email": "john@example.com",
    "password": "SecurePass123"
  }'
```

**Response:**
```json
{
  "message": "User registered successfully",
  "user": {"id": 1, "username": "john", "email": "john@example.com"},
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 2. Create a Poll
```bash
# Save your token from registration
TOKEN="your-jwt-token-here"

curl -X POST http://localhost:8080/api/polls \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Favorite Programming Language?",
    "description": "Vote for your favorite",
    "options": ["Python", "JavaScript", "Java", "Go"]
  }'
```

### 3. Cast a Vote
```bash
curl -X POST http://localhost:8080/api/vote \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "poll_id": 1,
    "option_id": 1
  }'
```

### 4. Get Results
```bash
curl http://localhost:8080/api/results/1
```

**Response:**
```json
{
  "poll_id": 1,
  "total_votes": 5,
  "results": [
    {"option_id": 1, "votes": 3, "percentage": 60.0},
    {"option_id": 2, "votes": 2, "percentage": 40.0}
  ]
}
```

## Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run with Coverage
```bash
pytest tests/ -v --cov
```

### Test Specific Service
```bash
pytest tests/test_auth.py -v
```

## Development

### Running Services Locally (without Docker)

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start PostgreSQL and Redis**
   ```bash
   docker-compose up postgres redis -d
   ```

3. **Set environment variables**
   ```bash
   export DATABASE_URL="postgresql://secvote:secvote_pass@localhost:5432/secvote_db"
   export REDIS_URL="redis://localhost:6379/0"
   export JWT_SECRET_KEY="your-secret-key"
   ```

4. **Run services in separate terminals**
   ```bash
   # Terminal 1
   python services/auth/app.py

   # Terminal 2
   python services/poll/app.py

   # Terminal 3
   python services/vote/app.py

   # Terminal 4
   python services/results/app.py

   # Terminal 5
   python gateway/app.py
   ```

## Troubleshooting

### Services won't start
```bash
# Check if ports are in use
lsof -i :8080
lsof -i :5432

# Clean up and rebuild
docker-compose down -v
docker-compose up --build
```

### Database connection errors
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres
```

### Redis connection errors
```bash
# Check if Redis is running
docker-compose ps redis

# Check logs
docker-compose logs redis
```

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

Key variables:
- `JWT_SECRET_KEY`: Secret for JWT signing (CHANGE IN PRODUCTION!)
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `FLASK_DEBUG`: Enable/disable debug mode (False for production)

### Service URLs

- API Gateway: http://localhost:8080
- Auth Service: http://localhost:5001
- Poll Service: http://localhost:5002
- Vote Service: http://localhost:5003
- Results Service: http://localhost:5004

## Useful Tips

### View Service Logs
```bash
docker-compose logs -f auth-service
docker-compose logs -f poll-service
docker-compose logs -f vote-service
docker-compose logs -f results-service
docker-compose logs -f gateway
```

### Access Database
```bash
docker exec -it secvote-postgres psql -U secvote -d secvote_db
```

### Access Redis
```bash
docker exec -it secvote-redis redis-cli
```

### Clean Database
```bash
docker-compose down -v  # This removes volumes
docker-compose up -d
```

## Next Steps

1. Read [README.md](README.md) for comprehensive documentation
2. Check [API_REFERENCE.md](docs/API_REFERENCE.md) for all endpoints
3. Review [SECURITY.md](docs/SECURITY.md) for security features
4. See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for system design

## Getting Help

- Check the documentation in `docs/` folder
- Review test files for usage examples
- Open an issue on GitHub

## Production Deployment

For production deployment:
1. Change `JWT_SECRET_KEY` to a strong random value
2. Set `FLASK_DEBUG=False`
3. Use strong database passwords
4. Set up SSL/TLS with reverse proxy
5. Configure proper CORS origins
6. Enable monitoring and logging
7. Set up database backups

See [SECURITY.md](docs/SECURITY.md) for detailed production recommendations.
