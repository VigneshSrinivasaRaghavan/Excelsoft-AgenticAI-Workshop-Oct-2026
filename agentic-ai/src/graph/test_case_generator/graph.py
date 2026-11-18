from langgraph.graph import StateGraph, END
from .state import TestCaseState
from .nodes import read_requirement, generate_tests, save_outputs, validate_tests, retry_generate, route_after_validation, show_preview, human_approval, route_after_human_approval

def build_graph():
    # Create Graph
    workflow = StateGraph(TestCaseState)

    # Add nodes
    workflow.add_node("read", read_requirement)
    workflow.add_node("generate", generate_tests)
    workflow.add_node("save", save_outputs)
    workflow.add_node("validate", validate_tests)
    workflow.add_node("retry", retry_generate)
    workflow.add_node("route", route_after_validation)
    workflow.add_node("preview", show_preview)
    workflow.add_node("human_approval", human_approval)
    workflow.add_node("route_after_human_approval", route_after_human_approval)

    # Connect nodes via edges
    workflow.set_entry_point("read")
    workflow.add_edge("read", "generate")
    workflow.add_edge("generate", "validate")

    # Conditional edges
    workflow.add_conditional_edges(
        "validate",
        route_after_validation,
        {
            "preview": "preview",
            "retry": "retry",
        }
    )

    workflow.add_edge("preview", "human_approval")

    workflow.add_conditional_edges(
        "human_approval",
        route_after_human_approval,
        {
            "save": "save",
            "retry": "retry",
        }
    )

    workflow.add_edge("retry", "validate")


    workflow.add_edge("save", END)

    # Compile graph
    return workflow.compile()