
# 🔐 SECURITY.md

## Security Overview

This project was designed with a security-oriented backend architecture and implements multiple protections against common web application threats.


## 🔑 Authentication & Access Control

### Password Hashing

Passwords are hashed using:

- bcrypt

Features:

- Automatic salting
- Adaptive hashing cost
- No plaintext password storage


### Email Verification

Users must verify their email before accessing protected operations.

Verification uses:

- Signed timed tokens via `itsdangerous`

Benefits:

- Prevents fake account abuse
- Reduces spam registrations

### Password Reset Tokens

Password reset links:

- Are cryptographically signed
- Expire automatically
- Cannot be reused indefinitely

### RBAC (Role-Based Access Control)

Administrative routes are isolated through Flask Blueprints.

Unauthorized users cannot access:

```text
/admin/*
````

## Global Ban Enforcement

Suspended users are automatically logged out through:

```python
before_app_request
```

This prevents access even with active sessions.

## 🛡️ Web Attack Protection

### CSRF Protection

All forms are protected using Flask-WTF CSRF tokens.

Mitigates:

* Cross-Site Request Forgery

### Rate Limiting

Authentication endpoints use Flask-Limiter.

Example protections:

* Login brute-force mitigation
* Credential stuffing prevention

### SQL Injection Prevention

Database interactions use SQLAlchemy ORM.

Benefits:

* Parameterized queries
* No raw SQL concatenation
* Automatic escaping

### Input Validation

All form inputs are validated server-side.

Validation includes:

* Email format
* Required fields
* Length restrictions
* Data types

## 🔒 Session & Sensitive Data Security

### Environment Variables

Sensitive values are stored outside source code.

Examples:

* SECRET_KEY
* Mail credentials
* Database configuration

### Secure Session Handling

User sessions are managed through Flask-Login.

Protected routes automatically redirect unauthenticated users.

## ⚙️ Business Logic Security

### Donation Cooldown Protection

The platform enforces:

* 90-day cooldown between donations

Prevents:

* Spam submissions
* Abuse of donation workflow

### Request Cooldown Protection

The platform enforces:

* 7-day cooldown between blood requests

Prevents:

* Resource abuse
* Excessive request spam

### Notification Permission Enforcement

Email notifications are only sent if:

```python
user.email_notifications == True
```

The system avoids unnecessary database queries by using authenticated user objects directly.

## 🔍 Security Design Principles

The application follows several defensive programming practices:

* Service-layer architecture
* Separation of concerns
* Explicit authorization checks
* Minimal database exposure
* Centralized business rules
* Safe form handling

## 🧪 Security Testing Goals

Planned future security validation includes:

* Manual penetration testing
* OWASP Top 10 review
* Authentication testing
* Authorization bypass testing
* Session manipulation testing
* Business logic abuse testing

## ⚠️ Current Limitations

Current limitations intentionally accepted for portfolio scope:

* SQLite instead of PostgreSQL
* No MFA
* No distributed rate limiting
* No production WAF/reverse proxy
* No centralized SIEM logging

## 📚 Security References

* OWASP Top 10
* Flask Security Best Practices
* NIST Password Guidelines
* OWASP ASVS

