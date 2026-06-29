"""JN Resolusi Agents Package"""
from agents.agent_a import run as run_agent_a, AgentAResult
from agents.agent_b import run as run_agent_b, AgentBResult
from agents.agent_c import run as run_agent_c, AgentCResult

__all__ = ["run_agent_a", "run_agent_b", "run_agent_c",
           "AgentAResult", "AgentBResult", "AgentCResult"]
