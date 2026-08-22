# Contributing to Agentic IDE

Thank you for your interest in contributing!

## Golden Rules

1. **Contracts are sacred**  
   Do not change any public interface in `packages/contracts` without first opening an ADR.

2. **Own the core**  
   External libraries must be integrated only through adapters.

3. **Feature ownership**  
   Respect the ownership matrix in `docs/feature-ownership.md`.

4. **Tests first for contracts**  
   New implementations of a contract must pass the corresponding contract tests.

## Development Workflow

1. Fork & clone
2. Create a feature branch: `git switch -c feature/your-feature`
3. Make changes (start with contracts if needed → ADR)
4. Add/adjust tests
5. Open a Pull Request with a clear description of ownership and any contract impact

## Code Style

- Python: ruff + mypy
- TypeScript: ESLint + Prettier (once web app is scaffolded)
- Prefer clear names over cleverness

## Questions?

Open an issue or discussion. We value architectural clarity over speed of feature delivery in this phase.
