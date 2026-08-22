# Feature Ownership Rules

## Purpose

Clear ownership prevents architectural drift and contract violations.

## Ownership Matrix

| Area | Owner Package | Notes |
|------|---------------|-------|
| Interface & Schema definitions | `packages/contracts` | Single source of truth |
| Agent lifecycle & runtime | `packages/agent-runtime` | |
| Graph execution engine | `packages/graph` | Behind adapter |
| State persistence | `packages/state` | |
| Model calling | `packages/providers` | |
| Tool execution | `packages/tools` | |
| MCP protocol | `packages/mcp` | |
| Plugin system | `packages/plugins` | |
| Lifecycle hooks | `packages/hooks` | |
| Execution harness | `packages/harness` | |
| Workspace / FS | `packages/workspace` | |
| Verification | `packages/verifier` | |
| Specs & requirements | `packages/specs` | |
| Preview & deploy targets | `packages/preview` | |
| HTTP / WS API | `apps/api` | |
| User interface | `apps/web` | |

## Rules

1. **No cross-package implementation leakage**  
   A package may depend on contracts of other packages, but must not import their internal implementation.

2. **Contracts are sacred**  
   Changing any public interface in `packages/contracts` requires:
   - An ADR
   - Version bump (semver)
   - Migration notes if breaking

3. **New features start with contracts**  
   Before writing implementation code, define or extend the relevant interfaces in `packages/contracts`.

4. **Adapters live at the edge**  
   Third-party libraries (LangGraph, OpenAI SDK, Docker SDK, etc.) may only be imported inside adapter modules, never in core packages.

5. **Feature PRs must declare ownership**  
   Every PR description must state which package(s) own the change and confirm contracts were respected or updated via ADR.

6. **Circular dependencies are forbidden**  
   The dependency graph must remain acyclic. Contracts sit at the bottom.
