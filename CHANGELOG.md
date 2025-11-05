# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- TypeScript code generation support
- Watch mode for auto-regeneration
- Custom template system enhancements
- Integration with popular agent frameworks
- Performance benchmarks
- Docker images

## [0.1.0] - 2025-01-XX

### Added
- Initial release of MCP CodeGen
- Core code generation from MCP servers
- Schema parser with full JSON Schema support
  - Basic types (string, number, integer, boolean)
  - Complex types (array, object)
  - Union types (anyOf, oneOf)
  - Enum/Literal types
  - Optional parameters
- Template renderer with Jinja2 support
  - Tool function templates
  - Package initialization templates
  - MCP client template
  - README generation
- Command-line interface with three commands:
  - `generate` - Generate code from MCP servers
  - `inspect` - Inspect servers without generating
  - `init` - Initialize new agent projects
- Comprehensive test suite
  - Unit tests for schema parser
  - Unit tests for template renderer
  - Integration tests with mock MCP servers
  - 85%+ code coverage
- Documentation
  - Comprehensive README
  - Quick start guide
  - Contributing guidelines
  - Project summary
  - Usage examples (basic and advanced)
- Development tooling
  - Black for formatting
  - Ruff for linting
  - MyPy for type checking
  - GitHub Actions CI/CD
  - Makefile for common tasks
- Python API for programmatic use
- Support for multiple MCP servers in one generation
- Configurable output directories
- Overwrite control for regeneration
- Verbose logging option

### Technical Details
- Requires Python 3.10+
- Uses MCP SDK for server communication
- Async/await support throughout
- Type hints for better IDE support
- Modular architecture for extensibility

## [0.0.1] - Development

### Added
- Initial project structure
- Basic proof of concept
- Core design patterns established

---

## Release Process

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md with release notes
3. Commit changes: `git commit -m "chore: prepare release v0.1.0"`
4. Tag release: `git tag v0.1.0`
5. Push: `git push && git push --tags`
6. Build: `make build`
7. Publish: `make publish` (or `make publish-test` for TestPyPI)

## Version Schema

- **Major version** (X.0.0): Breaking changes
- **Minor version** (0.X.0): New features, backward compatible
- **Patch version** (0.0.X): Bug fixes, backward compatible

## Types of Changes

- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security fixes
