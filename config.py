"""
EduAgent Interview Coach — Configuration Module
===============================================

Loads runtime settings from environment variables with sensible defaults.
Supports offline-first evaluation and local self-hosted MCP server configuration.
"""

import os
from typing import Literal

# Operational mode: 'local' (offline-first deterministic evaluation)
EVALUATION_MODE: Literal["local"] = os.getenv("EVALUATION_MODE", "local")

# Question bank location
QUESTION_BANK_PATH: str = os.getenv("QUESTION_BANK_PATH", "question_bank.json")

# Model Context Protocol (MCP) Server Settings
MCP_SERVER_HOST: str = os.getenv("MCP_SERVER_HOST", "127.0.0.1")
MCP_SERVER_PORT: int = int(os.getenv("MCP_SERVER_PORT", "8000"))
MCP_TRANSPORT: Literal["stdio", "sse", "http"] = os.getenv("MCP_TRANSPORT", "stdio")

# UI Settings
APP_TITLE: str = "EduAgent Interview Coach"
APP_ICON: str = "🧠"
DEFAULT_FIRST_QUESTION: str = "stack_001"
