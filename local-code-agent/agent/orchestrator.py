from agent.agents import code_reader, code_writer, tester, debugger, planner
from agent.tools import execute_tool, search_code, read_file, list_directory, get_code_structure, run_command
from agent.execution import execute_agent_loop
from agent.utils import extract_json_from_text
import json
import traceback

class Orchestrator:
    def __init__(self):
        self.state = {
            "context": {},
            "plan": [],
            "results": {}
        }
        # self.conversation_history = []

    def run(self, user_query):
        print(f"Orchestrator: Received query: {user_query}")

        # 1. Generate plan
        plan = self.create_plan(user_query)
        self.state["plan"] = plan
        print(f"Orchestrator: Plan generated: {json.dumps(plan, indent=2)}")

        # 2. Execute steps
        for step in plan:
            agent_name = step.get("agent")
            task = step.get("task")
            step_id = self.get_step_id(step)

            print(f"\nOrchestrator: Executing step {step_id} with agent {agent_name}...")
            print(f"Task: {task}")

            result = self.call_agent(agent_name, task)
            self.state["results"][step_id] = result
            print(f"Orchestrator: Step {step_id} completed.")

        # 3. Synthesize answer
        final_answer = self.synthesize_answer()
        return final_answer

    def get_step_id(self, step):
        # Generate a simple ID if not present
        if "id" in step:
            return str(step["id"])
        # Use index in plan
        try:
            return f"step_{self.state['plan'].index(step) + 1}"
        except:
            return "unknown_step"

    def create_plan(self, query):
        print("Orchestrator: calling Planner...")
        try:
            response = planner(query)
            text = response.text

            plan = extract_json_from_text(text)

            if plan is None:
                # Retry or cleanup
                print(f"Planner output invalid JSON: {text}")
                return [{"agent": self.choose_agent_fallback(query), "task": query}]

            if isinstance(plan, list):
                return plan
            elif isinstance(plan, dict):
                return [plan]
            else:
                print(f"Planner output not a list or dict: {plan}")
                return [{"agent": self.choose_agent_fallback(query), "task": query}]
        except Exception as e:
            print(f"Planner failed: {e}\n{traceback.format_exc()}")
            return [{"agent": self.choose_agent_fallback(query), "task": query}]

    def choose_agent_fallback(self, query):
        q = query.lower()
        if "test" in q: return "tester"
        if any(x in q for x in ["write", "create", "modify", "update", "fix", "add"]): return "writer"
        if "debug" in q or "error" in q or "fail" in q: return "debugger"
        return "reader"

    def call_agent(self, agent_name, task):
        agent_map = {
            "reader": code_reader,
            "code_reader": code_reader,
            "writer": code_writer,
            "code_writer": code_writer,
            "tester": tester,
            "debugger": debugger,
        }

        agent_fn = agent_map.get(agent_name.lower())
        if not agent_fn:
            print(f"Unknown agent: {agent_name}. Defaulting to reader.")
            agent_fn = code_reader

        return self.run_agent_loop(agent_fn, task)

    def run_agent_loop(self, agent_fn, task, max_iterations=10):
        history = []

        context_str = self.get_context_string()
        if context_str:
            task = f"{task}\n\nContext from previous steps:\n{context_str}"

        def get_response_fn(hist):
            return agent_fn(task, hist)

        def tool_executor(name, args):
            if name == "ask_orchestrator":
                return self.handle_orchestrator_request(args)
            else:
                return execute_tool(name, args)

        # Simple logging wrapper to match previous style roughly
        def log_func(msg):
            print(f"  {msg}")

        return execute_agent_loop(
            get_response_fn,
            history,
            tool_executor,
            max_iterations=max_iterations,
            log_func=log_func
        )

    def handle_orchestrator_request(self, args):
        action = args.get("action")
        print(f"  [Orchestrator] Handling request: {action}")

        if action == "search":
            query = args.get("query")
            return search_code(query)
        elif action == "read_file":
            path = args.get("path")
            return read_file(path)
        elif action == "list_dir":
            path = args.get("path")
            return list_directory(path)
        elif action == "get_state":
            return json.dumps(self.state, default=str)
        elif action == "run_test":
             cmd = args.get("command")
             return run_command(cmd)
        else:
            return f"Unknown orchestrator action: {action}"

    def get_context_string(self):
        if not self.state["results"]:
            return ""

        summary = []
        for step_id, result in self.state["results"].items():
            summary.append(f"Result from {step_id}:\n{result}\n")
        return "\n".join(summary)

    def synthesize_answer(self):
        summary = "Mission Completed.\n\n"
        for step_id, result in self.state["results"].items():
            summary += f"=== Step {step_id} ===\n{result}\n\n"
        return summary
