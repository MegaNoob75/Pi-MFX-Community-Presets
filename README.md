# Pi-MFX Community Presets

This repository is the public, read-only catalog of approved community presets for [Pi-MFX](https://github.com/MegaNoob75/Pi-MFX).

## Security model

- Packages are declarative data only.
- Packages may reference trusted LV2 plugin URIs, TONE3000 model IDs, and supported IR provider IDs.
- Packages must not contain plugins, models, IR files, executables, scripts, installer commands, HTML, JavaScript, SVG, symlinks, or arbitrary download URLs.
- Community submissions arrive as JSON attachments on intake issues; an issue is not part of the catalog.
- A maintainer reviews each submission and proposes accepted data through a pull request.
- GitHub Actions must validate the pull request before human approval and merge.
- Pi-MFX displays and confirms an installation plan before changing a device.
- Imports create a new community bank and never overwrite user data.

Use the [community preset submission form](https://github.com/MegaNoob75/Pi-MFX-Community-Presets/issues/new?template=community-preset-submission.yml) to attach a manifest exported by Pi-MFX.

## Layout

- `schema/` — versioned JSON Schemas for clean published manifests.
- `catalog/index.json` — machine-readable catalog index.
- `presets/` — approved packages added only after review.
- `.github/workflows/` — validation applied to catalog changes.

See [CONTRIBUTING.md](CONTRIBUTING.md) for package and review requirements.
