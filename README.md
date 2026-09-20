# Pi-MFX Community Presets

This repository is the public, read-only catalog of approved community presets for [Pi-MFX](https://github.com/MegaNoob75/Pi-MFX).

## Security model

- Packages are declarative data only.
- Packages may reference trusted LV2 plugin URIs, TONE3000 model IDs, and supported IR provider IDs.
- Packages must not contain plugins, models, IR files, executables, scripts, installer commands, HTML, JavaScript, SVG, symlinks, or arbitrary download URLs.
- Community submissions do not write directly to this repository. They enter a quarantine and review service first.
- A publishing bot will eventually be the only automated writer.
- Pi-MFX must display and confirm an installation plan before changing a device.
- Imports create a new community bank and never overwrite user data.

The catalog is currently being bootstrapped for Milestone 5. Do not submit presets until the quarantine submission flow is available.

## Layout

- `schema/` — versioned JSON Schemas for clean published manifests.
- `catalog/index.json` — machine-readable catalog index.
- `presets/` — approved packages, added only by the publishing process.
- `.github/workflows/` — validation applied to catalog changes.

See [CONTRIBUTING.md](CONTRIBUTING.md) for package and review requirements.
