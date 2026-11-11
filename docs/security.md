# Security & Privacy

## Overview

The Flood Claim Triage MVP handles sensitive reinsurer data including property portfolios, exposure values, and claim priorities. Security and privacy are critical for pilot success and production deployment.

## Threat Model

### Assets to Protect
1. **Property portfolio data**: Locations, exposure values, building types
2. **Claim triage decisions**: Inspection priorities, analyst overrides
3. **User credentials**: Passwords, API tokens
4. **Geospatial data**: Satellite imagery, weather data
5. **Audit trail**: Immutable record of all actions

### Threat Actors
- **External attackers**: SQL injection, credential stuffing, DDoS
- **Malicious insiders**: Data exfiltration, unauthorized access
- **Accidental exposure**: Misconfiguration, logging secrets

### Security Goals
- **Confidentiality**: Unauthorized parties cannot access property data
- **Integrity**: Data cannot be tampered with
- **Availability**: System is accessible to authorized users
- **Auditability**: All actions are logged and traceable
- **Non-repudiation**: Actions cannot be denied by users

## Authentication & Authorization

### JWT-Based Authentication
- **Access tokens**: 30-minute expiration
- **Refresh tokens**: 7-day expiration
- **Algorithm**: HS256 (symmetric signing)
- **Secret rotation**: Manual (planned: automatic every 90 days)

**Token Storage**:
- Frontend: `localStorage` (XSS risk mitigated by CSP)
- Backend: Never stored (stateless validation)

**Token Validation**:
- Signature verification
- Expiration check
- Token type check (access vs. refresh)
- User active status check

### Role-Based Access Control (RBAC)

| Role | Permissions |
|------|------------|
| **admin** | Full system access, user management, event creation, scoring |
| **analyst** | Event creation, scoring, triage review, overrides |
| **reviewer** | Triage review, overrides, read-only access to all data |
| **viewer** | Read-only access to triage queue and evidence |

**Enforcement**:
- Backend: Decorator-based route protection
- Frontend: UI element hiding (not security boundary)
- Database: No direct user access (all via API)

### Password Security
- **Hashing**: bcrypt with cost factor 12
- **Minimum length**: 8 characters
- **Complexity**: Not enforced in MVP (recommend: upper, lower, digit, symbol)
- **Password reset**: Not implemented in MVP (manual via admin)

## Transport Security

### TLS Configuration
- **Development**: HTTP (localhost only)
- **Production**: TLS 1.3 only
- **Certificates**: Let's Encrypt or AWS ACM
- **HSTS**: Enabled with 1-year max-age

### API Security
- **CORS**: Whitelist of allowed origins only
- **Content Security Policy**: Strict CSP headers
- **X-Frame-Options**: DENY (prevent clickjacking)
- **X-Content-Type-Options**: nosniff

## Data Security

### Encryption at Rest
- **Database**: Encrypted volumes (AES-256)
- **Object Storage**: Server-side encryption (S3-SSE or equivalent)
- **Backups**: Encrypted with separate key

### Encryption in Transit
- **All API calls**: HTTPS only in production
- **Database connections**: TLS enforced
- **Object storage**: HTTPS URLs only

### Data Minimization
- **No raw addresses**: Only hashed addresses stored
- **Optional PII**: Exposure value not required
- **Pseudonymization**: External property IDs used instead of internal identifiers
- **Scrubbing**: Logs sanitized to remove secrets and PII

### Data Retention
- **Properties**: Retained indefinitely (business need)
- **Events**: Retained indefinitely
- **Scores**: Retained for 7 years (regulatory requirement)
- **Audit logs**: Retained for 7 years (immutable)
- **Deleted properties**: Cascade delete all linked records (GDPR right to deletion)

## Secrets Management

### Environment Variables
All secrets configured via environment variables, never in code:
- `JWT_SECRET`: JWT signing key
- `DATABASE_URL`: Database connection string
- `S3_ACCESS_KEY` / `S3_SECRET_KEY`: Object storage credentials

### Secrets Injection
- **Development**: `.env` file (gitignored)
- **Production**: AWS Secrets Manager, GCP Secret Manager, or HashiCorp Vault
- **CI/CD**: GitHub Secrets

### Secret Rotation
- **JWT secret**: Manual rotation (planned: 90-day automatic)
- **Database password**: Manual rotation (planned: 90-day automatic)
- **S3 keys**: Manual rotation (planned: 90-day automatic)

## Audit & Logging

### Audit Trail
All write operations logged to `audit_events` table:
- User ID and timestamp
- Action type (accept, override, export, etc.)
- Before/after values (for overrides)
- Reason (user-provided)
- Immutable (no updates or deletes)

### Application Logs
Structured JSON logging with:
- Timestamp (ISO 8601)
- Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- User ID (if authenticated)
- Request ID (trace correlation)
- Message

**Never log**:
- Passwords (plain or hashed)
- JWT tokens
- API keys
- Raw property addresses
- Full credit card numbers

### Log Aggregation
- **Development**: stdout (Docker logs)
- **Production**: CloudWatch, Datadog, or ELK stack
- **Retention**: 90 days

### Security Monitoring
- Failed login attempts (rate limiting)
- Unusual override rates
- Bulk export operations
- Database connection errors
- Token validation failures

## Vulnerability Management

### Dependency Scanning
- **Backend**: `pip-audit` weekly
- **Frontend**: `npm audit` weekly
- **Docker images**: Trivy or Snyk scan

### Patch Management
- Critical vulnerabilities: Patch within 7 days
- High vulnerabilities: Patch within 30 days
- Medium/low: Patch in next release

### Penetration Testing
- Not conducted for MVP
- Recommended before production launch

### Bug Bounty
- Not implemented for MVP
- Consider for public-facing production

## Secure Development Practices

### Code Review
- All changes reviewed by second developer
- Security-focused review for auth/access control changes

### Input Validation
- All API inputs validated with Pydantic schemas
- SQL injection prevented via parameterized queries (SQLAlchemy ORM)
- XSS prevented via React auto-escaping

### Output Encoding
- JSON responses (no HTML rendering)
- CSV export: sanitize formulas (prevent CSV injection)

### Error Handling
- Generic error messages to users (prevent information disclosure)
- Detailed errors logged server-side
- No stack traces in production API responses

### Secure Defaults
- Authentication required by default
- Least-privilege role assignment
- TLS enforced in production
- CORS whitelist (not wildcard)

## Incident Response

### Detection
- Monitor for:
  - Failed login spikes
  - Unusual API patterns
  - Database connection failures
  - High override rates

### Response Plan
1. **Identify**: Detect anomaly via monitoring
2. **Contain**: Disable affected user accounts, block IPs if needed
3. **Eradicate**: Patch vulnerability, rotate compromised credentials
4. **Recover**: Restore from backup if needed, re-enable service
5. **Lessons Learned**: Post-mortem and process improvement

### Communication
- Pilot team notified within 1 hour
- Stakeholders notified within 4 hours
- Users notified within 24 hours (if data exposure)

## Compliance & Regulations

### GDPR (if applicable)
- **Right to access**: API endpoint for user data export
- **Right to deletion**: Cascade delete of all user-linked records
- **Data minimization**: No unnecessary PII collection
- **Consent**: Users agree to terms on first login

### SOC 2 (future)
- Audit trail for all actions
- Access control logs
- Encrypted at rest and in transit
- Backup and disaster recovery

### Industry Standards
- OWASP Top 10 compliance
- NIST Cybersecurity Framework alignment

## Data Flow & Trust Boundaries

```
┌──────────────────────────────────────────────────────────┐
│  User Browser (Untrusted)                                │
│  - Credentials entered                                   │
│  - JWT stored in localStorage                            │
└──────────────────────────────────────────────────────────┘
                    │ HTTPS (TLS 1.3)
                    ▼
┌──────────────────────────────────────────────────────────┐
│  API Gateway / Load Balancer (Trusted Boundary)          │
│  - TLS termination                                       │
│  - Rate limiting                                         │
│  - DDoS protection                                       │
└──────────────────────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────────────────┐
│  FastAPI Application (Trusted)                           │
│  - JWT validation                                        │
│  - RBAC enforcement                                      │
│  - Input validation                                      │
│  - Audit logging                                         │
└──────────────────────────────────────────────────────────┘
         │                        │                    │
         ▼                        ▼                    ▼
┌────────────────┐  ┌─────────────────────┐  ┌──────────────┐
│  PostgreSQL    │  │  S3 / MinIO         │  │  External    │
│  (Encrypted)   │  │  (Encrypted)        │  │  APIs        │
│  - TLS conn    │  │  - Presigned URLs   │  │  - API keys  │
└────────────────┘  └─────────────────────┘  └──────────────┘
```

## Security Checklist (Pre-Production)

- [ ] TLS 1.3 enforced
- [ ] JWT secret rotated from default
- [ ] Database password strong and rotated
- [ ] S3 bucket not public
- [ ] CORS whitelist configured
- [ ] Rate limiting enabled
- [ ] Secrets in secrets manager (not env vars)
- [ ] Logs sanitized (no secrets, no PII)
- [ ] Backups encrypted and tested
- [ ] Vulnerability scan passed
- [ ] Penetration test completed
- [ ] Incident response plan documented
- [ ] User training on security best practices
- [ ] Data retention policy documented
- [ ] Privacy policy and terms of service published

## Contact

**Security Issues**: Report via email to `security@example.com`

**Response Time**: 24 hours for critical, 72 hours for non-critical

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [GDPR Guidelines](https://gdpr.eu/)
- [FastAPI Security Best Practices](https://fastapi.tiangolo.com/tutorial/security/)
