# Security Policy

## Reporting a Vulnerability
1. **Do NOT** open a public issue
2. Email the maintainer directly
3. Include: description, steps to reproduce, potential impact

## Security Measures
- Resume data processed in-memory, not stored permanently
- API keys in environment variables only
- Input validation on all file upload endpoints
- Rate limiting in production
