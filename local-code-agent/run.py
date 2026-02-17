from agent.orchestrator import Orchestrator
import sys

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = input("Ask me about your codebase: ")

    print(f"Query: {query}")

    orchestrator = Orchestrator()
    answer = orchestrator.run(query)

    print("\n=== Agent Answer ===\n")
    print(answer)
