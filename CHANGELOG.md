# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),\
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.1] - 2026-09-19
### Fixed
- Restored `actions/configure-pages` in the deploy job, at `v6` for the Node.js 24 runtime.
  The pre-2.0.0 workflow had it and the migration dropped it. It does not remove the manual
  "Settings > Pages > Source: GitHub Actions" step — `enablement` needs a token other than
  `GITHUB_TOKEN` — but it fails with a readable message when that step was skipped, rather
  than leaving `deploy-pages` to fail later for an unclear reason.

## [2.1.0] - 2026-09-18
### Changed
- Dependencies are now declared in `pyproject.toml` and resolved by uv, with `uv.lock`
  committed. `requirements.txt` is generated from that lock with
  `uv export --no-dev --no-emit-project` and carries exact versions and hashes, so every
  user's build installs the same artifacts instead of whatever `~=` resolves to that day.
- `action.yml` is unchanged and still installs `requirements.txt` with pip: uv stays a
  maintainer tool, and users gain no third-party action in their workflow.
- CI runs `uv run --locked --dev pytest` and fails if `requirements.txt` has drifted
  from `uv.lock`.

### Removed
- `requirements-dev.txt`, replaced by the `dev` dependency group in `pyproject.toml`.

## [2.0.1] - 2026-09-18
### Fixed
- `examples/starter/assets/custom_image.yaml` still mapped `RepoGallery` to an image that
  only exists in this repository, so anyone who kept the default repository name got a
  broken card image instead of a random one.

### Added
- `tests/test_starter.py`, which generates a site from `examples/starter` with the workspace
  and the action path in separate directories and asserts every local reference resolves.
  `demo.yml` cannot catch this: `uses: ./` makes those two directories the same one.

## [2.0.0] - 2026-09-18
### Changed
- **BREAKING**: RepoGallery is now installed as a GitHub Action (`anlit75/RepoGallery@v2`)\
  instead of by forking. Your repository holds three files; the generator stays upstream,\
  so upgrades no longer produce merge conflicts.

  Migrating a fork-based install: in your fork, delete everything except `config.yaml` and
  `assets/custom_image.yaml`, copy in `examples/starter/.github/workflows/gallery.yml`,
  remove the `site.version` key from your `config.yaml`, then commit and push. Your Pages
  URL and your settings are preserved.
- `generate_html.py` now takes `--config`, `--templates`, `--output` and `--assets`\
  instead of assuming the repository root as the working directory.
- The site is written to `public/` with `css/`, `js/` and `img/` beside it; template paths\
  are no longer versioned, so `site.version` was removed from `config.yaml`.

- Pinned actions moved to the releases that run on Node.js 24, ahead of the Node.js 20
  runner deprecation: `checkout@v5`, `setup-python@v6`, `upload-pages-artifact@v5` and
  `deploy-pages@v5`. `upload-pages-artifact` now excludes dotfiles from the artifact by
  default; pass `include-hidden-files: true` if your site needs them.

### Added
- Regression tests (`tests/`) and a CI workflow running them on every pull request.
- A release workflow that moves the floating major tag, so patches reach pinned users.

### Fixed
- Only the first 30 repositories were ever fetched; the API is now paginated.
- Pull request counts were requested unauthenticated and silently fell back to 0.
- Repository metadata was interpolated into the page unescaped; autoescape is now on and the
  Live Demo button no longer builds inline JavaScript from the homepage URL.
- The footer mail icon read an undefined variable (`{{ mail }}`) and always produced an
  empty `mailto:`; it now uses the same address as the footer contact row.
- An unknown `random_image_theme` crashed the generator instead of falling back to text cards.
- `sort.descending` from `config.yaml` was ignored by the front-end sort menu.

### Removed
- `sync.sh` and `.gitattributes`: both tried to preserve `config.yaml` across upstream merges
  and neither worked. `sync.sh` kept the upstream file rather than yours, and `merge=theirs`
  is not a built-in git driver. Upgrades no longer touch your files at all.
- The dead README-image scraper, which cost two HTTP requests per repository and whose only
  consumer had been commented out.

## [1.2.0] - 2025-02-21
### Added
- Added a new exclusion mechanism in `config.yaml` that allows repositories to be excluded\
  using regular expressions, in addition to specifying full repository names.

### Changed
- Changed the synchronization mechanism to rebase the `main` branch instead of merging it.

### Removed
- Removed unnecessary bot commits from GitHub Actions.
- Removed automatic push of `index.html`.

## [1.1.0] - 2025-02-20
### Added
- Added user-configurable image settings, allowing users to define custom images.

### Changed
- When no user-provided image is available and "random image" is disabled,\
  the system now displays a text card instead of using the first image from the repository's README.

### Removed
- Removed the fallback behavior where the first image from the repository's README was used\
  when "random image" is disabled.

## [1.0.0] - 2025-02-16
### Added
- Initial release of RepoGallery.