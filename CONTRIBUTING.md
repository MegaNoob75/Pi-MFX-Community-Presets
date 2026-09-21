# Contributing

## Submit from Pi-MFX

1. Load and save the preset you want to share.
2. Open **Community Presets → Share Preset**.
3. Enter the author, license, description, and tags.
4. Select **Create Manifest**, then **Submit for Review**.
5. Attach the downloaded JSON file to the GitHub form and submit it.

GitHub validates the attachment as data. It does not execute the submission.

## Maintainer approval

1. Wait for the issue comment confirming that validation passed.
2. Review the manifest summary and submission notes.
3. Apply the **approved-for-pr** label.
4. Open the automatically generated pull request.
5. Wait for **Validate catalog** to pass.
6. Review the changed manifest and catalog entry, then merge.

The generated branch is unique to that submission and is deleted automatically when its pull request is merged or closed. Merging closes the intake issue.

## Allowed content

- Pi-MFX preset, snapshot, controller, tempo, and gain settings
- Trusted LV2 effect URIs
- TONE3000 model IDs, architecture, filename, and checksum
- Stable identifiers from supported providers
- Author, description, tags, license, and compatibility metadata

## Rejected content

Plugins, model files, IR files, audio, executables, scripts, installer commands, HTML, JavaScript, SVG, symlinks, path traversal, secrets, credentials, or arbitrary download URLs.

Automation checks structure, paths, identifiers, checksums, and forbidden content. A human remains responsible for authorship, licensing, usefulness, and the final merge.
