# Security Documentation

## Overview

Sec-Vote implements multiple layers of security to protect user data and ensure voting integrity.

## Security Features

### 1. Authentication & Authorization

#### JWT (JSON Web Tokens)
- **Token Generation**: Secure tokens are generated upon user registration and login
- **Token Expiration**: Tokens expire after 24 hours to limit exposure
- **Algorithm**: HS256 (HMAC with SHA-256)
- **Secret Key**: Configurable via environment variable (`JWT_SECRET_KEY`)

**Token Structure:**
```json
{
  "user_id": 1,
  "username": "johndoe",
  "exp": 1699459200,
  "iat": 1699372800
}
```

#### Password Security
- **Hashing**: bcrypt with automatically generated salt
- **Strength Requirements**:
  - Minimum 8 characters
  - Must contain letters
  - Must contain numbers
- **Storage**: Only hashed passwords are stored, never plaintext

### 2. Input Validation

All user inputs are validated before processing:

#### Username Validation
```python
def validate_username(username):
    - Length: 3-20 characters
    - Characters: Alphanumeric only
    - No special characters or spaces
```

#### Email Validation
```python
def validate_email(email):
    - Format: standard email regex pattern
    - Maximum length: 120 characters
```

#### Password Validation
```python
def validate_password(password):
    - Minimum 8 characters
    - At least one letter
    - At least one number
```

#### Text Sanitization
```python
def sanitize_input(text, max_length):
    - Strip whitespace
    - Limit length
    - Remove potentially dangerous characters
```

### 3. SQL Injection Prevention

- **ORM Usage**: SQLAlchemy ORM prevents SQL injection by parameterizing queries
- **No Raw SQL**: All database operations use ORM methods
- **Input Sanitization**: All inputs are sanitized before database operations

**Example Safe Query:**
```python
# Safe - Using ORM
user = User.query.filter_by(username=username).first()

# Unsafe (not used) - Raw SQL
# cursor.execute(f"SELECT * FROM users WHERE username = '{username}'")
```

### 4. Cross-Site Scripting (XSS) Prevention

- **Input Sanitization**: All text inputs are sanitized
- **Output Encoding**: JSON responses automatically encode special characters
- **Content-Type Headers**: Proper content-type headers prevent browser misinterpretation
- **CORS Configuration**: Configured to allow specific origins only

### 5. Rate Limiting

#### IP-Based Rate Limiting
Prevents abuse and DoS attacks:

**Endpoints and Limits:**
- Registration: 5 requests/minute
- Login: 10 requests/minute
- Voting: 20 requests/minute
- Anonymous Voting: 10 requests/minute
- Other APIs: 100 requests/minute

**Implementation:**
```python
@rate_limit(max_requests=10, window_seconds=60)
def protected_endpoint():
    pass
```

#### Vote Integrity
- **Authenticated Users**: Database check + Redis cache
- **Anonymous Users**: IP-based tracking
- **Cache Duration**: 1 hour for vote tracking

### 6. Database Security

#### Connection Security
- **Environment Variables**: Database credentials stored in environment variables
- **Connection Pooling**: SQLAlchemy manages connection pooling
- **SSL/TLS**: Support for encrypted database connections

#### Data Integrity
- **Foreign Keys**: Proper foreign key constraints
- **Indexes**: Performance indexes on frequently queried columns
- **Transactions**: ACID-compliant transactions

### 7. API Gateway Security

#### Service Isolation
- **Internal Network**: Services communicate over internal Docker network
- **External Access**: Only gateway exposed to external traffic
- **Service Authentication**: Services validate JWT tokens independently

#### Request Validation
- **Header Validation**: Checks for required headers
- **Timeout Handling**: 10-second timeout for service requests
- **Error Handling**: Graceful error responses without exposing internals

### 8. Docker Security

#### Container Isolation
- **Non-root User**: Services run as non-root user (recommended enhancement)
- **Network Isolation**: Dedicated Docker network for services
- **Volume Permissions**: Proper permissions on mounted volumes

#### Secret Management
- **Environment Variables**: Secrets passed via environment variables
- **No Hardcoded Secrets**: All secrets configurable
- **.env Files**: Use .env files for local development (not committed)

## Security Best Practices for Production

### 1. Change Default Credentials
```bash
# Update these in production
JWT_SECRET_KEY="use-a-strong-random-key-here"
POSTGRES_PASSWORD="strong-database-password"
```

### 2. Enable HTTPS
```nginx
# Use reverse proxy with SSL
server {
    listen 443 ssl;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8080;
    }
}
```

### 3. Configure CORS Properly
```python
# Restrict to specific domains
CORS(app, origins=["https://yourdomain.com"])
```

### 4. Database Security
```bash
# Use strong passwords
POSTGRES_PASSWORD="$(openssl rand -base64 32)"

# Enable SSL for database connections
DATABASE_URL="postgresql://user:pass@host:5432/db?sslmode=require"
```

### 5. Monitoring and Logging
```python
# Implement proper logging
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Log security events
logger.info(f"Login attempt from {ip_address}")
logger.warning(f"Failed login for user {username}")
```

### 6. Regular Updates
- Keep dependencies updated
- Monitor security advisories
- Apply security patches promptly

### 7. Backup Strategy
```bash
# Regular database backups
docker exec secvote-postgres pg_dump -U secvote secvote_db > backup.sql
```

## Vulnerability Prevention

### Prevented Vulnerabilities

✅ **SQL Injection**: ORM usage and input validation  
✅ **XSS**: Input sanitization and output encoding  
✅ **CSRF**: JWT tokens (stateless authentication)  
✅ **Brute Force**: Rate limiting on login/registration  
✅ **Session Hijacking**: JWT expiration and validation  
✅ **DoS**: Rate limiting on all endpoints  
✅ **Information Disclosure**: Generic error messages  

### Security Testing Checklist

- [ ] Test authentication with invalid tokens
- [ ] Attempt SQL injection in all inputs
- [ ] Test XSS with script tags in inputs
- [ ] Verify rate limiting works
- [ ] Test duplicate vote prevention
- [ ] Verify password hashing
- [ ] Test authorization (accessing other users' resources)
- [ ] Check for information leakage in errors
- [ ] Verify CORS configuration
- [ ] Test with expired JWT tokens

## Incident Response

### If a Security Issue is Found

1. **Report**: Create a security advisory on GitHub
2. **Assess**: Evaluate the severity and impact
3. **Patch**: Develop and test a fix
4. **Deploy**: Roll out the security patch
5. **Notify**: Inform users if necessary
6. **Review**: Conduct post-incident review

## Security Audit Recommendations

For production deployment:

1. **Third-Party Security Audit**: Hire security professionals
2. **Penetration Testing**: Test for vulnerabilities
3. **Code Review**: Security-focused code review
4. **Dependency Scanning**: Use tools like Snyk or Dependabot
5. **OWASP Compliance**: Follow OWASP Top 10 guidelines

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [Flask Security](https://flask.palletsprojects.com/en/2.3.x/security/)
- [bcrypt Documentation](https://pypi.org/project/bcrypt/)
