# Security Policy

## Supported versions

Only the latest published Beta receives security fixes.

| Version | Supported |
|---|---|
| `0.1.1-beta` | Yes |
| `0.1.0-beta` and earlier | No |

## Reporting a security issue

Do not include secrets, private repository contents, personal data, or exploitable details in a public issue.

Use GitHub's [private vulnerability reporting form](https://github.com/NaCr05/build-engineering-harness-skill/security/advisories/new). Do not open a public issue for a suspected vulnerability.

Relevant issues include:

- instructions that could expose secrets or private context;
- behavior that bypasses explicit approval boundaries;
- unsafe execution, deployment, migration, or paid-evaluation guidance;
- generated output that misrepresents unverified behavior as verified;
- installation or packaging behavior that writes outside the intended Skill directory.

Include a minimal reproduction, affected files or version, expected behavior, observed behavior, and impact. Remove all real credentials and confidential repository data.

The maintainer will make a best effort to acknowledge a complete report within seven calendar days and provide an initial triage update within fourteen calendar days. Fix and disclosure timing depends on severity and available evidence. Coordinate public disclosure with the maintainer so users have a reasonable opportunity to update.
