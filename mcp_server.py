"""
EduAgent Interview Coach — Alexa+ Model Context Protocol (MCP) Server
======================================================================

Self-hosted Model Context Protocol server exposing four standardized tools
for Alexa+ Agent Skills and autonomous agents:
1. `get_interview_question`: Retrieve questions by topic, difficulty, or question ID.
2. `evaluate_student_answer`: Grade a candidate's explanation against the 10-point rubric.
3. `get_session_weaknesses`: Inspect unresolved concepts and misconceptions.
4. `generate_revision_report`: Produce a comprehensive performance report with study advice.

Supports:
- JSON-RPC 2.0 protocol conforming to the Model Context Protocol standard.
- `stdio` transport for direct local agent execution.
- HTTP / SSE transport for remote Alexa+ agent invocations.
- Deterministic, offline-first execution with strict schema validation.
"""

import argparse
import http.server
import json
import os
import sys
import uuid
from typing import Any, Dict, List, Optional

from adaptive_engine import AdaptiveEngine
from evaluator import evaluate_answer, validate_evaluation_result
from interview_engine import InterviewEngine, InterviewSession
from report_generator import ReportGenerator


# =============================================================================
# Question Bank Loader
# =============================================================================

def load_question_bank(bank_path: str = "question_bank.json") -> Dict[str, Dict[str, Any]]:
    """Load question bank from JSON file into a lookup dictionary keyed by ID."""
    if not os.path.isabs(bank_path):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        bank_path = os.path.join(base_dir, bank_path)
    with open(bank_path, "r", encoding="utf-8") as f:
        questions: List[Dict[str, Any]] = json.load(f)
    return {q["id"]: q for q in questions}


# =============================================================================
# Tool Definitions & Schema Registry
# =============================================================================

MCP_PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "eduagent-interview-coach-mcp"
SERVER_VERSION = "1.0.0"

TOOLS_REGISTRY: List[Dict[str, Any]] = [
    {
        "name": "get_interview_question",
        "description": (
            "Retrieve an interview question from the reviewed Stacks and Queues question bank "
            "for technical interview practice. Optionally filter by topic ('Stacks'/'Queues'), "
            "difficulty ('easy'/'medium'/'hard'), or specific question_id."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "enum": ["Stacks", "Queues"],
                    "description": "Filter by DSA topic (Stacks or Queues)",
                },
                "difficulty": {
                    "type": "string",
                    "enum": ["easy", "medium", "hard"],
                    "description": "Filter by difficulty level (easy, medium, or hard)",
                },
                "question_id": {
                    "type": "string",
                    "description": "Specific question ID to retrieve (e.g., 'stack_001')",
                },
            },
        },
    },
    {
        "name": "evaluate_student_answer",
        "description": (
            "Evaluate a candidate's written or spoken technical explanation against the 10-point "
            "rubric (Correctness 0-4, Concepts 0-3, Reasoning 0-2, Clarity 0-1), identifying correct "
            "points, missing concepts, critical misconceptions, and next action."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "question_id": {
                    "type": "string",
                    "description": "The unique identifier of the question being answered",
                },
                "student_answer": {
                    "type": "string",
                    "description": "The candidate's typed or spoken technical explanation",
                },
            },
            "required": ["question_id", "student_answer"],
        },
    },
    {
        "name": "get_session_weaknesses",
        "description": (
            "Retrieve the candidate's tracked concept gaps, unresolved topics, and identified "
            "misconceptions from the active interview session."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "generate_revision_report",
        "description": (
            "Generate a comprehensive post-interview performance report, including total score, "
            "performance tier, demonstrated strengths, unresolved gaps, and prioritized study recommendations."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
]


# =============================================================================
# Core MCP Server Implementation
# =============================================================================

class MCPServer:
    """
    Self-hosted Model Context Protocol server managing session state and
    tool dispatch for Alexa+ Agent Skills.
    """

    def __init__(self, question_bank_path: str = "question_bank.json") -> None:
        self.question_bank = load_question_bank(question_bank_path)
        self.adaptive_engine = AdaptiveEngine()
        self.report_generator = ReportGenerator()
        self.session = InterviewSession(
            session_id=str(uuid.uuid4()),
            current_question_id="stack_001",
        )

    def reset_session(self, first_question_id: str = "stack_001") -> None:
        """Reset the server session with a clean state."""
        if first_question_id not in self.question_bank:
            first_question_id = next(iter(self.question_bank.keys()))
        self.session = InterviewSession(
            session_id=str(uuid.uuid4()),
            current_question_id=first_question_id,
        )

    # -------------------------------------------------------------------------
    # Tool Handlers
    # -------------------------------------------------------------------------

    def tool_get_interview_question(
        self,
        topic: Optional[str] = None,
        difficulty: Optional[str] = None,
        question_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Handler for `get_interview_question`.
        Returns candidate-safe question data (omitting internal grading rubrics).
        """
        target_q: Optional[Dict[str, Any]] = None

        if question_id:
            if question_id not in self.question_bank:
                raise ValueError(
                    f"Question ID '{question_id}' not found in question bank. "
                    f"Available IDs: {list(self.question_bank.keys())}"
                )
            target_q = self.question_bank[question_id]
        else:
            # Filter candidates by topic / difficulty
            candidates = list(self.question_bank.values())
            if topic:
                candidates = [c for c in candidates if c.get("topic", "").lower() == topic.lower()]
            if difficulty:
                candidates = [c for c in candidates if c.get("difficulty", "").lower() == difficulty.lower()]

            if not candidates:
                raise ValueError(
                    f"No questions matched filter (topic={topic}, difficulty={difficulty})."
                )

            # Prefer unasked questions from active session
            unasked = [c for c in candidates if c["id"] not in self.session.asked_question_ids]
            target_q = unasked[0] if unasked else candidates[0]

        # Update active session pointer
        self.session.current_question_id = target_q["id"]

        return {
            "id": target_q["id"],
            "topic": target_q.get("topic", "DSA"),
            "difficulty": target_q.get("difficulty", "medium"),
            "question": target_q["question"],
            "hint": target_q.get("hint", ""),
        }

    def tool_evaluate_student_answer(
        self,
        question_id: str,
        student_answer: str,
    ) -> Dict[str, Any]:
        """
        Handler for `evaluate_student_answer`.
        Evaluates answer, records session attempt, updates concept tracking, and returns rubric feedback.
        """
        if not question_id:
            raise ValueError("question_id is required.")
        if question_id not in self.question_bank:
            raise ValueError(f"Question ID '{question_id}' not found in question bank.")

        question = self.question_bank[question_id]

        # Perform deterministic local evaluation
        eval_result = evaluate_answer(question, student_answer, provider="local")
        validate_evaluation_result(eval_result)

        # Update concept mastery tracking
        self.adaptive_engine.update_concept_tracking(
            current_question=question,
            evaluation=eval_result,
            demonstrated_concepts=self.session.demonstrated_concepts,
            unresolved_concepts=self.session.unresolved_concepts,
        )

        # Record attempt in active session
        attempt = {
            "question_id": question_id,
            "student_answer": student_answer,
            "evaluation": eval_result,
        }
        self.session.attempts.append(attempt)
        if question_id not in self.session.asked_question_ids:
            self.session.asked_question_ids.append(question_id)

        return eval_result

    def tool_get_session_weaknesses(self) -> Dict[str, Any]:
        """
        Handler for `get_session_weaknesses`.
        Returns unresolved concepts and detected misconceptions from the active session.
        """
        misconceptions: List[str] = []
        for attempt in self.session.attempts:
            eval_res = attempt.get("evaluation", {})
            for m in eval_res.get("misconceptions", []):
                if m not in misconceptions:
                    misconceptions.append(m)

        return {
            "session_id": self.session.session_id,
            "total_attempts": len(self.session.attempts),
            "unresolved_concepts": sorted(list(self.session.unresolved_concepts)),
            "demonstrated_concepts": sorted(list(self.session.demonstrated_concepts)),
            "misconceptions_detected": misconceptions,
        }

    def tool_generate_revision_report(self) -> Dict[str, Any]:
        """
        Handler for `generate_revision_report`.
        Returns complete post-interview performance analysis and study recommendations.
        """
        report = self.report_generator.generate_report(self.session)
        markdown = self.report_generator.generate_markdown_report(report)
        report["markdown_report"] = markdown
        return report

    # -------------------------------------------------------------------------
    # JSON-RPC 2.0 Dispatcher
    # -------------------------------------------------------------------------

    def dispatch(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process a JSON-RPC 2.0 request and return the JSON-RPC response dictionary.
        Returns None for notifications (requests without an 'id').
        """
        req_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Handle notifications (no response required)
        if req_id is None and method in ("notifications/initialized", "initialized"):
            return None

        # Helper to construct error response
        def make_error(code: int, message: str, data: Any = None) -> Dict[str, Any]:
            err_dict: Dict[str, Any] = {"code": code, "message": message}
            if data is not None:
                err_dict["data"] = data
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": err_dict,
            }

        # Helper to construct success response
        def make_result(result: Any) -> Dict[str, Any]:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": result,
            }

        # 1. initialize
        if method == "initialize":
            return make_result({
                "protocolVersion": MCP_PROTOCOL_VERSION,
                "capabilities": {
                    "tools": {},
                },
                "serverInfo": {
                    "name": SERVER_NAME,
                    "version": SERVER_VERSION,
                },
            })

        # 2. ping
        if method == "ping":
            return make_result({})

        # 3. tools/list
        if method == "tools/list":
            return make_result({
                "tools": TOOLS_REGISTRY,
            })

        # 4. tools/call
        if method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})

            if not tool_name:
                return make_error(-32602, "Missing tool name in params")

            try:
                if tool_name == "get_interview_question":
                    res = self.tool_get_interview_question(
                        topic=arguments.get("topic"),
                        difficulty=arguments.get("difficulty"),
                        question_id=arguments.get("question_id"),
                    )
                elif tool_name == "evaluate_student_answer":
                    res = self.tool_evaluate_student_answer(
                        question_id=arguments.get("question_id", ""),
                        student_answer=arguments.get("student_answer", ""),
                    )
                elif tool_name == "get_session_weaknesses":
                    res = self.tool_get_session_weaknesses()
                elif tool_name == "generate_revision_report":
                    res = self.tool_generate_revision_report()
                else:
                    return make_error(-32601, f"Unknown tool: '{tool_name}'")

                return make_result({
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(res, indent=2),
                        }
                    ],
                    "isError": False,
                })

            except ValueError as ve:
                return make_result({
                    "content": [{"type": "text", "text": f"Validation Error: {str(ve)}"}],
                    "isError": True,
                })
            except Exception as exc:
                return make_result({
                    "content": [{"type": "text", "text": f"Execution Error: {str(exc)}"}],
                    "isError": True,
                })

        # Unknown method
        return make_error(-32601, f"Method not found: '{method}'")


# =============================================================================
# Transports: Stdio & HTTP / SSE
# =============================================================================

def run_stdio_server(server: MCPServer) -> None:
    """Run MCP server over standard I/O (stdio) transport."""
    sys.stderr.write(f"[{SERVER_NAME}] Starting stdio MCP server (version {SERVER_VERSION})...\n")
    sys.stderr.flush()

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": "Parse error: Invalid JSON"},
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()
            continue

        resp = server.dispatch(req)
        if resp is not None:
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()


def run_http_server(server: MCPServer, host: str = "127.0.0.1", port: int = 8000) -> None:
    """Run lightweight HTTP/SSE JSON-RPC server using standard library."""
    class MCPHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: Any) -> None:
            # Suppress default noisy access logs to keep stderr clean
            pass

        def do_OPTIONS(self) -> None:
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()

        def do_POST(self) -> None:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            try:
                req = json.loads(body)
                resp = server.dispatch(req)
                resp_bytes = json.dumps(resp).encode("utf-8") if resp else b""

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Content-Length", str(len(resp_bytes)))
                self.end_headers()
                if resp_bytes:
                    self.wfile.write(resp_bytes)
            except Exception as e:
                err_resp = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32603, "message": f"Internal error: {str(e)}"},
                }
                resp_bytes = json.dumps(err_resp).encode("utf-8")
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(resp_bytes)))
                self.end_headers()
                self.wfile.write(resp_bytes)

        def do_GET(self) -> None:
            if self.path in ("/sse", "/events"):
                # Basic SSE endpoint for Alexa+ agent streaming
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Connection", "keep-alive")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(b": keepalive\n\n")
                self.wfile.flush()
            else:
                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(
                    f"{SERVER_NAME} v{SERVER_VERSION} is running. Send POST JSON-RPC to this endpoint.".encode("utf-8")
                )

    httpd = http.server.HTTPServer((host, port), MCPHTTPRequestHandler)
    sys.stderr.write(f"[{SERVER_NAME}] HTTP MCP Server listening at http://{host}:{port}/\n")
    sys.stderr.flush()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


# =============================================================================
# CLI Entry Point
# =============================================================================

def main() -> None:
    """CLI entry point parsing transport options."""
    parser = argparse.ArgumentParser(description="EduAgent Interview Coach MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "http"],
        default=os.environ.get("MCP_TRANSPORT", "stdio"),
        help="MCP transport protocol (stdio or sse/http, default: stdio)",
    )
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host address for HTTP transport (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("MCP_SERVER_PORT", "8000")),
        help="Port number for HTTP transport (default: 8000)",
    )

    args = parser.parse_args()
    server = MCPServer()

    if args.transport in ("sse", "http"):
        run_http_server(server, host=args.host, port=args.port)
    else:
        run_stdio_server(server)


if __name__ == "__main__":
    main()
