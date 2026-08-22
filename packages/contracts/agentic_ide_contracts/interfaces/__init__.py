"""Public interface contracts."""

from agentic_ide_contracts.interfaces.agent import Agent, AgentConfig
from agentic_ide_contracts.interfaces.agent_graph import (
    AgentGraph,
    GraphDefinition,
    GraphEdge,
    GraphNode,
)
from agentic_ide_contracts.interfaces.agent_state import AgentState, StateStore
from agentic_ide_contracts.interfaces.execution_sandbox import (
    CommandResult,
    ExecutionSandbox,
    SandboxConfig,
)
from agentic_ide_contracts.interfaces.hook import Hook, HookPoint
from agentic_ide_contracts.interfaces.mcp_server import MCPResource, MCPServer, MCPTool
from agentic_ide_contracts.interfaces.model_provider import (
    Message,
    ModelProvider,
    ModelRequest,
    ModelResponse,
    ToolCall,
)
from agentic_ide_contracts.interfaces.model_router import ModelRouter
from agentic_ide_contracts.interfaces.plugin import Plugin, PluginManifest
from agentic_ide_contracts.interfaces.preview import (
    DeploymentTarget,
    Preview,
    PreviewService,
    PreviewStatus,
)
from agentic_ide_contracts.interfaces.project import Project, ProjectStore
from agentic_ide_contracts.interfaces.session import Session, SessionStore
from agentic_ide_contracts.interfaces.specification import Specification
from agentic_ide_contracts.interfaces.task import Task, TaskStatus
from agentic_ide_contracts.interfaces.tool import Tool, ToolParameter, ToolResult, ToolSpec
from agentic_ide_contracts.interfaces.verifier import (
    VerificationResult,
    VerificationStatus,
    Verifier,
)
from agentic_ide_contracts.interfaces.workspace import FileInfo, Workspace
from agentic_ide_contracts.events.events import Event, EventType

__all__ = [
    "Agent",
    "AgentConfig",
    "AgentGraph",
    "AgentState",
    "CommandResult",
    "DeploymentTarget",
    "Event",
    "EventType",
    "ExecutionSandbox",
    "FileInfo",
    "GraphDefinition",
    "GraphEdge",
    "GraphNode",
    "Hook",
    "HookPoint",
    "MCPResource",
    "MCPServer",
    "MCPTool",
    "Message",
    "ModelProvider",
    "ModelRequest",
    "ModelResponse",
    "ModelRouter",
    "Plugin",
    "PluginManifest",
    "Preview",
    "PreviewService",
    "PreviewStatus",
    "Project",
    "ProjectStore",
    "SandboxConfig",
    "Session",
    "SessionStore",
    "Specification",
    "StateStore",
    "Task",
    "TaskStatus",
    "Tool",
    "ToolCall",
    "ToolParameter",
    "ToolResult",
    "ToolSpec",
    "VerificationResult",
    "VerificationStatus",
    "Verifier",
    "Workspace",
]
