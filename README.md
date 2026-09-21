# Pi-MFX Community Presets

This repository is the public catalog of approved community presets for [Pi-MFX](https://github.com/MegaNoob75/Pi-MFX).

## Submit and approve

1. Pi-MFX exports a declarative JSON manifest and opens the [submission form](https://github.com/MegaNoob75/Pi-MFX-Community-Presets/issues/new?template=community-preset-submission.yml).
2. GitHub validates the attachment without executing it.
3. A maintainer applies the **approved-for-pr** label.
4. GitHub creates an isolated pull request containing the manifest and catalog entry.
5. The catalog check must pass and a human must merge the pull request.
6. GitHub closes the intake issue and deletes the temporary submission branch after merge.

## Security model

- Submissions are JSON data only.
- Plugins, models, IRs, audio, executables, scripts, installers, HTML, SVG, symlinks, and arbitrary download URLs are rejected.
- TONE3000 and other supported assets are referenced only by stable provider IDs, filenames, and checksums.
- Untrusted issue content is never executed.
- No personal GitHub token or publishing credential is stored on a Pi.
- Pi-MFX shows an installation plan before changing a device.
- Imports create a new Community bank and never overwrite user data.

## Layout

- `schema/` — the versioned manifest schema.
- `catalog/index.json` — the machine-readable catalog index.
- `presets/` — approved data-only manifests.
- `.github/scripts/catalog_guard.py` — trusted validation and catalog preparation.
- `.github/workflows/` — submission processing and catalog validation.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the review workflow.
