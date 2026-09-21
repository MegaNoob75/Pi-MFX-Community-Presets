# Security Policy

Do not submit credentials, tokens, private account data, or confidential filenames.

Community attachments are untrusted data. The submission workflow:

- accepts one GitHub-hosted JSON attachment with a 1 MiB limit;
- validates it against the strict manifest schema and additional content guards;
- never executes submitted content;
- requires a maintainer with repository write access to apply **approved-for-pr**;
- creates a separate temporary branch and pull request;
- requires catalog validation and a human merge;
- deletes the temporary branch after the pull request is closed.

The workflow uses GitHub's short-lived repository token with only the permissions required by each job. No personal GitHub token belongs in this repository or on a Pi-MFX device.

Provider assets are resolved later through Pi-MFX's trusted integrations and verified by checksum. Model, IR, plugin, audio, script, and executable files are not accepted into this catalog.

Report catalog vulnerabilities using GitHub's private security-reporting option rather than a public issue.
