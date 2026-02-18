import argparse
import sys
import os
import config

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Local Code Agent")
    parser.add_argument("query", nargs="*", help="The query to ask the agent")
    parser.add_argument("--root", "-r", help="The root directory of the project to analyze", default=None)

    args = parser.parse_args()

    if args.root:
        # Update project root
        project_root = os.path.abspath(args.root)
        if not os.path.exists(project_root):
            print(f"Error: Project root '{project_root}' does not exist.")
            sys.exit(1)
        config.PROJECT_ROOT = project_root
        print(f"Project root set to: {config.PROJECT_ROOT}")

    if args.query:
        query = " ".join(args.query)
    else:
        query = input("Ask me about your codebase: ")

    print(f"Query: {query}")

    from agent.orchestrator import Orchestrator
    orchestrator = Orchestrator()
    answer = orchestrator.run(query)

    print("\n=== Agent Answer ===\n")
    print(answer)
