# Architecture Documentation

## System Overview

Sec-Vote is a microservices-based polling platform designed with security and scalability in mind. The system follows a distributed architecture pattern where each service has a single responsibility.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Client Layer                         │
│                  (Web, Mobile, CLI clients)                  │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ HTTPS
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                       API Gateway                            │
│              (Port 8080 - Request Routing)                   │
│              - Rate Limiting                                 │
│              - Service Health Checks                         │
│              - Request Forwarding                            │
└──┬──────────┬──────────┬──────────┬─────────────────────────┘
   │          │          │          │
   │          │          │          │
   ▼          ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│  Auth  │ │  Poll  │ │  Vote  │ │Results │
│Service │ │Service │ │Service │ │Service │
│:5001   │ │:5002   │ │:5003   │ │:5004   │
└───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘
    │          │          │          │
    │          └──────────┴──────────┘
    │                     │
    ▼                     ▼
┌─────────┐         ┌─────────┐
│  Redis  │         │PostgreSQL│
│  Cache  │         │ Database │
│  :6379  │         │  :5432   │
└─────────┘         └─────────┘
```

## Service Descriptions

### 1. API Gateway

**Purpose**: Single entry point for all client requests

**Responsibilities**:
- Route requests to appropriate microservices
- Implement rate limiting
- Monitor service health
- Handle service unavailability gracefully
- Aggregate responses when necessary

**Technology**: Flask

**Key Features**:
- IP-based rate limiting
- Service discovery
- Request/response logging
- Error handling and timeout management

### 2. Authentication Service

**Purpose**: Manage user authentication and authorization

**Responsibilities**:
- User registration
- User login
- JWT token generation
- Token validation
- Password management

**Database Schema**:
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);
```

**API Endpoints**:
- `POST /register` - Register new user
- `POST /login` - Authenticate user
- `POST /verify` - Verify JWT token

### 3. Poll Service

**Purpose**: Manage poll creation and lifecycle

**Responsibilities**:
- Create polls
- List polls
- Get poll details
- Update poll status
- Delete polls (creator only)
- Close polls (creator only)

**Database Schema**:
```sql
CREATE TABLE polls (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    creator_id INTEGER NOT NULL,
    creator_username VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    allow_multiple_votes BOOLEAN DEFAULT FALSE,
    is_anonymous BOOLEAN DEFAULT FALSE
);

CREATE TABLE poll_options (
    id SERIAL PRIMARY KEY,
    poll_id INTEGER REFERENCES polls(id) ON DELETE CASCADE,
    text VARCHAR(200) NOT NULL,
    order INTEGER DEFAULT 0
);
```

**API Endpoints**:
- `POST /polls` - Create poll
- `GET /polls` - List polls
- `GET /polls/{id}` - Get poll details
- `DELETE /polls/{id}` - Delete poll
- `POST /polls/{id}/close` - Close poll

### 4. Vote Service

**Purpose**: Handle vote casting and validation

**Responsibilities**:
- Accept authenticated votes
- Accept anonymous votes
- Prevent duplicate voting
- Track vote metadata
- Validate vote eligibility

**Database Schema**:
```sql
CREATE TABLE votes (
    id SERIAL PRIMARY KEY,
    poll_id INTEGER NOT NULL,
    option_id INTEGER NOT NULL,
    user_id INTEGER,
    username VARCHAR(20),
    voted_at TIMESTAMP DEFAULT NOW(),
    ip_address VARCHAR(45)
);

CREATE INDEX idx_poll_user ON votes(poll_id, user_id);
```

**Vote Validation Logic**:
1. Check if poll exists and is active
2. For authenticated users: Check user hasn't voted
3. For anonymous users: Check IP hasn't voted (with time window)
4. Verify option belongs to poll
5. Record vote with metadata

**API Endpoints**:
- `POST /vote` - Cast authenticated vote
- `POST /vote/anonymous` - Cast anonymous vote
- `GET /vote/check/{poll_id}` - Check vote status
- `GET /vote/user` - Get user's vote history

### 5. Results Service

**Purpose**: Aggregate and display voting results

**Responsibilities**:
- Calculate vote counts
- Calculate percentages
- Cache results for performance
- Provide detailed results (creator only)
- Export results to CSV
- Track trending polls

**Caching Strategy**:
- Results cached for 30 seconds
- Cache invalidated on new votes
- Redis for fast access

**API Endpoints**:
- `GET /results/{poll_id}` - Get poll results
- `GET /results/{poll_id}/detailed` - Get detailed results
- `GET /results/{poll_id}/export` - Export to CSV
- `GET /results/stats` - Platform statistics
- `GET /results/trending` - Trending polls

## Data Flow

### Vote Casting Flow

```
Client
  │
  ├─► POST /api/vote
  │
Gateway
  │
  ├─► Validate Rate Limit
  ├─► Forward to Vote Service
  │
Vote Service
  │
  ├─► Validate JWT Token
  ├─► Check Duplicate Vote (Redis Cache)
  ├─► Check Duplicate Vote (Database)
  ├─► Record Vote
  ├─► Update Cache
  │
  └─► Return Success
```

### Poll Creation Flow

```
Client
  │
  ├─► POST /api/polls
  │
Gateway
  │
  ├─► Forward to Poll Service
  │
Poll Service
  │
  ├─► Validate JWT Token
  ├─► Validate Input
  ├─► Create Poll Record
  ├─► Create Option Records
  │
  └─► Return Poll Details
```

## Communication Patterns

### Inter-Service Communication

**Synchronous HTTP**:
- Gateway to services
- Service health checks

**Shared Database** (Alternative approach):
- Each service has its own database
- Vote and Results services share vote data

**Caching**:
- Redis for vote duplicate detection
- Redis for results caching
- Reduces database load

## Security Architecture

### Defense in Depth

1. **Network Layer**: Docker network isolation
2. **Gateway Layer**: Rate limiting, request validation
3. **Service Layer**: JWT validation, input sanitization
4. **Data Layer**: ORM protection, encrypted connections

### Token Flow

```
1. User registers/logs in
   └─► Auth Service generates JWT

2. User makes authenticated request
   ├─► Client includes JWT in header
   ├─► Gateway forwards JWT
   └─► Service validates JWT locally

3. JWT contains:
   ├─► user_id
   ├─► username
   ├─► expiration time
   └─► issued time
```

## Scalability Considerations

### Horizontal Scaling

**Stateless Services**: All services are stateless and can be scaled horizontally

```yaml
# Docker Compose scaling example
docker-compose up --scale vote-service=3
```

**Load Balancing**: Add nginx or HAProxy in front of gateway

### Database Scaling

**Read Replicas**: PostgreSQL read replicas for high read load
**Sharding**: Partition data by poll_id for very high scale

### Caching Strategy

**Redis Cluster**: Scale Redis for high cache load
**Cache Invalidation**: Time-based expiration

## Monitoring and Observability

### Health Checks

Each service exposes `/health` endpoint:
```json
{
  "status": "healthy",
  "service": "vote"
}
```

Gateway aggregates health:
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

### Logging

**Service Logs**: Each service logs to stdout
**Log Aggregation**: Use ELK stack or similar in production
**Log Levels**: INFO, WARNING, ERROR

### Metrics (Recommended)

- Request count per endpoint
- Response times
- Error rates
- Active polls
- Total votes
- Cache hit rates

## Deployment

### Development

```bash
docker-compose up --build
```

### Production Considerations

1. **Environment Variables**: Use secrets management
2. **HTTPS**: Reverse proxy with SSL
3. **Database**: Managed PostgreSQL service
4. **Cache**: Managed Redis service
5. **Monitoring**: Application Performance Monitoring (APM)
6. **Logging**: Centralized logging service
7. **Backup**: Automated database backups

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Services | Python/Flask | Microservices framework |
| Gateway | Python/Flask | API routing |
| Database | PostgreSQL | Data persistence |
| Cache | Redis | Performance & deduplication |
| ORM | SQLAlchemy | Database abstraction |
| Auth | JWT + bcrypt | Authentication |
| Containerization | Docker | Service isolation |
| Orchestration | Docker Compose | Local deployment |

## Design Patterns

### Patterns Used

1. **API Gateway Pattern**: Single entry point
2. **Microservices Pattern**: Service decomposition
3. **Database per Service**: Each service manages its data
4. **Circuit Breaker**: Timeout and retry logic
5. **Rate Limiting**: Request throttling
6. **Caching**: Performance optimization

## Future Enhancements

1. **Message Queue**: RabbitMQ/Kafka for async processing
2. **Service Mesh**: Istio for advanced networking
3. **GraphQL Gateway**: Alternative to REST
4. **WebSocket**: Real-time result updates
5. **Kubernetes**: Production orchestration
6. **CI/CD**: Automated testing and deployment
