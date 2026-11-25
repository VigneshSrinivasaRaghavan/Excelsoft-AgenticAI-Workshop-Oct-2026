"""
Log Analyzer - Node Functions
"""
import json
from datetime import datetime
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from .state import LogAnalyzerState
from src.core import get_langchain_llm, pick_log_file, search_vector_store
from src.prompts.log_analyzer_prompts import LOG_ANALYZER_SYSTEM_PROMPT
from src.core import PersistentMemory

persistent_memory = PersistentMemory(collection_name="log_analyzer_memory")

# Setup
ROOT = Path(__file__).resolve().parents[3]
LOG_DIR = ROOT / "data" / "logs"
OUT_DIR = ROOT / "outputs" / "log_analyzer"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Build Langchain components
llm = get_langchain_llm()
prompt_template = ChatPromptTemplate.from_messages([
    ("system", LOG_ANALYZER_SYSTEM_PROMPT),
    ("user", "Analyze this log:\n\n{log_content}")
])
parser = StrOutputParser()
chain = prompt_template | llm | parser


def read_log(state: LogAnalyzerState) -> LogAnalyzerState:
    if state.get("log_content"):
        if state.get("conversation_history"):
            print(f"Follow-up instruction: {state.get('user_instruction', '')[:60]}...")
        else:
            print("Log file loaded from CLI argument.")
        return {}
    log_file = pick_log_file(None, LOG_DIR)
    log_content = log_file.read_text(encoding="utf-8")
    print(f"Log file loaded: {log_file.name}")
    return {"log_content": log_content}

def retrieve_context(state: LogAnalyzerState) -> LogAnalyzerState:
    """Retrieve relevant troubleshooting guides from knowledge base."""

    log_content = state["log_content"]

    # Extract key error patterns from log (first 500 chars)
    log_preview = log_content[:500]

    print("Retrieving relevant troubleshooting guides...")

    # Search vector store
    results = search_vector_store(
        query=f"troubleshooting guide for: {log_preview}",
        top_k=3
    )

    # Format context
    context_parts = []
    for i, (doc, score) in enumerate(results, 1):
        source = doc.metadata.get('source', 'Unknown').split('/')[-1]
        similarity = 1 - score

        print(f"Retrieved [{i}] {source} (similarity: {similarity:.2f})")

        context_parts.append(f"[Source: {source}]\\n{doc.page_content}\\n")

    retrieved_context = "\\n---\\n".join(context_parts)

    print(f"Retrieved {len(results)} relevant troubleshooting guides")

    return {"retrieved_context": retrieved_context}


def analyze_log(state: LogAnalyzerState) -> LogAnalyzerState:
    """Analyze log using RAG + STM + LTM context."""
    log_content = state["log_content"]
    retrieved_context = state.get("retrieved_context", "")
    past_incidents = state.get("past_incidents", "")
    conversation_history = state.get("conversation_history", [])
    user_instruction = state.get("user_instruction", "")
    existing_analysis = state.get("analysis_text", "")

    # Build conversation context from STM (last 6 messages)
    conversation_text = ""
    if conversation_history:
        lines = [f"{msg['role']}: {msg['content']}" for msg in conversation_history[-6:]]
        conversation_text = "\n".join(lines)

    # Compose prompt
    if conversation_history and existing_analysis and user_instruction:
        # Follow-up mode — refine existing analysis based on instruction
        prompt_content = f"""TROUBLESHOOTING GUIDES (RAG):
{retrieved_context}
"""
        if past_incidents:
            prompt_content += f"""
PAST SIMILAR INCIDENTS (from previous sessions):
{past_incidents}
"""
        prompt_content += f"""
CONVERSATION HISTORY (current session):
{conversation_text}

EXISTING ANALYSIS:
{existing_analysis}

ORIGINAL LOG:
{log_content}

FOLLOW-UP INSTRUCTION: {user_instruction}
Refine or extend the existing analysis above based on the instruction.
Return the complete updated analysis in the same three-part format (text, JSON, executive summary).
"""
    else:
        # First run — fresh analysis
        prompt_content = f"""TROUBLESHOOTING GUIDES (RAG):
{retrieved_context}
"""
        if past_incidents:
            prompt_content += f"""
PAST SIMILAR INCIDENTS (from previous sessions):
{past_incidents}
"""
        prompt_content += f"""
LOG TO ANALYZE:
{log_content}
"""

    try:
        response = chain.invoke({"log_content": prompt_content})
        text_report, json_report, exec_summary = _split_response(response)

        # Update STM — append this turn to conversation history
        updated_history = list(conversation_history)
        turn_label = user_instruction if user_instruction else "Analyze log"
        updated_history.append({"role": "user", "content": turn_label})
        severity = json_report.get("severity", "unknown") if isinstance(json_report, dict) else "unknown"
        error_count = json_report.get("error_count", 0) if isinstance(json_report, dict) else 0
        updated_history.append({
            "role": "agent",
            "content": f"Analysis complete — severity: {severity}, errors: {error_count}"
        })

        return {
            "analysis_text": text_report,
            "analysis_json": json_report,
            "executive_summary": exec_summary,
            "errors": [],
            "conversation_history": updated_history
        }

    except Exception as e:
        return {
            "analysis_text": "",
            "analysis_json": {},
            "executive_summary": "",
            "errors": [f"LLM error: {e}"]
        }


def save_outputs(state: LogAnalyzerState) -> LogAnalyzerState:
    """Save analysis to timestamped files. LTM save happens in driver after user confirms."""
    if state.get("errors"):
        return {}

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save text analysis — timestamped so sessions don't overwrite each other
    text_file = OUT_DIR / f"analysis_report_{timestamp}.txt"
    text_file.write_text(state["analysis_text"], encoding="utf-8")

    # Save JSON report — timestamped
    json_file = OUT_DIR / f"analysis_report_{timestamp}.json"
    json_file.write_text(
        json.dumps(state["analysis_json"], indent=2),
        encoding="utf-8"
    )

    # Save executive summary — timestamped
    exec_file = OUT_DIR / f"executive_summary_{timestamp}.txt"
    exec_file.write_text(state["executive_summary"], encoding="utf-8")

    print(f"Saved analysis reports to {OUT_DIR}")
    return {}

def _split_response(response: str) -> tuple:
    """Split LLM response into 3 parts."""
    text_report = response
    json_report = {}
    exec_summary = "Executive summary not generated."

    # Split by ```json markdown fence
    if "```json" in response:
        parts = response.split("```json")
        text_report = parts[0].strip()
        remainder = parts[1]

        # Extract JSON
        if "```" in remainder:
            json_block = remainder.split("```")[0].strip()
            try:
                json_report = json.loads(json_block)
            except json.JSONDecodeError:
                json_report = {"error": "Failed to parse JSON"}

            # Extract executive summary
            after_json = remainder.split("```", 1)[1]
            if "---EXECUTIVE---" in after_json:
                exec_parts = after_json.split("---EXECUTIVE---")
                exec_summary = exec_parts[1].strip()

    return text_report, json_report, exec_summary

def load_memories(state: LogAnalyzerState) -> LogAnalyzerState:
    log_content = state.get("log_content", "")
    conversation_history = state.get("conversation_history", [])

    print(f"Loaded conversation history: {len(conversation_history)} message(s)")

    # LTM — search using first 300 chars of log as query
    past_incidents = persistent_memory.get_context(
        query=f"log analysis incident: {log_content[:300]}",
        top_k=2
    )

    return {"past_incidents": past_incidents}