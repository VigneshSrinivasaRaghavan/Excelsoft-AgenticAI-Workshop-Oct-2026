from src.graph.test_case_generator_rag.graph import build_graph

def main():
    # Build the graph
    app = build_graph()

    # Initialize empty state
    init_state = {
        "requirement": "",
        "retrieved_context": "",
        "test_cases": [],
        "errors": [],
        "validation_status": "pending",
        "retry_count": 0,
        "human_approval": "pending",
        "human_feedback": ""
    }

    # Run Pipeline
    final_state = app.invoke(init_state)

    # Print Results
    print("Pipeline Complete!")
    print(f"Test Cases Generated: {len(final_state['test_cases'])}")
    print(f"Errors: {final_state['errors']}")

if __name__ == "__main__":
    main()