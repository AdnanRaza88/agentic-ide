# Testing Strategy

## Goals

- Protect contracts from accidental breakage
- Enable confident refactoring of replaceable components (graph engine, providers, etc.)
- Keep the modular monolith testable without requiring a full stack for unit tests

## Test Pyramid

| Level | Scope | Tools | Location |
|-------|-------|-------|----------|
| Unit | Individual functions, pure logic, contract implementations | pytest, vitest | `packages/*/tests`, `apps/*/tests` |
| Contract | Interface compliance, schema validation | pytest + hypothesis / pydantic | `packages/contracts/tests` |
| Integration | Package interactions, API + runtime | pytest + httpx, testcontainers | `tests/integration` |
| E2E | Full user flows (UI → API → agent → sandbox) | Playwright + pytest | `tests/e2e` |
| Adversarial / Property | Model router, tool safety, sandbox isolation | custom | `tests/adversarial` |

## Contract Tests (Critical)

Every implementation of a public interface **must** pass the corresponding contract test suite living under `packages/contracts/tests`.

Example:
- `ModelProvider` implementations → `test_model_provider_contract.py`
- `Tool` implementations → `test_tool_contract.py`
- `Verifier` implementations → `test_verifier_contract.py`

## Sandbox & Execution Tests

- Use real Docker where possible (testcontainers)
- Prefer lightweight mock sandboxes for unit speed
- Always verify isolation boundaries (no host FS leakage)

## Continuous Integration

- All PRs run unit + contract tests
- Integration tests run on main and release branches
- E2E runs nightly or on demand

## Coverage Targets (Initial)

- Contracts: 100% of public interfaces covered by contract tests
- Core packages: ≥ 80% line coverage
- Apps: ≥ 70%
