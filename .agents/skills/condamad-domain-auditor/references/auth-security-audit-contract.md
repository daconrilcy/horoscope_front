# Auth Security Audit Contract

Audit must verify:

- authentication boundary;
- unauthorized vs forbidden behavior;
- token/session handling;
- password/secret handling when applicable;
- negative tests for unauthorized paths;
- no auth bypass through internal services;
- sensitive data not leaked in errors/logs.

Use OWASP ASVS as reference for security verification coverage. OWASP ASVS is a recognized basis for verifying web application controls across architecture, authentication, session management, access control, API services, configuration, logging, and business logic. OWASP access control principles are directly applicable: subjects may access objects and actions only according to policy.
