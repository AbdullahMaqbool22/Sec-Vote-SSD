# Production Deployment Checklist

Use this checklist before deploying Sec-Vote to production.

## Security Configuration

### Secrets and Keys
- [ ] Generate strong JWT_SECRET_KEY (min 32 random characters)
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
- [ ] Change default database password
- [ ] Change default Redis password (if exposed)
- [ ] Store secrets in secure vault (AWS Secrets Manager, HashiCorp Vault, etc.)
- [ ] Never commit `.env` file to version control

### Application Security
- [ ] Set `FLASK_DEBUG=False` in all services
- [ ] Set `FLASK_ENV=production` in all services
- [ ] Configure CORS to allow only your frontend domain
  ```python
  CORS(app, origins=["https://yourdomain.com"])
  ```
- [ ] Review and adjust rate limiting thresholds
- [ ] Enable HTTPS only (no HTTP)
- [ ] Set secure cookie flags if using sessions

## Infrastructure

### Database
- [ ] Use managed PostgreSQL service (AWS RDS, Google Cloud SQL, etc.)
- [ ] Enable SSL/TLS for database connections
- [ ] Set up automated backups
- [ ] Configure backup retention policy
- [ ] Test restore procedure
- [ ] Enable point-in-time recovery
- [ ] Set up connection pooling
- [ ] Configure proper resource limits (RAM, CPU)

### Redis
- [ ] Use managed Redis service (AWS ElastiCache, Redis Cloud, etc.)
- [ ] Enable password authentication
- [ ] Configure maxmemory policy
- [ ] Set up persistence (AOF or RDB)
- [ ] Configure proper eviction policy

### Container Orchestration
- [ ] Use Kubernetes or ECS for production
- [ ] Set resource limits for containers
  ```yaml
  resources:
    limits:
      cpu: "1"
      memory: "512Mi"
    requests:
      cpu: "0.5"
      memory: "256Mi"
  ```
- [ ] Configure health checks for all services
- [ ] Set up auto-scaling policies
- [ ] Configure rolling update strategy

## Network & Load Balancing

### Reverse Proxy
- [ ] Set up Nginx or HAProxy as reverse proxy
- [ ] Configure SSL/TLS certificates (Let's Encrypt recommended)
- [ ] Enable HTTP/2
- [ ] Set up SSL best practices (A+ rating on SSL Labs)
- [ ] Configure request timeout
- [ ] Add security headers
  ```nginx
  add_header X-Frame-Options "SAMEORIGIN";
  add_header X-Content-Type-Options "nosniff";
  add_header X-XSS-Protection "1; mode=block";
  add_header Strict-Transport-Security "max-age=31536000";
  ```

### Load Balancing
- [ ] Set up load balancer for API Gateway
- [ ] Configure health checks
- [ ] Set up sticky sessions if needed
- [ ] Configure connection draining

## Monitoring & Logging

### Application Monitoring
- [ ] Set up APM (New Relic, DataDog, or Prometheus)
- [ ] Monitor response times
- [ ] Track error rates
- [ ] Set up alerts for high error rates
- [ ] Monitor service health
- [ ] Track database query performance

### Logging
- [ ] Centralize logs (ELK stack, Splunk, or CloudWatch)
- [ ] Set appropriate log levels
- [ ] Implement log rotation
- [ ] Set up log retention policy
- [ ] Remove sensitive data from logs
- [ ] Set up alerts for critical errors

### Metrics to Track
- [ ] Request rate per endpoint
- [ ] Response time (p50, p95, p99)
- [ ] Error rate (4xx, 5xx)
- [ ] Database connection pool usage
- [ ] Redis cache hit rate
- [ ] Active users
- [ ] Votes per minute
- [ ] Poll creation rate

## Performance

### Optimization
- [ ] Enable database query caching
- [ ] Add database indexes for slow queries
- [ ] Optimize Redis cache expiration times
- [ ] Enable gzip compression in reverse proxy
- [ ] Implement CDN for static content (if any)
- [ ] Consider database read replicas for high load

### Testing
- [ ] Run load tests to determine capacity
- [ ] Test auto-scaling triggers
- [ ] Perform stress testing
- [ ] Test failover scenarios
- [ ] Benchmark database queries

## Backup & Recovery

### Backup Strategy
- [ ] Database: automated daily backups
- [ ] Database: weekly full backups
- [ ] Keep backups for 30 days minimum
- [ ] Store backups in different region/zone
- [ ] Test backup restoration monthly
- [ ] Document recovery procedures

### Disaster Recovery
- [ ] Create runbook for common incidents
- [ ] Set up monitoring alerts
- [ ] Configure automatic failover if possible
- [ ] Define RTO (Recovery Time Objective)
- [ ] Define RPO (Recovery Point Objective)
- [ ] Document escalation procedures

## Testing

### Pre-deployment Testing
- [ ] Run all unit tests
- [ ] Run integration tests
- [ ] Perform security scan (CodeQL, Snyk, etc.)
- [ ] Test in staging environment
- [ ] Perform load testing
- [ ] Test backup and restore
- [ ] Verify monitoring and alerts work

### Security Testing
- [ ] Run penetration testing
- [ ] Perform security audit
- [ ] Test authentication flows
- [ ] Verify authorization rules
- [ ] Test rate limiting
- [ ] Check for exposed secrets
- [ ] Verify HTTPS enforcement

## Documentation

### Operations
- [ ] Document deployment procedure
- [ ] Create runbook for common tasks
- [ ] Document rollback procedure
- [ ] Create incident response plan
- [ ] Document monitoring dashboard
- [ ] Create on-call procedures

### Developer
- [ ] Update API documentation
- [ ] Document environment variables
- [ ] Create troubleshooting guide
- [ ] Document architecture changes
- [ ] Update README with production notes

## Compliance & Legal

### Data Privacy
- [ ] Review data collection practices
- [ ] Implement data retention policy
- [ ] Add privacy policy
- [ ] Add terms of service
- [ ] Implement GDPR compliance (if applicable)
- [ ] Add data export functionality
- [ ] Add data deletion functionality

### Security
- [ ] Set up security incident response plan
- [ ] Configure security audit logging
- [ ] Set up intrusion detection
- [ ] Implement rate limiting
- [ ] Add IP blocking capability

## Deployment

### Pre-deployment
- [ ] Review this entire checklist
- [ ] Create deployment plan
- [ ] Schedule maintenance window
- [ ] Notify users of maintenance
- [ ] Prepare rollback plan
- [ ] Back up current production state

### Deployment Steps
- [ ] Deploy to staging first
- [ ] Verify staging works correctly
- [ ] Create production backup
- [ ] Deploy to production
- [ ] Run smoke tests
- [ ] Monitor for errors
- [ ] Verify all services are healthy

### Post-deployment
- [ ] Monitor error rates
- [ ] Check performance metrics
- [ ] Verify logging is working
- [ ] Test critical user flows
- [ ] Update documentation
- [ ] Communicate deployment success
- [ ] Keep rollback plan ready for 24 hours

## Maintenance

### Regular Tasks
- [ ] Weekly: Review error logs
- [ ] Weekly: Check performance metrics
- [ ] Monthly: Review security alerts
- [ ] Monthly: Test backup restoration
- [ ] Quarterly: Rotate secrets
- [ ] Quarterly: Security audit
- [ ] Yearly: Penetration testing

### Updates
- [ ] Keep dependencies updated
- [ ] Apply security patches promptly
- [ ] Review and update documentation
- [ ] Test updates in staging first
- [ ] Schedule regular update windows

## Cost Optimization

- [ ] Right-size database instances
- [ ] Right-size Redis instances
- [ ] Set up auto-scaling to scale down during low traffic
- [ ] Review and optimize cloud resource usage
- [ ] Set up billing alerts
- [ ] Review unused resources monthly

## Sign-off

Before going live, get sign-off from:
- [ ] Development Team Lead
- [ ] Security Team
- [ ] Operations Team
- [ ] Product Owner
- [ ] CTO/Technical Director

---

## Quick Security Verification

Run these commands before production:

```bash
# 1. No debug mode
grep -r "debug=True" services/ gateway/
# Should return nothing

# 2. No hardcoded secrets
grep -r "password.*=" --include="*.py" | grep -v "password_hash"
# Review results carefully

# 3. Environment variables set
env | grep -E "(JWT_SECRET|DATABASE|REDIS)"

# 4. All tests pass
pytest tests/ -v

# 5. Security scan
python -m pip install safety
safety check
```

## Emergency Contacts

Document emergency contacts:
- [ ] On-call engineer: _______________
- [ ] Database admin: _______________
- [ ] Security team: _______________
- [ ] Cloud provider support: _______________

## Rollback Procedure

If deployment fails:
1. Stop traffic to new version
2. Switch back to previous version
3. Restore database if needed
4. Verify system is stable
5. Investigate issue
6. Create incident report

---

**Last Updated**: Before each production deployment  
**Review Frequency**: Before each deployment  
**Owner**: DevOps/Operations Team
