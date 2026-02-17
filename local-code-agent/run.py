from agent.core import run_agent
import sys

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = input("Ask me about your codebase: ")

    print(f"Query: {query}")
    answer = run_agent(query)
    print("\n=== Agent Answer ===\n")
    print(answer)
