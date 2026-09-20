# Contributing

## Submit from Pi-MFX

1. Open **Community Presets → Share Preset**.
2. Enter the author, license, description, and tags.
3. Select **Create Manifest**.
4. Select **Submit for Review**. Pi-MFX downloads the JSON manifest and opens the [submission form](https://github.com/MegaNoob75/Pi-MFX-Community-Presets/issues/new?template=community-preset-submission.yml).
5. Attach the downloaded JSON file and submit the form.

The intake issue is the quarantine boundary: it cannot change the catalog. A maintainer reviews the attachment, proposes accepted data through a pull request, waits for GitHub Actions to pass, and then approves the merge. No GitHub credential is stored on a Pi-MFX device.

## Allowed package content

- Versioned Pi-MFX preset and snapshot data
- Controller assignments, tempo, and gain settings
- LV2 URIs from the trusted Pi-MFX plugin catalog
- TONE3000 model IDs, architecture, expected filename, and checksum
- Stable identifiers from supported IR providers
- Author, description, tags, license, compatibility, and checksums

## Never allowed

Plugins, NAM/AIDA-X model files, IR files, executables, scripts, installer commands, HTML, JavaScript, SVG, symlinks, path traversal, secrets, credentials, or arbitrary download URLs.

## Approval checks

Approval requires strict schema and content validation, dependency review, checksum verification, duplicate detection, a passing catalog workflow, and human review. Untrusted submission attachments are never executed.
