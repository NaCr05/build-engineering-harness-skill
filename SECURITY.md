# Security Policy

## Supported versions

Active maintenance is paused as of 2026-08-06. No version currently receives a committed security-fix or response-time guarantee. The latest published Beta remains available as-is; [GitHub Releases](https://github.com/NaCr05/build-engineering-harness-skill/releases) is the source of truth for publication and download status.

The current repository version is `0.3.4-beta`. A version appearing on `main`, in `VERSION`, or in release-preparation documentation does not by itself mean that it is published or supported.

| Release class | Availability and support |
|---|---|
| Latest published Beta | Available as-is; no fix or response SLA |
| Draft or otherwise unpublished candidate | Not supported |
| Older Beta or superseded candidate | Not supported |

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

Private reports remain welcome, but they may remain unacknowledged or unresolved until active maintenance resumes. There is no promised acknowledgement, triage, remediation, release, or disclosure timeline during the maintenance pause. Users who require an actively supported security posture should review and pin the exact release and its attestations before use, or maintain a reviewed fork.
