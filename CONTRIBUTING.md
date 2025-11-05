# Contributing to MCP CodeGen

Thank you for your interest in contributing to MCP Agent Tools! This document provides guidelines for contributing to the project.

## Development Setup

1. **Clone the repository**
```bash
git clone https://github.com/bluman1/mcp-agent-tools.git
cd mcp-agent-tools
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install in development mode**
```bash
pip install -e ".[dev]"
```

4. **Verify installation**
```bash
mcp-agent-tools --version
pytest
```

## Code Style

We use standard Python tooling for code quality:

- **Black** for code formatting
- **Ruff** for linting
- **MyPy** for type checking

Run these before committing:

```bash
# Format code
black src/ tests/ examples/

# Lint
ruff check src/ tests/ examples/

# Type check
mypy src/
```

## Testing

We aim for high test coverage. Please add tests for new features.

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=mcp_agent_tools --cov-report=html

# Run specific test file
pytest tests/test_generator.py

# Run specific test
pytest tests/test_generator.py::TestMCPCodeGenerator::test_generate_code
```

## Pull Request Process

1. **Create a feature branch**
```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes**
   - Write clear, documented code
   - Add tests for new functionality
   - Update documentation as needed

3. **Run tests and quality checks**
```bash
pytest
black src/ tests/
ruff check src/ tests/
mypy src/
```

4. **Commit your changes**
```bash
git add .
git commit -m "feat: add amazing new feature"
```

We use conventional commit messages:
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `test:` - Test additions or changes
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

5. **Push and create PR**
```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub with:
- Clear description of changes
- Link to any related issues
- Screenshots if applicable

## Areas for Contribution

We welcome contributions in these areas:

### New Features
- Support for additional template languages (TypeScript, Go, etc.)
- Enhanced type inference from JSON schemas
- Integration with more MCP servers
- Custom template system improvements
- Watch mode for auto-regeneration

### Bug Fixes
- Check open issues for bugs to fix
- Add tests that reproduce the bug
- Provide clear fix with explanation

### Documentation
- Improve README and examples
- Add tutorials and guides
- Document edge cases and gotchas
- Translate documentation

### Testing
- Increase test coverage
- Add integration tests with real MCP servers
- Performance benchmarks

### Tools & Infrastructure
- CI/CD improvements
- Docker support
- IDE extensions

## Code Review Process

All contributions require code review:

1. Automated checks must pass (tests, linting, type checking)
2. At least one maintainer review required
3. Address review feedback
4. Once approved, maintainer will merge

## Reporting Issues

When reporting issues, please include:

1. **Description** - Clear description of the issue
2. **Steps to reproduce** - Minimal example to reproduce
3. **Expected behavior** - What you expected to happen
4. **Actual behavior** - What actually happened
5. **Environment** - OS, Python version, package versions
6. **Logs** - Any relevant error messages or logs

Use this template:

```markdown
## Description
[Clear description of the issue]

## Steps to Reproduce
1. Run `mcp-agent-tools generate -c "..."`
2. ...
3. Error occurs

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happens]

## Environment
- OS: [e.g., Ubuntu 22.04, macOS 13.0, Windows 11]
- Python: [e.g., 3.11.5]
- mcp-agent-tools: [e.g., 0.1.0]

## Logs
```
[paste error logs here]
```
```

## Questions?

- Open an issue for questions
- Join discussions on GitHub Discussions
- Check existing issues and PRs

## Code of Conduct

Please note we have a code of conduct. Please follow it in all your interactions with the project.

### Our Standards

- Be respectful and inclusive
- Welcome newcomers
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy toward others

### Unacceptable Behavior

- Harassment or discriminatory language
- Trolling or insulting comments
- Public or private harassment
- Publishing others' private information
- Other conduct inappropriate in a professional setting

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- GitHub contributors page

Thank you for contributing to MCP Agent Tools! 🎉
