# Contributing

Direct preset uploads and pull requests are not accepted yet.

When the Milestone 5 quarantine service is available, Pi-MFX will generate a manifest from the active preset and submit it for automated validation and human review. Only the publishing bot may add approved packages to `presets/`.

## Allowed package content

- Versioned Pi-MFX preset and snapshot data
- Controller assignments, tempo, and gain settings
- LV2 URIs from the trusted Pi-MFX plugin catalog
- TONE3000 model IDs, architecture, expected filename, and checksum
- Stable identifiers from supported IR providers
- Author, description, tags, license, compatibility, and checksums
- Optional preview media that the quarantine service has decoded and safely re-encoded

## Never allowed

Plugins, NAM/AIDA-X model files, IR files, executables, scripts, installer commands, HTML, JavaScript, SVG, symlinks, path traversal, secrets, credentials, or arbitrary download URLs.

Approval requires schema validation, archive-safety checks, malware scanning, duplicate detection, clean-package reconstruction, isolated Pi-MFX test loading, and human review.
