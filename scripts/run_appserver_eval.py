#!/usr/bin/env python3
"""
Multi-Turn CLI Compaction Evaluation using App-Server Protocol

Tests actual Rust compaction by:
1. Running codex app-server as subprocess with JSON-RPC over stdin/stdout
2. Creating a thread with low token limit to force compaction
3. Sending multiple turns to accumulate context and trigger auto-compaction
4. Measuring retention of goals, constraints, and decisions

Protocol flow:
  - initialize -> initialized event
  - thread/start -> threadId
  - turn/start (repeated) -> events until task_complete
  - Listen for compaction warnings

Usage:
    python scripts/run_appserver_eval.py
    python scripts/run_appserver_eval.py --token-limit 5000 --turns 10
    python scripts/run_appserver_eval.py --codex-path /path/to/codex
"""

import argparse
import json
import os
import subprocess
import sys
import time
import queue
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import threading

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Default binary path - project's Codex binary
DEFAULT_CODEX = str(project_root / "codex" / "codex-rs" / "target" / "release" / "codex")


class AppServerClient:
    """
    Client for codex app-server JSON-RPC protocol.
    """
    def __init__(self, codex_path: str, token_limit: int = 5000, timeout: int = 120):
        self.codex_path = codex_path
        self.token_limit = token_limit
        self.timeout = timeout
        self.process: Optional[subprocess.Popen] = None
        self.request_id = 0
        self.thread_id: Optional[str] = None
        self.events: List[Dict] = []
        self.responses: queue.Queue = queue.Queue()
        self.reader_thread: Optional[threading.Thread] = None
        self.running = False
        self.compaction_count = 0

    def start(self) -> bool:
        """Start the app-server subprocess."""
        cmd = [self.codex_path, "app-server"]
        try:
            # Pass current environment (includes loaded dotenv) to subprocess
            env = os.environ.copy()
            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(project_root),
                bufsize=1,  # Line buffered
                env=env,
            )
            self.running = True
            # Start reader thread
            self.reader_thread = threading.Thread(target=self._read_output, daemon=True)
            self.reader_thread.start()
            time.sleep(0.5)  # Give server time to start
            return True
        except Exception as e:
            print(f"Failed to start app-server: {e}")
            return False

    def _read_output(self):
        """Read output from the app-server in a separate thread."""
        while self.running and self.process and self.process.stdout:
            try:
                line = self.process.stdout.readline()
                if not line:
                    break
                line = line.strip()
                if not line:
                    continue
                try:
                    msg = json.loads(line)
                    # Check if it's a response (has id) or notification
                    if "id" in msg:
                        self.responses.put(msg)
                    elif "method" in msg:
                        # It's a notification/event
                        self.events.append(msg)
                        self._handle_event(msg)
                except json.JSONDecodeError:
                    pass
            except Exception:
                break

    def _handle_event(self, event: Dict):
        """Handle incoming events."""
        method = event.get("method", "")
        params = event.get("params", {})

        if method == "warning":
            message = params.get("message", "")
            if "compaction" in message.lower():
                self.compaction_count += 1
                print(f"    [COMPACTION WARNING] {message[:100]}...")

        if method == "thread/compacted":
            self.compaction_count += 1
            print(f"    [COMPACTION] Thread compacted")

    def stop(self):
        """Stop the app-server."""
        self.running = False
        if self.process:
            try:
                # Send shutdown notification
                self._send_notification("shutdown", {})
                time.sleep(0.5)
                self.process.terminate()
                self.process.wait(timeout=5)
            except:
                if self.process:
                    self.process.kill()
            self.process = None

    def _send_request(self, method: str, params: Dict) -> Optional[Dict]:
        """Send a JSON-RPC request and wait for response."""
        if not self.process:
            return None

        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params,
        }

        try:
            self.process.stdin.write(json.dumps(request) + "\n")
            self.process.stdin.flush()

            # Wait for response with matching ID
            start_time = time.time()
            while time.time() - start_time < self.timeout:
                try:
                    response = self.responses.get(timeout=1)
                    if response.get("id") == self.request_id:
                        return response
                except queue.Empty:
                    continue
            return None
        except Exception as e:
            print(f"Error sending request: {e}")
            return None

    def _send_notification(self, method: str, params: Dict):
        """Send a JSON-RPC notification (no response expected)."""
        if not self.process:
            return

        notification = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
        }
        try:
            self.process.stdin.write(json.dumps(notification) + "\n")
            self.process.stdin.flush()
        except:
            pass

    def initialize(self) -> bool:
        """Initialize the app-server connection."""
        response = self._send_request("initialize", {
            "clientInfo": {
                "name": "eval-client",
                "version": "1.0.0",
            }
        })
        if response and "result" in response:
            return True
        return False

    def start_thread(self, model: str = "gpt-4o-mini") -> Optional[str]:
        """Start a new conversation thread."""
        config = {
            "model_auto_compact_token_limit": self.token_limit,
        }
        response = self._send_request("thread/start", {
            "model": model,
            "modelProvider": "openai",
            "config": config,
            "approvalPolicy": "never",
            "sandbox": "dangerFullAccess",
        })
        if response and "result" in response:
            # Thread ID is nested inside result.thread.id
            thread_data = response["result"].get("thread", {})
            self.thread_id = thread_data.get("id") or response["result"].get("threadId")
            return self.thread_id
        return None

    def send_turn(self, text: str) -> bool:
        """Send a user turn and wait for task completion."""
        if not self.thread_id:
            return False

        # Clear events before sending turn to track completion
        events_before = len(self.events)

        response = self._send_request("turn/start", {
            "threadId": self.thread_id,
            "input": [{"type": "text", "text": text}],
        })

        if not response or "result" not in response:
            return False

        # Wait for task complete event (only checking new events)
        return self._wait_for_task_complete(events_start=events_before)

    def _wait_for_task_complete(self, timeout: int = 120, events_start: int = 0) -> bool:
        """Wait for a turn/completed or task_complete event."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            # Only check events after events_start
            for event in self.events[events_start:]:
                method = event.get("method", "")
                # Check for various completion event names
                if method in ["turn/completed", "codex/event/task_complete", "taskComplete"]:
                    return True
            time.sleep(0.1)
        return False

    def trigger_compact(self) -> bool:
        """Manually trigger compaction."""
        if not self.thread_id:
            return False

        response = self._send_request("thread/compact", {
            "threadId": self.thread_id,
        })
        return response and "result" in response

    def get_final_output(self) -> str:
        """Get the final assistant output from events."""
        # Look for item/completed events with assistant content
        for event in reversed(self.events):
            method = event.get("method", "")
            if method == "item/completed":
                params = event.get("params", {})
                item = params.get("item", {})
                if item.get("type") == "assistant":
                    content_list = item.get("content", [])
                    for content in content_list:
                        if content.get("type") == "text":
                            text = content.get("text", "")
                            if text:
                                return text
            # Also check for assistantMessage (older format)
            elif method == "assistantMessage":
                content = event.get("params", {}).get("content", "")
                if content:
                    return content
        return ""


def create_conversation_turns(num_turns: int = 15) -> List[str]:
    """Create conversation turns designed to accumulate context."""
    goal = "Build a real-time chat application with WebSocket support handling 10,000 concurrent users"
    constraints = [
        "Budget: Maximum $5000",
        "Timeline: 2 weeks",
        "Team: 2 Python developers",
        "PostgreSQL database",
        "Mobile and web support",
    ]

    turns = [
        f"I need help with: {goal}",
        "Key constraints: " + ", ".join(constraints),
    ]

    research = [
        "Research Python WebSocket frameworks - FastAPI, AIOHTTP, Tornado. FastAPI seems best with async support.",
        "FastAPI benefits: automatic docs, native async, Pydantic validation, good performance. Team can learn in 1-2 days.",
        "Scaling needs Redis pub/sub for cross-instance messaging. Fan-out pattern enables horizontal scaling.",
        "Memory analysis: 50-100KB per WebSocket. For 10K connections need 500MB-1GB RAM plus overhead.",
        "PostgreSQL should use asyncpg - 3x faster than psycopg2 in async contexts. Need connection pooling.",
        "Architecture: Load Balancer -> FastAPI workers -> Redis pub/sub -> PostgreSQL. Sticky sessions for WebSockets.",
        "Auth: JWT tokens validated on WebSocket upgrade. Refresh tokens for re-auth without disconnection.",
        "Error handling: exponential backoff reconnection, server cleanup on disconnect, proper error codes.",
        "Monitoring: Prometheus metrics for connections, message rates, latency percentiles. Grafana dashboards.",
        "Deployment: Kubernetes with HPA, start 4 pods, scale on connection count. 2 cores, 2GB per pod.",
        "Security: rate limiting 10/s, input validation, message size 64KB max, TLS 1.3, audit logging.",
        "Performance: message batching, MessagePack format, connection pooling, Redis caching, lazy loading.",
    ]

    turns.extend(research[:num_turns - 3])

    turns.append(
        "Summarize everything we discussed: What is the main goal? What are the constraints? "
        "What framework did we choose? What's the architecture? What database approach?"
    )

    return turns


def measure_retention(output: str) -> Dict[str, float]:
    """Measure goal and constraint retention in output."""
    output_lower = output.lower()

    goal_kw = ["chat", "websocket", "real-time", "10000", "10,000", "concurrent"]
    goal_found = sum(1 for kw in goal_kw if kw in output_lower)
    goal_retention = goal_found / len(goal_kw) if goal_kw else 0

    constraint_kw = ["5000", "$5000", "budget", "2 weeks", "postgresql", "mobile", "web", "python"]
    constraint_found = sum(1 for kw in constraint_kw if kw in output_lower)
    constraint_retention = constraint_found / len(constraint_kw) if constraint_kw else 0

    decision_kw = ["fastapi", "redis", "kubernetes", "jwt", "prometheus", "asyncpg"]
    decision_found = sum(1 for kw in decision_kw if kw in output_lower)
    decision_retention = decision_found / len(decision_kw) if decision_kw else 0

    return {
        "goal_retention": goal_retention,
        "constraint_retention": constraint_retention,
        "decision_retention": decision_retention,
        "overall_retention": (goal_retention + constraint_retention + decision_retention) / 3,
    }


def run_test(
    codex_path: str,
    turns: List[str],
    token_limit: int,
    verbose: bool = True,
) -> Dict[str, Any]:
    """Run multi-turn test with app-server."""
    results = {
        "binary": codex_path,
        "token_limit": token_limit,
        "num_turns": len(turns),
        "compaction_events": 0,
        "turns_completed": 0,
        "final_output": "",
        "retention": {},
        "error": None,
    }

    client = AppServerClient(codex_path, token_limit=token_limit)

    if not client.start():
        results["error"] = "Failed to start app-server"
        return results

    try:
        # Initialize
        if verbose:
            print("  Initializing app-server...")
        if not client.initialize():
            results["error"] = "Failed to initialize"
            return results

        # Start thread
        if verbose:
            print("  Starting thread...")
        thread_id = client.start_thread()
        if not thread_id:
            results["error"] = "Failed to start thread"
            return results

        if verbose:
            print(f"  Thread ID: {thread_id}")

        # Send turns
        for i, turn in enumerate(turns):
            if verbose:
                print(f"  Turn {i+1}/{len(turns)}: {turn[:50]}...")

            if client.send_turn(turn):
                results["turns_completed"] += 1
            else:
                if verbose:
                    print(f"    Failed to complete turn {i+1}")

            time.sleep(0.5)  # Brief pause between turns

        # Get results
        results["compaction_events"] = client.compaction_count
        results["final_output"] = client.get_final_output()
        results["retention"] = measure_retention(results["final_output"])

    except Exception as e:
        results["error"] = str(e)
    finally:
        client.stop()

    return results


def run_single_eval(
    codex_path: str,
    token_limit: int = 5000,
    num_turns: int = 12,
    verbose: bool = True,
) -> Dict:
    """Run single-binary evaluation."""
    print("\n" + "=" * 70)
    print("APP-SERVER COMPACTION EVALUATION")
    print("=" * 70)
    print(f"\nCodex binary: {codex_path}")
    print(f"Token limit: {token_limit}")
    print(f"Number of turns: {num_turns}")

    turns = create_conversation_turns(num_turns)

    results = {
        "timestamp": datetime.now().isoformat(),
        "token_limit": token_limit,
        "num_turns": len(turns),
        "test": None,
    }

    print("\n" + "-" * 50)
    print("Testing Codex Compaction")
    print("-" * 50)

    test_results = run_test(codex_path, turns, token_limit, verbose)
    results["test"] = test_results

    if verbose:
        print(f"\n  Turns completed: {test_results['turns_completed']}/{len(turns)}")
        print(f"  Compaction events: {test_results['compaction_events']}")
        if test_results.get("retention"):
            ret = test_results["retention"]
            print(f"  Goal retention: {ret.get('goal_retention', 0):.2%}")
            print(f"  Constraint retention: {ret.get('constraint_retention', 0):.2%}")
            print(f"  Decision retention: {ret.get('decision_retention', 0):.2%}")
            print(f"  Overall retention: {ret.get('overall_retention', 0):.2%}")
        if test_results.get("error"):
            print(f"  Error: {test_results['error']}")

    # Print summary
    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)

    ret = test_results.get("retention", {})
    print(f"\n{'Metric':<25} {'Value':>15}")
    print("-" * 42)
    print(f"{'Turns Completed':<25} {test_results['turns_completed']:>15}")
    print(f"{'Compaction Events':<25} {test_results['compaction_events']:>15}")
    print(f"{'Goal Retention':<25} {ret.get('goal_retention', 0):>15.2%}")
    print(f"{'Constraint Retention':<25} {ret.get('constraint_retention', 0):>15.2%}")
    print(f"{'Decision Retention':<25} {ret.get('decision_retention', 0):>15.2%}")
    print(f"{'Overall Retention':<25} {ret.get('overall_retention', 0):>15.2%}")

    # Save results
    output_dir = project_root / "results"
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"appserver_eval_{timestamp}.json"

    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to: {output_path}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate Codex compaction using app-server protocol",
    )

    parser.add_argument(
        "--codex-path",
        type=str,
        default=DEFAULT_CODEX,
        help=f"Path to Codex binary (default: {DEFAULT_CODEX})"
    )
    parser.add_argument("--token-limit", type=int, default=5000)
    parser.add_argument("--turns", type=int, default=12)
    parser.add_argument("--verbose", "-v", action="store_true", default=True)
    parser.add_argument("--quiet", "-q", action="store_true")

    args = parser.parse_args()

    if not os.path.exists(args.codex_path):
        print(f"ERROR: Codex binary not found at: {args.codex_path}")
        print("\nTo build the Codex binary:")
        print(f"  cd {project_root / 'codex' / 'codex-rs'}")
        print("  cargo build --release")
        return 1

    run_single_eval(
        codex_path=args.codex_path,
        token_limit=args.token_limit,
        num_turns=args.turns,
        verbose=args.verbose and not args.quiet,
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
