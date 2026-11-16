from src.graph.test_case_generator.graph import build_graph

def main():
    # Build the graph
    app = build_graph()

    # Initialize empty state
    init_state = {
        "requirement": "",
        "test_cases": [],
        "errors": []
    }

    # Run Pipeline
    final_state = app.invoke(init_state)

    # Print Results
    print("Pipeline Complete!")
    print(f"Test Cases Generated: {len(final_state['test_cases'])}")
    print(f"Errors: {final_state['errors']}")

if __name__ == "__main__":
    main()