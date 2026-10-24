"""
Unit tests for the Alexa+ Model Context Protocol (MCP) Server
=============================================================

Tests:
- Server initialization & question bank loading
- Individual tool execution:
  - `get_interview_question` (by ID, topic/difficulty filter, error cases)
  - `evaluate_student_answer` (strong answer, misconception, attempt recording)
  - `get_session_weaknesses` (tracks session gaps)
  - `generate_revision_report` (structured report & markdown generation)
- JSON-RPC 2.0 Protocol Compliance:
  - `initialize` handshake
  - `tools/list` schema registry
  - `tools/call` execution and structured text content output
  - `tools/call` error handling (returns isError: True)
  - Unknown method handling (-32601)
  - Ping and notification handling
"""

import json
import pytest

from mcp_server import MCPServer, TOOLS_REGISTRY, MCP_PROTOCOL_VERSION, SERVER_NAME


@pytest.fixture
def mcp():
    """Fixture providing a fresh MCPServer instance for each test."""
    server = MCPServer(question_bank_path="question_bank.json")
    server.reset_session("stack_001")
    return server


# =============================================================================
# Direct Tool Handler Tests
# =============================================================================

def test_server_initialization(mcp):
    assert len(mcp.question_bank) == 10
    assert mcp.session.session_id is not None
    assert mcp.session.current_question_id == "stack_001"
    assert len(mcp.session.attempts) == 0


def test_tool_get_interview_question_by_id(mcp):
    res = mcp.tool_get_interview_question(question_id="stack_001")
    assert res["id"] == "stack_001"
    assert res["topic"] == "Stacks"
    assert res["difficulty"] == "easy"
    assert "question" in res
    assert "hint" in res
    # Ensure internal scoring criteria are NOT exposed to candidate
    assert "expected_points" not in res
    assert "critical_misconceptions" not in res


def test_tool_get_interview_question_by_filters(mcp):
    res = mcp.tool_get_interview_question(topic="Queues", difficulty="easy")
    assert res["topic"] == "Queues"
    assert res["difficulty"] == "easy"
    assert res["id"] in ("queue_001", "queue_002")


def test_tool_get_interview_question_invalid_id_raises(mcp):
    with pytest.raises(ValueError, match="not found in question bank"):
        mcp.tool_get_interview_question(question_id="non_existent_id")


def test_tool_get_interview_question_no_match_raises(mcp):
    with pytest.raises(ValueError, match="No questions matched filter"):
        mcp.tool_get_interview_question(topic="BinaryTrees", difficulty="hard")


def test_tool_evaluate_student_answer_strong(mcp):
    answer = (
        "A stack is a Last In First Out (LIFO) data structure. "
        "The push operation adds an element to the top, and the pop operation removes the top element."
    )
    result = mcp.tool_evaluate_student_answer(question_id="stack_001", student_answer=answer)

    assert result["score"] >= 8
    assert result["recommended_action"] == "progress"
    assert len(result["correct_points"]) >= 3

    # Verify session state was recorded
    assert len(mcp.session.attempts) == 1
    assert "stack_001" in mcp.session.asked_question_ids
    assert len(mcp.session.demonstrated_concepts) > 0


def test_tool_evaluate_student_answer_misconception(mcp):
    answer = "A stack is First In First Out (FIFO). You add to the rear and remove from front."
    result = mcp.tool_evaluate_student_answer(question_id="stack_001", student_answer=answer)

    assert result["score"] <= 4
    assert result["recommended_action"] == "scaffold_hint"
    assert len(result["misconceptions"]) > 0

    # Verify session recorded the gap
    assert len(mcp.session.unresolved_concepts) > 0


def test_tool_evaluate_invalid_question_id_raises(mcp):
    with pytest.raises(ValueError, match="not found in question bank"):
        mcp.tool_evaluate_student_answer("invalid_id", "Some answer")


def test_tool_get_session_weaknesses(mcp):
    # First, submit a misconception answer
    mcp.tool_evaluate_student_answer(
        question_id="stack_001",
        student_answer="A stack is FIFO, like a regular queue.",
    )

    weaknesses = mcp.tool_get_session_weaknesses()
    assert weaknesses["session_id"] == mcp.session.session_id
    assert weaknesses["total_attempts"] == 1
    assert len(weaknesses["misconceptions_detected"]) > 0
    assert len(weaknesses["unresolved_concepts"]) > 0


def test_tool_generate_revision_report(mcp):
    # Submit one strong answer and one partial answer
    mcp.tool_evaluate_student_answer(
        question_id="stack_001",
        student_answer="Stack is LIFO. Push inserts at top. Pop deletes from top.",
    )
    mcp.tool_evaluate_student_answer(
        question_id="queue_001",
        student_answer="A queue adds elements to the back.",
    )

    report = mcp.tool_generate_revision_report()
    assert "total_score" in report
    assert "percentage" in report
    assert "performance_tier" in report
    assert "demonstrated_concepts" in report
    assert "recommendations" in report
    assert "markdown_report" in report
    assert report["attempts_count"] == 2
    assert report["performance_tier"] in ("Proficient", "Developing", "Foundational")


# =============================================================================
# JSON-RPC 2.0 Protocol Compliance Tests
# =============================================================================

def test_jsonrpc_initialize(mcp):
    req = {
        "jsonrpc": "2.0",
        "id": "req-1",
        "method": "initialize",
        "params": {
            "protocolVersion": MCP_PROTOCOL_VERSION,
            "capabilities": {},
            "clientInfo": {"name": "alexa-test-client", "version": "1.0"},
        },
    }
    resp = mcp.dispatch(req)
    assert resp["jsonrpc"] == "2.0"
    assert resp["id"] == "req-1"
    assert "result" in resp
    assert resp["result"]["protocolVersion"] == MCP_PROTOCOL_VERSION
    assert resp["result"]["serverInfo"]["name"] == SERVER_NAME


def test_jsonrpc_ping(mcp):
    req = {"jsonrpc": "2.0", "id": 100, "method": "ping"}
    resp = mcp.dispatch(req)
    assert resp["id"] == 100
    assert resp["result"] == {}


def test_jsonrpc_notifications_return_none(mcp):
    req = {"jsonrpc": "2.0", "method": "notifications/initialized"}
    resp = mcp.dispatch(req)
    assert resp is None


def test_jsonrpc_tools_list(mcp):
    req = {"jsonrpc": "2.0", "id": "list-1", "method": "tools/list"}
    resp = mcp.dispatch(req)
    assert resp["id"] == "list-1"
    tools = resp["result"]["tools"]
    assert len(tools) == 4
    tool_names = [t["name"] for t in tools]
    assert "get_interview_question" in tool_names
    assert "evaluate_student_answer" in tool_names
    assert "get_session_weaknesses" in tool_names
    assert "generate_revision_report" in tool_names

    # Check inputSchema validity
    for t in tools:
        assert "name" in t
        assert "description" in t
        assert "inputSchema" in t
        assert t["inputSchema"]["type"] == "object"


def test_jsonrpc_tools_call_get_interview_question(mcp):
    req = {
        "jsonrpc": "2.0",
        "id": "call-1",
        "method": "tools/call",
        "params": {
            "name": "get_interview_question",
            "arguments": {"question_id": "queue_001"},
        },
    }
    resp = mcp.dispatch(req)
    assert resp["id"] == "call-1"
    assert resp["result"]["isError"] is False
    content_text = resp["result"]["content"][0]["text"]
    q_data = json.loads(content_text)
    assert q_data["id"] == "queue_001"
    assert q_data["topic"] == "Queues"


def test_jsonrpc_tools_call_evaluate_student_answer(mcp):
    req = {
        "jsonrpc": "2.0",
        "id": "call-2",
        "method": "tools/call",
        "params": {
            "name": "evaluate_student_answer",
            "arguments": {
                "question_id": "queue_001",
                "student_answer": (
                    "A queue is a First In First Out (FIFO) data structure. "
                    "Enqueue adds to the rear and dequeue removes from the front."
                ),
            },
        },
    }
    resp = mcp.dispatch(req)
    assert resp["id"] == "call-2"
    assert resp["result"]["isError"] is False
    content_text = resp["result"]["content"][0]["text"]
    eval_data = json.loads(content_text)
    assert eval_data["score"] >= 8
    assert eval_data["recommended_action"] == "progress"


def test_jsonrpc_tools_call_validation_error(mcp):
    req = {
        "jsonrpc": "2.0",
        "id": "call-err",
        "method": "tools/call",
        "params": {
            "name": "get_interview_question",
            "arguments": {"question_id": "fake_id_123"},
        },
    }
    resp = mcp.dispatch(req)
    assert resp["id"] == "call-err"
    # In MCP, tool application errors are returned as result with isError=True
    assert resp["result"]["isError"] is True
    assert "Validation Error" in resp["result"]["content"][0]["text"]


def test_jsonrpc_unknown_tool_error(mcp):
    req = {
        "jsonrpc": "2.0",
        "id": "unknown-tool",
        "method": "tools/call",
        "params": {
            "name": "unsupported_tool",
            "arguments": {},
        },
    }
    resp = mcp.dispatch(req)
    assert resp["id"] == "unknown-tool"
    assert "error" in resp
    assert resp["error"]["code"] == -32601


def test_jsonrpc_unknown_method(mcp):
    req = {
        "jsonrpc": "2.0",
        "id": 999,
        "method": "non_existent_method",
    }
    resp = mcp.dispatch(req)
    assert resp["id"] == 999
    assert "error" in resp
    assert resp["error"]["code"] == -32601
    assert "Method not found" in resp["error"]["message"]
