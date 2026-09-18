# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),\
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-09-18
### Changed
- **BREAKING**: RepoGallery is now installed as a GitHub Action (`anlit75/RepoGallery@v1`)\
  instead of by forking. Your repository holds three files; the generator stays upstream,\
  so upgrades no longer produce merge conflicts. See "Migrating from a fork" in the README.
- `generate_html.py` now takes `--config`, `--templates`, `--output` and `--assets`\
  instead of assuming the repository root as the working directory.
- The site is written to `public/` with `css/`, `js/` and `img/` beside it; template paths\
  are no longer versioned, so `site.version` was removed from `config.yaml`.

### Added
- Regression tests (`tests/`) and a CI workflow running them on every pull request.
- A release workflow that moves the floating major tag, so patches reach pinned users.

### Changed
- Pinned actions moved to the releases that run on Node.js 24, ahead of the Node.js 20
  runner deprecation: `checkout@v5`, `setup-python@v6`, `upload-pages-artifact@v5` and
  `deploy-pages@v5`. `upload-pages-artifact` now excludes dotfiles from the artifact by
  default; pass `include-hidden-files: true` if your site needs them.

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