# Integration Strategy

## Philosophy

Integrate external systems **only** through well-defined adapters that implement platform contracts.

Never let an external library dictate internal types or control flow.

## Allowed Integration Styles

1. **Adapter Pattern** (preferred)  
   External SDK → Adapter class → Platform Interface

2. **CLI Boundary**  
   Spawn external tools via subprocess with structured I/O

3. **HTTP / gRPC**  
   Treat external services as remote endpoints behind a client adapter

4. **MCP**  
   Use the MCP contract for tool and resource servers

5. **Plugin**  
   Dynamic loading of packages that implement the Plugin contract

## Forbidden Patterns

- Importing LangGraph / OpenAI / Anthropic types into core packages
- Making any single model provider or orchestration library a hard dependency of `agent-runtime`
- Leaking Docker client objects outside the workspace/harness layer

## Concrete Examples

| External System | Integration Point | Adapter Location |
|-----------------|-------------------|------------------|
| LangGraph | AgentGraph | `packages/graph/adapters/langgraph.py` |
| OpenAI SDK | ModelProvider | `packages/providers/openai.py` |
| Anthropic SDK | ModelProvider | `packages/providers/anthropic.py` |
| Ollama | ModelProvider | `packages/providers/ollama.py` |
| Docker | ExecutionSandbox | `packages/workspace/docker_sandbox.py` |
| MCP Servers | MCPServer | `packages/mcp/client.py` |
| GitHub / Vercel / etc. | DeploymentTarget | `packages/preview/targets/` |

## Versioning & Compatibility

- Adapters may pin specific versions of external libraries
- Core contracts remain stable; adapters absorb breaking changes of external deps
- When an external dependency forces a contract change → write an ADR first
